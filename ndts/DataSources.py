#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package ndts nexdatas
## \file DataSources.py
# data-source types

import time
import json
import sys
from xml.dom import minidom
from Types import NTP
import Streams
import threading


try:
    import PyTango
    ## global variable if PyTango module installed
    PYTANGO_AVAILABLE = True
except ImportError, e:
    PYTANGO_AVAILABLE = False
    print >> sys.stdout, "PYTANGO not available: %s" % e
    if Streams.log_info:
        print >> Streams.log_info, "PYTANGO not available: %s" % e


## list of available databases
DB_AVAILABLE = []

try:
    import MySQLdb
    DB_AVAILABLE.append("MYSQL")
except ImportError, e:
    print >> sys.stdout, "MYSQL not available: %s" % e
    if Streams.log_info:
        print >> Streams.log_info, "MYSQL not available: %s" % e
    
try:
    import psycopg2
    DB_AVAILABLE.append("PGSQL")
except ImportError, e:
    print >> sys.stdout, "PGSQL not available: %s" % e
    if Streams.log_info:
        print >> Streams.log_info,  "PGSQL not available: %s" % e

try:
    import cx_Oracle
    DB_AVAILABLE.append("ORACLE")
except ImportError, e:
    print >> sys.stdout, "ORACLE not available: %s" % e
    if Streams.log_info:
        print >> Streams.log_info, "ORACLE not available: %s" % e
        


from DataHolder import DataHolder

from Errors import (PackageError, DataSourceSetupError)





## Data source
class DataSource(object):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        pass


    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        pass


    ## access to data
    # \brief It is an abstract method providing data   
    def getData(self):
        pass


    ## checks if the data is valid
    # \returns if the data is valid
    def isValid(self):
        return True



    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return "unknown DataSource"


    ## provides xml content of the node
    # \param node DOM node
    # \returns xml content string
    def _getText(self, node):
        xml = node.toxml() 
        start = xml.find('>')
        end = xml.rfind('<')
        if start == -1 or end < start:
            return ""
        return xml[start + 1:end].replace("&lt;","<").replace("&gt;",">").replace("&amp;","&")


