#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file PyEvalSource.py
# data-source types

""" Definitions of PYEVAL datasource """

import sys
import threading
import copy
from xml.dom import minidom

from .Types import NTP
from . import Streams

from .DataHolder import DataHolder
from .DataSources import DataSource
from .Errors import DataSourceSetupError


class Variables(object):
    pass


## Python Eval data source
class PyEvalSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of data
        self.__name = None
        ## the current  static JSON object
        self.__globalJSON = None
        ## the current  dynamic JSON object
        self.__localJSON = None
        ## datasource pool
        self.__pool = None
        ## datasources xml
        self.__sources = {}
        ## datasources
        self.__datasources = {}
        ## python script
        self.__script = ""
        ## common block
        self.__commonblock = False
        ## lock for common block
        self.__lock = None
        ## common block variables
        self.__common = None
        ## data format
        self.__result = {"rank": "SCALAR",
                         "value": None,
                         "tangoDType": "DevString",
                         "shape": [1, 0],
                         "encoding": None,
                         "decoders": None}

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        dom = minidom.parseString(xml)
        mds = dom.getElementsByTagName("datasource")
        inputs = []
        if mds and len(mds) > 0:
            inputs = mds[0].getElementsByTagName("datasource")
        for inp in inputs:
            if inp.hasAttribute("name") and inp.hasAttribute("type"):
                name = inp.getAttribute("name").strip()
                dstype = inp.getAttribute("type").strip()
                if len(name) > 0:
                    if len(name) > 3 and name[:2] == 'ds.':
                        name = name[3:]
                    self.__sources[name] = (dstype, inp.toxml())
                else:
                    if Streams.log_error:
                        print >> Streams.log_error, \
                            "PyEvalSource::setup() - "\
                            "PyEval input %s not defined" % name
                    raise DataSourceSetupError(
                        "PyEvalSource::setup() - "
                        "PyEval input %s not defined" % name)

            else:
                if Streams.log_error:
                    print >> Streams.log_error, \
                        "PyEvalSource::setup() - "\
                        "PyEval input name wrongly defined"
                raise DataSourceSetupError(
                    "PyEvalSource::setup() - "
                    "PyEval input name wrongly defined")
        res = dom.getElementsByTagName("result")
        if res and len(res) > 0:
            self.__name = res[0].getAttribute("name") \
                if res[0].hasAttribute("name") else 'result'
            if len(self.__name) > 3 and self.__name[:2] == 'ds.':
                self.__name = self.__name[3:]
            self.__script = self._getText(res[0])

        if len(self.__script) == 0:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "PyEvalSource::setup() - "\
                    "PyEval script %s not defined" % self.__name
            raise DataSourceSetupError(
                "PyEvalSource::setup() - "
                "PyEval script %s not defined" % self.__name)

        if "commonblock" in self.__script:
            self.__commonblock = True
        else:
            self.__commonblock = False

    ## self-description
    # \returns self-describing string
    def __str__(self):
        return " PYEVAL %s" % (self.__script)

    ## sets JSON string
    # \brief It sets the currently used  JSON string
    # \param globalJSON static JSON string
    # \param localJSON dynamic JSON string
    def setJSON(self, globalJSON, localJSON=None):
        self.__globalJSON = globalJSON
        self.__localJSON = localJSON
        for source in self.__datasources.values():
            if hasattr(source, "setJSON"):
                source.setJSON(self.__globalJSON,
                               self.__localJSON)

    ## provides access to the data
    # \returns  dictionary with collected data
    def getData(self):
        if not self.__name:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "PyEvalSource::getData() - PyEval datasource not set up"
            raise DataSourceSetupError(
                "PyEvalSource::getData() - PyEval datasource not set up")

        ds = Variables()
        for name, source in self.__datasources.items():
            dt = source.getData()
            value = None
            if dt:
                dh = DataHolder(**dt)
                if dh and hasattr(dh, "value"):
                    value = dh.value
            setattr(ds, name, value)

        setattr(ds, self.__name, None)

        if not self.__commonblock:
            exec(self.__script.strip(), {}, {"ds": ds})
            rec = getattr(ds, self.__name)
        else:
            rec = None
            with self.__lock:
                exec(self.__script.strip(), {}, {
                        "ds": ds, "commonblock": self.__common})
                rec = copy.deepcopy(getattr(ds, self.__name))
        ntp = NTP()
        rank, shape, pythonDType = ntp.arrayRankShape(rec)
        if rank in NTP.rTf:
            if shape is None:
                shape = [1, 0]

            return {"rank": NTP.rTf[rank],
                    "value": rec,
                    "tangoDType": NTP.pTt[pythonDType.__name__],
                    "shape": shape}

    ## sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.__result["decoders"] = decoders
        for source in self.__datasources.values():
            if hasattr(source, "setDecoders"):
                source.setDecoders(decoders)

    ## sets the datasources
    # \param pool datasource pool
    def setDataSources(self, pool):
        self.__pool = pool
        pool.lock.acquire()
        try:
            if 'PYEVAL' not in self.__pool.common.keys():
                self.__pool.common['PYEVAL'] = {}
            if "lock" not in self.__pool.common['PYEVAL'].keys():
                self.__pool.common['PYEVAL']["lock"] = threading.Lock()
            self.__lock = self.__pool.common['PYEVAL']["lock"]
            if "common" not in self.__pool.common['PYEVAL'].keys():
                self.__pool.common['PYEVAL']["common"] = {}
            self.__common = self.__pool.common['PYEVAL']["common"]

        finally:
            pool.lock.release()

        for name, inp in self.__sources.items():
            if pool and pool.hasDataSource(inp[0]):
                self.__datasources[name] = pool.get(inp[0])()
                self.__datasources[name].setup(inp[1])
                if hasattr(self.__datasources[name], "setJSON") \
                        and self.__globalJSON:
                    self.__datasources[name].setJSON(self.__globalJSON)
                if hasattr(self.__datasources[name], "setDataSources"):
                    self.__datasources[name].setDataSources(pool)

            else:
                if Streams.log_error:
                    print >> Streams.log_error, \
                        "PyEvalSource::setDataSources - Unknown data source"
                else:
                    print >> sys.stderr, \
                        "PyEvalSource::setDataSources - Unknown data source"

                self.__datasources[name] = DataSource()
