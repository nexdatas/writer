#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
#
#    nexdatas is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    nexdatas is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
## \package nxswriter nexdatas
## \file TangoSource.py
# data-source types

""" Definitions of TANGO datasource """

import time
import threading
from xml.dom import minidom

from . import Streams
from .Types import NTP

from .DataSources import DataSource
from .Errors import (PackageError, DataSourceSetupError)


try:
    import PyTango
    ## global variable if PyTango module installed
    PYTANGO_AVAILABLE = True
except ImportError as e:
    PYTANGO_AVAILABLE = False
    Streams.info("PYTANGO not available: %s" % e)


## tools for proxy
class ProxyTools(object):

    ## sets the Tango proxy up
    ## \param cls ProxyTools class
    ## \param device tango device
    # \returns proxy if proxy is set up
    @classmethod
    def proxySetup(cls, device):
        found = False
        cnt = 0

        try:
            proxy = PyTango.DeviceProxy(device)

        except:
            Streams.error(
                "ProxyTools.proxySetup() - "
                "Cannot connect to %s " % device,
                std=False)
            raise

        while not found and cnt < 1000:
            if cnt > 1:
                time.sleep(0.01)
            try:
                proxy.ping()
                found = True
            except:
                time.sleep(0.01)
                found = False
            cnt += 1
        if found:
            return proxy

    ## checks if proxy is valid
    ## \param cls ProxyTools class
    # \param proxy PyTango proxy
    # \returns True if proxy is valid else false
    @classmethod
    def isProxyValid(cls, proxy):
        failed = True
        try:
            proxy.ping()
            failed = False
        except:
            failed = True
        return not failed


