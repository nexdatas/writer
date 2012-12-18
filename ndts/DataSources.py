#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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

import json
from xml.dom import minidom
from Types import NTP

try:
    import PyTango
    ## global variable if PyTango module installed
    PYTANGO_AVAILABLE = True
except ImportError, e:
    PYTANGO_AVAILABLE = False
    print "PYTANGO not available: %s" % e


## list of available databases
DB_AVAILABLE = []

try:
    import MySQLdb
    DB_AVAILABLE.append("MYSQL")
except ImportError, e:
    print "MYSQL not available: %s" % e
    
try:
    import psycopg2
    DB_AVAILABLE.append("PGSQL")
except ImportError, e:
    print "PGSQL not available: %s" % e

try:
    import cx_Oracle
    DB_AVAILABLE.append("ORACLE")
except ImportError, e:
    print "ORACLE not available: %s" % e


#import copy



## exception for fetching data from data source
class PackageError(Exception): pass

## exception for setting data source
class DataSourceSetupError(Exception): pass


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
        return xml[start + 1:end].replace("&lt;","<").replace("&gt;","<").replace("&amp;","&")



## Tango data source
class TangoSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of data
        self.name = None
        ## name of the Tango device
        self.device = None
        ## member type of the data, i.e. attribute, property,...
        self.memberType = None
        ## host name of Tango server
        self.hostname = None
        ## port of Tango server
        self.port = None
        ## encoding of Tango DevEncoded variables
        self.encoding = None
        ## decoder pool
        self._decoders = None

    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return "Tango Device %s : %s (%s)" % (self.device, self.name, self.memberType )


    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "TG XML" , xml
        dom = minidom.parseString(xml)
        rec = dom.getElementsByTagName("record")
        if rec and len(rec)> 0:
            self.name = rec[0].getAttribute("name")
        if not self.name:
            raise  DataSourceSetupError, \
                "Tango record name not defined: %s" % xml

        dv = dom.getElementsByTagName("device")
        if dv and len(dv)> 0:
            self.device = dv[0].getAttribute("name")
            self.hostname = dv[0].getAttribute("hostname")
            self.port = dv[0].getAttribute("port")
            self.encoding = dv[0].getAttribute("encoding")
            self.memberType = dv[0].getAttribute("member")
            if not self.memberType or self.memberType not in ["attribute", "command", "property"]:
                self.memberType = "attribute" 
#            print "Tango Device:", self.name, self.device, self.hostname,self.port, self.memberType, self.encoding
        if not self.device :
            raise  DataSourceSetupError, \
                "Tango device name not defined: %s" % xml


    ## sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self._decoders = decoders


    ## data provider
    # \returns dictionary with collected data  
    def getData(self):
        if not PYTANGO_AVAILABLE:
            raise PackageError, "Support for PyTango datasources not available" 

        if self.device and self.memberType and self.name:
            if self.hostname and self.port:
                proxy = PyTango.DeviceProxy("%s:%s/%s" % (self.hostname.encode(),
                                                          self.port.encode(),
                                                          self.device.encode()))
            else:
                proxy = PyTango.DeviceProxy(self.device.encode())
            da = None
            if self.memberType == "attribute":
                alist = proxy.get_attribute_list()

                if self.name.encode() in alist:
                    da = proxy.read_attribute( self.name.encode())
#                    if str(da.data_format).split('.')[-1] == "SPECTRUM":
#                        print "Spectrum Device: ", self.device.encode()
#                    if str(da.data_format).split('.')[-1] == "IMAGE":
#                        print "Image Device: ", self.device.encode()
#                    print "DH:",da.data_format, da.value, da.type, [da.dim_x,da.dim_y],self.encoding, self._decoders
                    return {"format":da.data_format, "value":da.value, "tangoDType":da.type, 
                            "shape":[da.dim_x,da.dim_y],
                            "encoding": self.encoding, "decoders": self._decoders}

            elif self.memberType == "property":
#                print "getting the property: ", self.name
                plist = proxy.get_property_list('*')
                if self.name.encode() in plist:
                    da = proxy.get_property(self.name.encode())[self.name.encode()][0]
                    return {"format":"SCALAR", "value":da, "tangoDType":"DevString", "shape":[1,0]}
            elif self.memberType == "command":