## tools for proxy
class ProxyTools(object):


    ## sets the Tango proxy up
    ## \param device tango device    
    # \returns proxy if proxy is set up    
    @classmethod
    def proxySetup(cls, device):    
        found = False
        cnt = 0

        try:
            proxy = PyTango.DeviceProxy(device)

        except:
            if Streams.log_error:
                print >> Streams.log_error, "ProxyTools.proxySetup() - Cannot connect to %s " % device
            raise

        while not found and cnt < 1000:
            if cnt > 1:
                time.sleep(0.01)
            try:
                if proxy.state() != PyTango.DevState.RUNNING:
                    found = True
                found = True
            except:    
                time.sleep(0.01)
                found = False
            cnt +=1
        if found:
            return proxy    


    ## checks if proxy is valid
    # \param proxy PyTango proxy
    # \returns True if proxy is valid else false
    @classmethod
    def isProxyValid(cls, proxy):
        failed = True
        try:
            if proxy:
                proxy.state()
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
        self.dv = None

        ## global tango group for TANGO datasources
        self.__tngrp = None
        ## datasource pool
        self.__pool = None
        ## device proxy
        self.__proxy = None

        ## decoder pool
        self.__decoders = None



    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " TANGO Device %s : %s (%s)" % (self.dv, self.member.name, self.member.memberType )


    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "TG XML" , xml 
        dom = minidom.parseString(xml)
        rec = dom.getElementsByTagName("record")
        name = None
        if rec and len(rec)> 0:
            name = rec[0].getAttribute("name") if rec[0].hasAttribute("name") else None
        if not name:
            if Streams.log_error:
                print >> Streams.log_error,  "TangoSource::setup() - Tango record name not defined: %s" % xml

            raise  DataSourceSetupError, \
                "Tango record name not defined: %s" % xml
        dv = dom.getElementsByTagName("device")
        device = None
        if dv and len(dv)> 0:
            device = dv[0].getAttribute("name") if dv[0].hasAttribute("name") else None
            hostname = dv[0].getAttribute("hostname") if dv[0].hasAttribute("hostname") else None
            port = dv[0].getAttribute("port") if dv[0].hasAttribute("port") else None
            self.group = dv[0].getAttribute("group") if dv[0].hasAttribute("group") else None
            encoding = dv[0].getAttribute("encoding") if dv[0].hasAttribute("encoding") else None
            memberType = dv[0].getAttribute("member") if dv[0].hasAttribute("member") else None
            if not memberType or memberType not in ["attribute", "command", "property"]:
                memberType = "attribute" 
            self.member = TgMember(name, memberType, encoding)
        if not device :
            if Streams.log_error:
                print >> Streams.log_error,  "TangoSource::setup() - Tango device name not defined: %s" % xml
            raise  DataSourceSetupError, \
                "Tango device name not defined: %s" % xml

        if hostname and port:
            self.dv = "%s:%s/%s" % (hostname.encode(), port.encode(),device.encode())
        elif device:
            self.dv = "%s" % (device.encode())
            
        self.__proxy = ProxyTools.proxySetup(self.dv)    

        if not self.__proxy:
            if Streams.log_error:
                print >> Streams.log_error,  "TangoSource::setup() - Cannot connect to: %s \ndefined by %s" \
                    % (self.dv, xml)
            raise  DataSourceSetupError, \
                "Cannot connect to: %s \ndefined by %s" % (self.dv, xml)




    ## sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.__decoders = decoders


    ## data provider
    # \returns dictionary with collected data  
    def getData(self):
        if not PYTANGO_AVAILABLE:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "TangoSource::getData() - Support for PyTango datasources not available" 
            raise PackageError, "Support for PyTango datasources not available" 

        if self.dv and self.member.memberType and self.member.name:
            if not self.__proxy or not ProxyTools.isProxyValid(self.__proxy):
                self.__proxy = ProxyTools.proxySetup(self.dv)    
                if not self.__proxy:
                    if Streams.log_error:
                        print >> Streams.log_error,  "TangoSource::getData() - Setting up lasts to long: %s" % xml
                    raise  DataSourceSetupError, \
                        "Setting up lasts to long: %s" % xml
                
            if self.group is None:
                self.member.getData(self.__proxy)
            else:
                if not hasattr(self.__tngrp, "getData"): 
                    if Streams.log_error:
                        print >> Streams.log_error, \
                            "TangoSource::getData() - DataSource pool not set up" 
                    raise DataSourceSetupError, "DataSource pool not set up" 

                self.__tngrp.getData(self.__pool.counter)

            if hasattr(self.__tngrp, "lock"):
                self.__tngrp.lock.acquire()
            try:
                val = self.member.getValue(self.__decoders)
            finally:
                if hasattr(self.__tngrp,"lock"):
                    self.__tngrp.lock.release()
            return  val

                    
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
                tdv = self.__tngrp.getDevice(self.dv)
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
    def __init__(self, counter = 0):
        self.lock = threading.Lock()
        self.counter = counter
        self.devices = {}

    ## provides tango device
    # \param device tango device name    
    # \returns TgDevice instance of tango device
    def getDevice(self, device):
        if device not in self.devices:
            self.devices[device] = TgDevice(device)
        return self.devices[device]    



    ## reads data from device proxy
    # \param counter counter of scan steps
    # \param proxy device proxy
    def getData(self, counter):
        if counter == self.counter:
            return
        try:
            self.lock.acquire()

            self.counter = counter
            errors = []


            for dv in self.devices.values():
                for mb in dv.members.values():
                    mb.reset()

                if not dv.proxy or not ProxyTools.isProxyValid(dv.proxy):
                    dv.proxy = ProxyTools.proxySetup(dv.device)    
                    if not dv.proxy:
                        if Streams.log_error:
                            print >> Streams.log_error,  "TgGroup::getData() - Setting up lasts to long: %s" % dv.device
                        raise DataSourceSetupError, \
                            "TgGroup::getData() - Setting up lasts to long: %s" % dv.device

                if dv.attributes:
                    attr = dv.attributes
                    alist = dv.proxy.get_attribute_list()
                
                    for a in attr:
                        if a.encode() not in alist:
                            errors.append((a, dv.device))
                    if errors:                
                        if Streams.log_error:
                            print >> Streams.log_error, "TgGroup::getData() - attribute not in tango device attributes:%s" % errors
                        raise DataSourceSetupError, ("TgGroup::getData() - attribute not in tango device attributes:%s" % errors )

                    res = dv.proxy.read_attributes(attr)
                    for i in range(len(attr)):
                        mb = dv.members[attr[i]]
                        mb.setData(res[i])
                

                for mb in dv.members.values():
                    if mb.memberType == "property":
                        #                print "getting the property: ", self.name
                        plist = dv.proxy.get_property_list('*')
                        if mb.name.encode() in plist:
                            da = dv.proxy.get_property(mb.name.encode())[mb.name.encode()]
                            mb.setData(da)
                    elif mb.memberType == "command":
                        #                print "calling the command: ", self.name
                        clist = [cm.cmd_name for cm in dv.proxy.command_list_query()]
                        if mb.name in clist:
                            cd = dv.proxy.command_query(mb.name.encode())
                            da = dv.proxy.command_inout(mb.name.encode())
                            mb.setData(da, cd)
    
        finally:
            self.lock.release()