## Tango data source
class TangoSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## Tango device member
        self.member = TgMember(None)
        ## datasource tango group
        self.group = None
        ## full device name
        self.device = None

        ## global tango group for TANGO datasources
        self.__tngrp = None
        ## datasource pool
        self.__pool = None
        ## device proxy
        self.__proxy = None

        ## the current  static JSON object
        self.__globalJSON = None
        ## the current  dynamic JSON object
        self.__localJSON = None

        ## decoder pool
        self.__decoders = None
        ## client datasource for mixed CLIENT/TANGO mode
        self.client = None

    ## self-description
    # \returns self-describing string
    def __str__(self):
        return " TANGO Device %s : %s (%s)" % (
            self.device, self.member.name, self.member.memberType)

    ## sets JSON string
    # \brief It sets the currently used  JSON string
    # \param globalJSON static JSON string
    # \param localJSON dynamic JSON string
    def setJSON(self, globalJSON, localJSON=None):
        self.__globalJSON = globalJSON
        self.__localJSON = localJSON

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        dom = minidom.parseString(xml)
        rec = dom.getElementsByTagName("record")
        name = None
        if rec and len(rec) > 0:
            name = rec[0].getAttribute("name") \
                if rec[0].hasAttribute("name") else None
        if not name:
            Streams.error(
                "TangoSource::setup() - "
                "Tango record name not defined: %s" % xml,
                std=False)

            raise DataSourceSetupError(
                "Tango record name not defined: %s" % xml)
        dv = dom.getElementsByTagName("device")
        device = None
        client = False
        if dv and len(dv) > 0:
            device = dv[0].getAttribute("name") \
                if dv[0].hasAttribute("name") else None
            hostname = dv[0].getAttribute("hostname") \
                if dv[0].hasAttribute("hostname") else None
            port = dv[0].getAttribute("port") \
                if dv[0].hasAttribute("port") else None
            group = dv[0].getAttribute("group") \
                if dv[0].hasAttribute("group") else None
            encoding = dv[0].getAttribute("encoding") \
                if dv[0].hasAttribute("encoding") else None
            memberType = dv[0].getAttribute("member") \
                if dv[0].hasAttribute("member") else None
            if not memberType or memberType not in [
                    "attribute", "command", "property"]:
                memberType = "attribute"
            if group != '__CLIENT__':
                self.group = group
            else:
                client = True
            self.member = TgMember(name, memberType, encoding)
        if not device:
            Streams.error(
                "TangoSource::setup() - "
                "Tango device name not defined: %s" % xml,
                std=False)

            raise DataSourceSetupError(
                "Tango device name not defined: %s" % xml)

        if hostname and port and device:
            self.device = "%s:%s/%s" % (hostname.encode(),
                                        port.encode(), device.encode())
        elif device:
            self.device = "%s" % (device.encode())

        self.__proxy = ProxyTools.proxySetup(self.device)

        if not self.__proxy:
            Streams.error(
                "TangoSource::setup() - "
                "Cannot connect to: %s \ndefined by %s"
                % (self.device, xml), std=False)

            raise DataSourceSetupError(
                "Cannot connect to: %s \ndefined by %s" % (self.device, xml))
        elif hostname and port and device and client:
            try:
                host = self.__proxy.get_db_host().split(".")[0]
            except:
                host = hostname.encode().split(".")[0]
            self.client = "%s:%s/%s/%s" % (
                host, port.encode(),
                device.encode(), name.lower()
            )

    ## sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.__decoders = decoders

    ## data provider
    # \returns dictionary with collected data
    def getData(self):
        if self.client:
            res = None
            try:
                res = self._getJSONData(
                    "tango://%s" % self.client,
                    self.__globalJSON, self.__localJSON)
            except:
                res = None
            if not res:
                try:
                    res = self._getJSONData(
                        self.client,
                        self.__globalJSON, self.__localJSON)
                except:
                    res = None
            if res:
                return res
        if not PYTANGO_AVAILABLE:
            Streams.error(
                "TangoSource::getData() - "
                "Support for PyTango datasources not available",
                std=False)

            raise PackageError(
                "Support for PyTango datasources not available")

        if self.device and self.member.memberType and self.member.name:
            if not self.__proxy or not ProxyTools.isProxyValid(self.__proxy):
                self.__proxy = ProxyTools.proxySetup(self.device)
                if not self.__proxy:
                    Streams.error(
                        "TangoSource::getData() - "
                        "Setting up lasts to long: %s" % self.device,
                        std=False)

                    raise DataSourceSetupError(
                        "Setting up lasts to long: %s" % self.device)

            if self.group is None:
                self.member.getData(self.__proxy)
            else:
                if not hasattr(self.__tngrp, "getData"):
                    Streams.error(
                        "TangoSource::getData() - "
                        "DataSource pool not set up",
                        std=False)

                    raise DataSourceSetupError("DataSource pool not set up")

                self.__tngrp.getData(
                    self.__pool.counter, self.__proxy, self.member)

            if hasattr(self.__tngrp, "lock"):
                self.__tngrp.lock.acquire()
            try:
                val = self.member.getValue(self.__decoders)
            finally:
                if hasattr(self.__tngrp, "lock"):
                    self.__tngrp.lock.release()
            return val

    ## sets the datasources
    # \param pool datasource pool
    def setDataSources(self, pool):
        self.__pool = pool
        pool.lock.acquire()
        try:
            if 'TANGO' not in self.__pool.common.keys():
                self.__pool.common['TANGO'] = {}
            if self.group:
                if self.group not in self.__pool.common['TANGO'].keys():
                    self.__pool.common['TANGO'][self.group] = TgGroup()
                self.__tngrp = self.__pool.common['TANGO'][self.group]

                self.__tngrp.lock.acquire()
                tdv = self.__tngrp.getDevice(self.device)
                tdv.proxy = self.__proxy
                self.member = tdv.setMember(self.member)
        finally:
            if self.group:
                self.__tngrp.lock.release()
            pool.lock.release()


