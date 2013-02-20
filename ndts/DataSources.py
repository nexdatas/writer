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
        return xml[start + 1:end].replace("&lt;","<").replace("&gt;","<").replace("&amp;","&")



## Tango data source
class TangoSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of datar
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
        self.__decoders = None

    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " Tango Device %s : %s (%s)" % (self.device, self.name, self.memberType )


    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
#        print "TG XML" , xml
        dom = minidom.parseString(xml)
        rec = dom.getElementsByTagName("record")
        if rec and len(rec)> 0:
            self.name = rec[0].getAttribute("name") if rec[0].hasAttribute("name") else None
        if not self.name:
            raise  DataSourceSetupError, \
                "Tango record name not defined: %s" % xml

        dv = dom.getElementsByTagName("device")
        if dv and len(dv)> 0:
            self.device = dv[0].getAttribute("name") if dv[0].hasAttribute("name") else None
            self.hostname = dv[0].getAttribute("hostname") if dv[0].hasAttribute("hostname") else None
            self.port = dv[0].getAttribute("port") if dv[0].hasAttribute("port") else None
            self.encoding = dv[0].getAttribute("encoding") if dv[0].hasAttribute("encoding") else None
            self.memberType = dv[0].getAttribute("member") if dv[0].hasAttribute("member") else None
            if not self.memberType or self.memberType not in ["attribute", "command", "property"]:
                self.memberType = "attribute" 
#            print "Tango Device:", self.name, self.device, self.hostname,self.port, self.memberType, self.encoding
        if not self.device :
            raise  DataSourceSetupError, \
                "Tango device name not defined: %s" % xml


    ## sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        self.__decoders = decoders


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
#                print "getting the attribute: ", self.name
                alist = proxy.get_attribute_list()

                if self.name.encode() in alist:
                    da = proxy.read_attribute( self.name.encode())
                    return {"format":str(da.data_format).split('.')[-1], 
                            "value":da.value, "tangoDType":str(da.type).split('.')[-1], 
                            "shape":([da.dim_y,da.dim_x] if da.dim_y else [da.dim_x, 0]),
                            "encoding": self.encoding, "decoders": self.__decoders}

            elif self.memberType == "property":
#                print "getting the property: ", self.name
                plist = proxy.get_property_list('*')
                if self.name.encode() in plist:
                    da = proxy.get_property(self.name.encode())[self.name.encode()][0]
                    return {"format":"SCALAR", "value":str(da), "tangoDType":"DevString", "shape":[1,0]}
            elif self.memberType == "command":
#                print "calling the command: ", self.name
		clist = [cm.cmd_name for cm in proxy.command_list_query()]
                if self.name in clist:
                    cd = proxy.command_query(self.name.encode())
                    da = proxy.command_inout(self.name.encode())
                    return {"format":"SCALAR", "value":da, 
                            "tangoDType":str(cd.out_type).split('.')[-1],  "shape":[1,0], 
                            "encoding":self.encoding, "decoders":self.__decoders}
                    
                        

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
        return " %s DataBase %s with %s " % (self.dbtype, self.dbname if self.dbname else "" , self.query )

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
            raise PackageError, "Support for %s database not available" % self.dbtype


        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
#                data = copy.deepcopy(cursor.fetchone())
                data = cursor.fetchone()
                dh = {"format":"SCALAR", "value":str(data[0]), "tangoDType":"DevString", "shape":[1,0]}
#                print "SCALAR",dh
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
            raise  DataSourceSetupError, \
                "Client record name not defined: %s" % xml
            


    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " Client record %s from JSON: %s or %s " % (self.name, self.__localJSON , self.__globalJSON  )


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
            
    