## tango device
class TgDevice(object):
    ## default constructor
    # \param device tango device name
    def __init__(self, device, proxy = None):
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
    def __init__(self, name, memberType='attribute', encoding = None):
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
    # \param da output tango data
    # \param input command data
    def setData(self, da, cd=None):
        self.__da = da
        self.__cd = cd
    

    ## provides value of tango member    
    # \returns dictionary with {"format":, "value":, "tangoDType":,  "shape":, "encoding":, "decoders":}
    # \param decoders decoder pool
    def getValue(self, decoders = None):
        if self.__value:
            return self.__value
        if self.__da is None:
            if Streams.log_error:
                print >> Streams.log_error, "TgMember::getValue() - Data for %s not fetched" % self.name
            raise DataSourceSetupError, ("TgMember::getValue() -  Data or %s not fetched" % self.name)
            
        if self.memberType == "attribute":
            self.__value = {"format":str(self.__da.data_format).split('.')[-1], 
                          "value":self.__da.value, "tangoDType":str(self.__da.type).split('.')[-1], 
                          "shape":([self.__da.dim_y,self.__da.dim_x] \
                                       if self.__da.dim_y else [self.__da.dim_x, 0]),
                          "encoding": self.encoding, "decoders": decoders}
        elif self.memberType == "property":

            ntp = NTP()
            rank, shape, pythonDType = ntp.arrayRankRShape(self.__da)

            if rank in NTP.rTf:
                shape.reverse()
                if not shape or shape == [1] or shape == [1,0]:
                    shape = [1,0]
                    rank = 0
                    value = self.__da[0]
                else:
                    value = self.__da
                self.__value = {"format":NTP.rTf[rank], "value":value, 
                                "tangoDType":NTP.pTt[pythonDType.__name__], "shape":shape}
#            self.__value = {"format":"SCALAR", "value":str(self.__da), "tangoDType":"DevString", "shape":[1,0]}
        elif self.memberType == "command":
            if self.__cd is None:
                if Streams.log_error:
                    print >> Streams.log_error, "TgMember::getValue() - Data for %s not fetched" % self.name
                raise DataSourceSetupError, ("TgMember::getValue() -  Data or %s not fetched" % self.name)
            self.__value = {"format":"SCALAR", "value":self.__da, 
                          "tangoDType":str(self.__cd.out_type).split('.')[-1],  "shape":[1,0], 
                          "encoding":self.encoding, "decoders":decoders}
        return self.__value
        
    ## reads data from device proxy
    # \param proxy device proxy
    def getData(self, proxy):
        self.reset()
        
        if self.memberType == "attribute":
            #            print "getting the attribute: ", self.name
            alist = proxy.get_attribute_list()
            if self.name.encode() in alist:
                self.__da = proxy.read_attribute( self.name.encode())
        elif self.memberType == "property":
            #                print "getting the property: ", self.name
            plist = proxy.get_property_list('*')
            if self.name.encode() in plist:
                self.__da = proxy.get_property(self.name.encode())[self.name.encode()]
        elif self.memberType == "command":
            #                print "calling the command: ", self.name
            clist = [cm.cmd_name for cm in proxy.command_list_query()]
            if self.name in clist:
                self.__cd = proxy.command_query(self.name.encode())
                self.__da = proxy.command_inout(self.name.encode())
                