## Group of tango devices
class TgGroup(object):
    ## default constructor
    # \param counter of steps
    def __init__(self, counter=0):
        ## threading lock
        self.lock = threading.Lock()
        ## counter of steps
        self.counter = counter
        ## TANGO devices
        self.devices = {}

    ## provides tango device
    # \param device tango device name
    # \returns TgDevice instance of tango device
    def getDevice(self, device):
        if device not in self.devices:
            self.devices[device] = TgDevice(device)
        return self.devices[device]

    ## fetches attribute data for given device
    # \param device given device
    @classmethod
    def __fetchAttributes(cls, device):
        attr = device.attributes
        alist = device.proxy.get_attribute_list()
        alist = [a.lower() for a in alist]

        errors = []
        for a in attr:
            if a.encode().lower() not in alist:
                errors.append((a, device.device))
        if errors:
            Streams.error(
                "TgGroup::getData() - "
                "attribute not in tango "
                "device attributes:%s" % errors,
                std=False)

            raise DataSourceSetupError(
                "TgGroup::getData() - "
                "attribute not in tango "
                "device attributes:%s" % errors)

        res = device.proxy.read_attributes(attr)
        for i in range(len(attr)):
            mb = device.members[attr[i]]
            mb.setData(res[i])

    ## fetches attribute data for given proxy
    # \param proxy given proxy
    # \param member given member
    @classmethod
    def __fetchAttribute(cls, proxy, member):
        alist = proxy.get_attribute_list()
        alist = [a.lower() for a in alist]
        if member.name.lower() in alist:
            da = proxy.read_attribute(member.name.encode())
            member.setData(da)

    ## fetches property data for given member
    # \param proxy given proxy
    # \param member given member
    @classmethod
    def __fetchProperty(cls, proxy, member):
        plist = proxy.get_property_list('*')
        plist = [a.lower() for a in plist]
        if member.name.encode().lower() in plist:
            da = proxy.get_property(
                member.name.encode())[member.name.encode()]
            member.setData(da)

    ## fetches command data for given member
    # \param proxy given proxy
    # \param member given member
    @classmethod
    def __fetchCommand(cls, proxy, member):
        clist = [cm.cmd_name
                 for cm in proxy.command_list_query()]
        clist = [a.lower() for a in clist]
        if member.name.encode().lower() in clist:
            cd = proxy.command_query(member.name.encode())
            da = proxy.command_inout(member.name.encode())
            member.setData(da, cd)

    ## reads data from device proxy
    # \param counter counter of scan steps
    # \param proxy device proxy
    # \param member required member
    def getData(self, counter, proxy=None, member=None):

        with self.lock:
            if counter == self.counter:
                if proxy and member and not member.isDataSet():
                    if member.memberType == "attribute":
                        self.__fetchAttribute(proxy, member)
                    elif member.memberType == "command":
                        self.__fetchCommand(proxy, member)
                    elif member.memberType == "property":
                        self.__fetchProperty(proxy, member)
                return

            self.counter = counter

            for dv in self.devices.values():
                for mb in dv.members.values():
                    mb.reset()

                if not dv.proxy or not ProxyTools.isProxyValid(dv.proxy):
                    dv.proxy = ProxyTools.proxySetup(dv.device)
                    if not dv.proxy:
                        Streams.error(
                            "TgGroup::getData() - "
                            "Setting up lasts to long: %s" % dv.device,
                            std=False)

                        raise DataSourceSetupError(
                            "TgGroup::getData() - "
                            "Setting up lasts to long: %s" % dv.device)

                if dv.attributes:
                    self.__fetchAttributes(dv)

                for mb in dv.members.values():
                    if mb.memberType == "property":
                        self.__fetchProperty(dv.proxy, mb)
                    elif mb.memberType == "command":
                        self.__fetchCommand(dv.proxy, mb)


## tango device
class TgDevice(object):
    ## default constructor
    # \param device tango device name
    # \param proxy device proxy
    def __init__(self, device, proxy=None):
        ## tango device name
        self.device = device
        ## dictionary with tango members
        self.members = {}
        ## device attribute names
        self.attributes = []
        ## device property names
        self.properties = []
        ## device command names
        self.commands = []
        ## device proxy
        self.proxy = proxy

    ## provides tango device member
    # \param member tango  device member
    # \returns TgMember instance of tango device member
    def setMember(self, member):
        if member.name not in self.members:
            self.members[member.name] = member
            self.__setFlag(member)
        return self.members[member.name]

    ## sets corresponding flag related to member type
    # \param member given tango device member
    def __setFlag(self, member):
        if member.memberType == 'attribute':
            self.attributes.append(member.name.encode())
        elif member.memberType == 'property':
            self.properties.append(member.name.encode())
        elif member.memberType == 'command':
            self.commands.append(member.name.encode())