#                print "calling the command: ", self.name
		clist = [cm.cmd_name for cm in proxy.command_list_query()]
                if self.name in clist:
                    cd = proxy.command_query(self.name.encode())
                    da = proxy.command_inout(self.name.encode())
                    return {"format":"SCALAR", "value":da, "tangoDType":cd.out_type, "shape":[1,0], 
                                      "encoding":self.encoding, "decoders":self._decoders}
                    
                        

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
        self._dbConnect = {"MYSQL":self._connectMYSQL, 
                          "PGSQL":self._connectPGSQL,
                          "ORACLE":self._connectORACLE}

    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " %s DataBase %s with %s " % (self.dbtype, self.dbname if self.dbname else "" , self.query )

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "DB XML" , xml
        dom = minidom.parseString(xml)
        query = dom.getElementsByTagName("query")
        if query and len(query)> 0:
            self.format = query[0].getAttribute("format")
#            print "format:", self.format
            self.query = self._getText(query[0])
            
        if not self.format or not self.query:
            raise  DataSourceSetupError, \
                "Database query or its format not defined: %s" % xml

        db = dom.getElementsByTagName("database")
        if db and len(db)> 0:
            self.dbname = db[0].getAttribute("dbname")
            self.dbtype = db[0].getAttribute("dbtype")
            self.user = db[0].getAttribute("user") 
            self.passwd = db[0].getAttribute("passwd")
            self.mode = db[0].getAttribute("mode")
            mycnf = db[0].getAttribute("mycnf")
            if mycnf:
                self.mycnf
            self.hostname = db[0].getAttribute("hostname")
            self.port = db[0].getAttribute("port")
            self.dsn = self._getText(db[0])
            
#            print "DATABASE:", self.dbname, self.dbtype, self.user,self.passwd , self.hostname, self.port, self.mode, self.mycnf,self.dsn




    ## connects to MYSQL database    
    # \returns open database object
    def _connectMYSQL(self):
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
    def _connectPGSQL(self):
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
    def _connectORACLE(self):
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

        if self.dbtype in self._dbConnect.keys() and self.dbtype in DB_AVAILABLE:
            db = self._dbConnect[self.dbtype]()
        else:
            raise PackageError, "Support for %s database not available" % self.dbtype


        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
#                data = copy.deepcopy(cursor.fetchone())
                data = cursor.fetchone()
                dh = {"format":"SCALAR", "value":data[0], "tangoDType":"DevString", "shape":[1,0]}
            elif self.format == 'SPECTRUM':
                data = cursor.fetchall()
#                data = copy.deepcopy(cursor.fetchall())
                if len(data[0]) == 1:
                    ldata = list(el[0] for el in data)
                else:
                    ldata = list(el for el in data[0])
                dh = {"format":"SPECTRUM", "value":ldata, "tangoDType":"DevString", "shape":[len(ldata),0]}
            else:
                data = cursor.fetchall()
#                data = copy.deepcopy(cursor.fetchall())
                ldata = list(list(el) for el in data)
                dh = {"format":"IMAGE", "value":ldata, "tangoDType":"DevString", "shape":[len(ldata), len(ldata[0])]}
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
        self._globalJSON = None
        ## the current  dynamic JSON object
        self._localJSON = None
        

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "CL XML" , xml
        dom = minidom.parseString(xml)
        rec = dom.getElementsByTagName("record")
        if rec and len(rec)> 0:
            self.name = rec[0].getAttribute("name")
#            print "NAME:", self.name
        if not self.name:
            raise  DataSourceSetupError, \
                "Client record name not defined: %s" % xml
            


    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " client record %s from JSON:  %s or %s " % (self.name, self._localJSON , self._globalJSON  )


    ## sets JSON string
    # \brief It sets the currently used  JSON string
    # \param globalJSON static JSON string    
    # \param localJSON dynamic JSON string    
    def setJSON(self, globalJSON, localJSON=None):
        self._globalJSON = globalJSON
        self._localJSON = localJSON
            

    ## provides access to the data    
    # \returns  dictionary with collected data   
    def getData(self):
        
        if  self._globalJSON and 'data' not in self._globalJSON.keys() :
            self._globalJSON = None

        if self._localJSON and 'data' not in self._localJSON.keys() :
            self._localJSON = None
            
        rec = None
        if self._localJSON and 'data' in  self._localJSON and self.name in self._localJSON['data']:
            rec = self._localJSON['data'][str(self.name)]
        elif self._globalJSON and 'data' in self._globalJSON and self.name in self._globalJSON['data']:
            rec = self._globalJSON['data'][str(self.name)]
        else:
            return    
        ntp = NTP()
        rank, rshape, pythonDType = ntp.arrayRankRShape(rec)
        if rank in NTP.rTf:
            shape = rshape.reverse()
            if  shape is None:
                shape = [1,0]
            return {"format":NTP.rTf[rank], "value":rec, 
                    "tangoDType":NTP.pTt[pythonDType.__name__], "shape":shape}
            
    