## DataBase data source
class DBaseSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of the host with the data source
        self.hostname = None
        ## port related to the host
        self.port = None
        ## database query
        self.query = None
        ## DSN string
        self.dsn = None
        ## database type, i.e. MYSQL, PGSQL, ORACLE
        self.dbtype = None
        ## oracle database mode
        self.mode = None
        ## database name
        self.dbname = None
        ## database user
        self.user = None
        ## database password
        self.passwd = None
        ## mysql database configuration file
        self.mycnf = '/etc/my.cnf'
        ## record format, i.e. SCALAR, SPECTRUM, IMAGE
        self.format = None


        
        ## map 
        self.__dbConnect = {"MYSQL":self.__connectMYSQL, 
                          "PGSQL":self.__connectPGSQL,
                          "ORACLE":self.__connectORACLE}

    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " %s DB %s with %s " % (self.dbtype, self.dbname if self.dbname else "" , self.query )

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "DB XML" , xml
        dom = minidom.parseString(xml)
        query = dom.getElementsByTagName("query")
        if query and len(query)> 0:
            self.format = query[0].getAttribute("format") if query[0].hasAttribute("format") else None
#            print "format:", self.format
            self.query = self._getText(query[0])
            
        if not self.format or not self.query:
            if Streams.log_error:
                print >> Streams.log_error,  "DBaseSource::setup() - Database query or its format not defined: %s" % xml
            raise  DataSourceSetupError, \
                "Database query or its format not defined: %s" % xml

        db = dom.getElementsByTagName("database")
        if db and len(db)> 0:
            self.dbname = db[0].getAttribute("dbname") if db[0].hasAttribute("dbname") else None
            self.dbtype = db[0].getAttribute("dbtype") if db[0].hasAttribute("dbtype") else None
            self.user = db[0].getAttribute("user")  if db[0].hasAttribute("user") else None
            self.passwd = db[0].getAttribute("passwd") if db[0].hasAttribute("passwd") else None
            self.mode = db[0].getAttribute("mode") if db[0].hasAttribute("mode") else None
            mycnf = db[0].getAttribute("mycnf") if db[0].hasAttribute("mycnf") else None
            if mycnf:
                self.mycnf = mycnf
            self.hostname = db[0].getAttribute("hostname") if db[0].hasAttribute("hostname") else None
            self.port = db[0].getAttribute("port") if db[0].hasAttribute("port") else None
            self.dsn = self._getText(db[0])
            
#            print "DATABASE:", self.dbname, self.dbtype, self.user,self.passwd , self.hostname, self.port, self.mode, self.mycnf,self.dsn




    ## connects to MYSQL database    
    # \returns open database object
    def __connectMYSQL(self):
        args = {}
        if self.mycnf:
            args["read_default_file"] = self.mycnf.encode()
        if self.dbname:
            args["db"] = self.dbname.encode()
        if self.user:
            args["user"] = self.user.encode()
        if self.passwd:
            args["passwd"] = self.passwd.encode()
        if self.hostname:
            args["host"] = self.hostname.encode()
        if self.port:
            args["port"] = int(self.port)
        return MySQLdb.connect(**args)

    ## connects to PGSQL database    
    # \returns open database object
    def __connectPGSQL(self):
        args = {}

        if self.dbname:
            args["database"] = self.dbname.encode()
        if self.user:
            args["user"] = self.user.encode()
        if self.passwd:
            args["password"] = self.passwd.encode()
        if self.hostname:
            args["host"] = self.hostname.encode()
        if self.port:
            args["port"] = int(self.port)
            
        return psycopg2.connect(**args)

    ## connects to ORACLE database    
    # \returns open database object
    def __connectORACLE(self):
        args = {}
        if self.user:
            args["user"] = self.user.encode()
        if self.passwd:
            args["password"] = self.passwd.encode()
        if self.dsn:
            args["dsn"] = self.dsn.encode()
        if self.mode:
            args["mode"] = self.mode.encode()
            
        return cx_Oracle.connect(**args)

    ## provides access to the data    
    # \returns  dictionary with collected data   
    def getData(self):

        db = None

        if self.dbtype in self.__dbConnect.keys() and self.dbtype in DB_AVAILABLE:
            db = self.__dbConnect[self.dbtype]()
        else:
            if Streams.log_error:
                print >> Streams.log_error,  "DBaseSource::getData() - Support for %s database not available" % self.dbtype
            raise PackageError, "Support for %s database not available" % self.dbtype


        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