## tango device member
class TgMember(object):
    ## default constructor
    def __init__(self, name, memberType='attribute', encoding=None):
        ## name of data record
        self.name = name
        ## member type of the data, i.e. attribute, property,...
        self.memberType = memberType
        ## encoding of Tango DevEncoded variables
        self.encoding = encoding
        ## data value
        self.__value = None
        ## output data
        self.__da = None
        ## input command data
        self.__cd = None

    ## cleans output value
    def reset(self):
        self.__value = None
        self.__da = None
        self.__cd = None

    ## sets tango data
    # \param data output tango data
    # \param cmd input command data
    def setData(self, data, cmd=None):
        self.__da = data
        self.__cd = cmd

    ## checks if data is set
    # \returns True if data is set
    def isDataSet(self):
        status = True if self.__da else False
        if self.memberType == 'command':
            status = status and (True if self.__cd else False)
        return status

    ## provides value of tango member
    # \returns dictionary with {"rank":, "value":, "tangoDType":,
    #          "shape":, "encoding":, "decoders":}
    # \param decoders decoder pool
    def getValue(self, decoders=None):
        if self.__value:
            return self.__value
        if self.__da is None:
            Streams.error(
                "TgMember::getValue() - "
                "Data for %s not fetched" % self.name,
                std=False)

            raise DataSourceSetupError(
                "TgMember::getValue() -  "
                "Data of %s not fetched" % self.name)

        if self.memberType == "attribute":
            self.__value = {
                "rank": str(self.__da.data_format).split('.')[-1],
                "value": self.__da.value,
                "tangoDType": str(self.__da.type).split('.')[-1],
                "shape": ([self.__da.dim_y, self.__da.dim_x]
                          if self.__da.dim_y
                          else [self.__da.dim_x, 0]),
                "encoding": self.encoding, "decoders": decoders}
        elif self.memberType == "property":

            ntp = NTP()
            rank, shape, pythonDType = ntp.arrayRankShape(self.__da)

            if rank in NTP.rTf:
                if not shape or shape == [1] or shape == [1, 0]:
                    shape = [1, 0]
                    rank = 0
                    value = self.__da[0]
                else:
                    value = self.__da
                self.__value = {
                    "rank": NTP.rTf[rank], "value": value,
                    "tangoDType": NTP.pTt[pythonDType.__name__],
                    "shape": shape}
        elif self.memberType == "command":
            if self.__cd is None:
                Streams.error(
                    "TgMember::getValue() - "
                    "Data for %s not fetched" % self.name,
                    std=False)

                raise DataSourceSetupError(
                    "TgMember::getValue() -  "
                    "Data or %s not fetched" % self.name)
            self.__value = {
                "rank": "SCALAR",
                "value": self.__da,
                "tangoDType": str(self.__cd.out_type).split('.')[-1],
                "shape": [1, 0],
                "encoding": self.encoding,
                "decoders": decoders}
        return self.__value

    ## reads data from device proxy
    # \param proxy device proxy
    def getData(self, proxy):
        self.reset()
        if self.memberType == "attribute":
            alist = proxy.get_attribute_list()
            alist = [a.lower() for a in alist]
            if self.name.encode().lower() in alist:
                self.__da = proxy.read_attribute(self.name.encode())
        elif self.memberType == "property":
            plist = proxy.get_property_list('*')
            plist = [a.lower() for a in plist]
            if self.name.encode().lower() in plist:
                self.__da = proxy.get_property(
                    self.name.encode())[self.name.encode()]
        elif self.memberType == "command":
            clist = [cm.cmd_name for cm in proxy.command_list_query()]
            clist = [a.lower() for a in clist]
            if self.name.encode().lower() in clist:
                self.__cd = proxy.command_query(self.name.encode())
                self.__da = proxy.command_inout(self.name.encode())