#                data = copy.deepcopy(cursor.fetchone())
                data = cursor.fetchone()
                dh = {"format":"SCALAR", "value":data[0], "tangoDType":(NTP.pTt[type(data[0]).__name__]), "shape":[1,0]}
            elif self.format == 'SPECTRUM':
                data = cursor.fetchall()
#                data = copy.deepcopy(cursor.fetchall())
                if len(data[0]) == 1:
                    ldata = list(el[0] for el in data)
                else:
                    ldata = list(el for el in data[0])
                dh = {"format":"SPECTRUM", "value":ldata, "tangoDType":(NTP.pTt[type(ldata[0]).__name__]), "shape":[len(ldata),0]}
            else:
                data = cursor.fetchall()
#                data = copy.deepcopy(cursor.fetchall())
                ldata = list(list(el) for el in data)
                dh = {"format":"IMAGE", "value":ldata, "tangoDType":NTP.pTt[type(ldata[0][0]).__name__], "shape":[len(ldata), len(ldata[0])]}
            cursor.close()
            db.close()
        return dh



## Client data source
class ClientSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of data
        self.name = None
        ## the current  static JSON object
        self.__globalJSON = None
        ## the current  dynamic JSON object
        self.__localJSON = None
        

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "CL XML" , xml
        dom = minidom.parseString(xml)
        rec = dom.getElementsByTagName("record")
        if rec and len(rec)> 0:
            self.name = rec[0].getAttribute("name") if rec[0].hasAttribute("name") else None
#            print "NAME:", self.name
        if not self.name:
            if Streams.log_error:
                print >> Streams.log_error, "ClientSource::setup() - Client record name not defined: %s" % xml
            raise  DataSourceSetupError, \
                "Client record name not defined: %s" % xml
            


    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " CLIENT record %s" % (self.name)


    ## sets JSON string
    # \brief It sets the currently used  JSON string
    # \param globalJSON static JSON string    
    # \param localJSON dynamic JSON string    
    def setJSON(self, globalJSON, localJSON=None):
        self.__globalJSON = globalJSON
        self.__localJSON = localJSON
            

    ## provides access to the data    
    # \returns  dictionary with collected data   
    def getData(self):
        if  self.__globalJSON and 'data' not in self.__globalJSON.keys() :
            self.__globalJSON = None

        if self.__localJSON and 'data' not in self.__localJSON.keys() :
            self.__localJSON = None
            
        rec = None
        if self.__localJSON and 'data' in  self.__localJSON and self.name in self.__localJSON['data']:
            rec = self.__localJSON['data'][str(self.name)]
        elif self.__globalJSON and 'data' in self.__globalJSON and self.name in self.__globalJSON['data']:
            rec = self.__globalJSON['data'][str(self.name)]
        else:
            return    
        ntp = NTP()
        rank, shape, pythonDType = ntp.arrayRankRShape(rec)

        if rank in NTP.rTf:
            shape.reverse()
            if  shape is None:
                shape = [1,0]
            return {"format":NTP.rTf[rank], "value":rec, 
                    "tangoDType":NTP.pTt[pythonDType.__name__], "shape":shape}
            


class variables(object):    pass


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
        ## datasources xml
        self.__sources = {}
        ## datasources 
        self.__datasources = {}
        ## python script
        self.__script =""
        ## data format
        self.__result ={"format":"SCALAR", 
                        "value":None, 
                        "tangoDType":"DevString",  
                        "shape":[1,0], 
                        "encoding":None, 
                        "decoders":None}

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "CL XML" , xml
        dom = minidom.parseString(xml)
        mds = dom.getElementsByTagName("datasource")
        inputs = []
        if mds and len(mds)>0:
            inputs = mds[0].getElementsByTagName("datasource")
        for inp in inputs:
            if inp.hasAttribute("name") and inp.hasAttribute("type"):
                name = inp.getAttribute("name").strip()
                dstype = inp.getAttribute("type").strip()
                if len(name)>0:
                    if len(name)>3 and name[:2] == 'ds.':
                        name = name[3:]
                    self.__sources[name] = (dstype, inp.toxml())
                else:
                    if Streams.log_error:
                        print >> Streams.log_error, "PyEvalSource::setup() - PyEval input %s not defined" % name
                    raise  DataSourceSetupError, \
                        "PyEvalSource::setup() - PyEval input %s not defined" % name
                        
            else:
                if Streams.log_error:
                    print >> Streams.log_error, "PyEvalSource::setup() - PyEval input name wrongly defined"
                raise  DataSourceSetupError, \
                    "PyEvalSource::setup() - PyEval input name wrongly defined"
        res = dom.getElementsByTagName("result")
        if res and len(res)>0:
            self.__name = res[0].getAttribute("name") if res[0].hasAttribute("name") else 'result'
            if len(self.__name) >3 and self.__name[:2] == 'ds.':
                self.__name = self.__name[3:]
            self.__script = self._getText(res[0]) 
            
        if len(self.__script) == 0:
            if Streams.log_error:
                print >> Streams.log_error, "PyEvalSource::setup() - PyEval script %s not defined" % self.__name
            raise  DataSourceSetupError, \
                "PyEvalSource::setup() - PyEval script %s not defined" % self.__name
            


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
        for name, source in self.__datasources.items():
            if hasattr(source, "setJSON"):
                source.setJSON(self.__globalJSON,self.__localJSON)
            

    ## provides access to the data    
    # \returns  dictionary with collected data   
    def getData(self):
        if not self.__name:
            if Streams.log_error:
                print >> Streams.log_error, "PyEvalSource::getData() - PyEval datasource not set up"
            raise  DataSourceSetupError, \
                 "PyEvalSource::getData() - PyEval datasource not set up"
        class Variables(object): 
            pass
        ds = Variables()
        for name, source in self.__datasources.items():
            dt = source.getData()   
            value = None
            if dt:
                dh = DataHolder(**dt)
                if dh and hasattr(dh,"value"):
                    value = dh.value
            setattr(ds, name, value)

        setattr(ds, self.__name, None)

        exec(self.__script.strip(), {}, {"ds":ds})
        rec = getattr(ds,self.__name)
        ntp = NTP()
        rank, shape, pythonDType = ntp.arrayRankRShape(rec)

        if rank in NTP.rTf:
            shape.reverse()
            if  shape is None:
                shape = [1,0]
            return {"format":NTP.rTf[rank], "value":rec, 
                    "tangoDType":NTP.pTt[pythonDType.__name__], "shape":shape}
            
    


    ## sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.__result["decoders"] = decoders        
        for name, source in self.__datasources.items():
            if hasattr(source, "setDecorders"):
                source.setDecoders(decoders)
        
    ## sets the datasources
    # \param pool datasource pool
    def setDataSources(self, pool):
        
        for name, inp in self.__sources.items():
            if pool and pool.hasDataSource(inp[0]):
                self.__datasources[name] = pool.get(inp[0])()
                self.__datasources[name].setup(inp[1])
                if hasattr(self.__datasources[name],"setJSON") and self.__globalJSON:
                    self.__datasources[name].setJSON(self.__globalJSON)
                if hasattr(self.__datasources[name],"setDataSources"):
                    self.__datasources[name].setDataSources(pool)

            else:
                print >> sys.stderr, "PyEvalSource::setDataSources - Unknown data source"
                if Streams.log_error:
                    print >> Streams.log_error, "PyEvalSource::setDataSources - Unknown data source"
                    
                self.__datasources[name] = DataSource()
        

