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
## \file DataSource.py
# data-source types

import json

import PyTango 

from Element import *
from DataHolder import *
from Types import *

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



## Data source
class DataSource(object):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        ## name of the host with the data source
        self.hostname = None
        ## port related to the host
        self.port = None
        ## name of data
        self.name = None

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

## Tango data source
class TangoSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of the tango device
        self.device = None
        ## member type of the data, i.e. attribute, property,...
        self.memberType = None

    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return "Tango Device %s : %s (%s)" % (self.device, self.name, self.memberType )



    ## data provider
    # \returns DataHolder with collected data  
    def getData(self):
        if self.device and self.memberType and self.name:
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
                    return DataHolder(da.data_format, da.value, da.type, [da.dim_x,da.dim_y])

            elif self.memberType == "property":
#                print "getting the property: ", self.name
                plist = proxy.get_property_list('*')
                if self.name.encode() in plist:
                    da = proxy.get_property(self.name.encode())[self.name.encode()][0]
                    return DataHolder("SCALAR", da, "DevString", [1,0])
            elif self.memberType == "command":
#                print "calling the command: ", self.name
		clist = [cm.cmd_name for cm in proxy.command_list_query()]
                if self.name in clist:
                    cd = proxy.command_query(self.name.encode())
                    da = proxy.command_inout(self.name.encode())
                    return DataHolder("SCALAR", da, cd.out_type, [1,0])
                    
                        

## DataBase data source
class DBaseSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
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
    # \returns  DataHolder with collected data   
    def getData(self):

        db = None

        if self.dbtype in self._dbConnect.keys() and self.dbtype in DB_AVAILABLE:
            db = self._dbConnect[self.dbtype]()
                

        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
                data = cursor.fetchone()
                dh = DataHolder("SCALAR", data[0], "DevString", [1,0])
            elif self.format == 'SPECTRUM':
                data = cursor.fetchall()
                if len(data[0]) == 1:
                    ldata = list(el[0] for el in data)
                else:
                    ldata = list(el for el in data[0])
                dh = DataHolder("SPECTRUM", ldata, "DevString", [len(ldata),0])
            else:
                data = cursor.fetchall()
                ldata = list(list(el) for el in data)
                dh = DataHolder("IMAGE", ldata, "DevString", [len(ldata), len(ldata[0])])
            cursor.close()
            db.close()
        return dh

## Client data source
class ClientSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## the current  static JSON object
        self._globalJSON = None
        ## the current  dynamic JSON object
        self._localJSON = None
        
    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return " client record %s from JSON:  %s or %s " % (self.name, self._localJSON , self._globalJSON  )


    ## sets JSON string
    # \brief It sets the currently used  JSON string
    # \param globalJSON static JSON string    
    # \param localJSON dynamic JSON string    
    def setJSON(self, globalJSON, localJSON=None):
            self._globalJSON = json.loads(globalJSON)
            if localJSON:
                self._localJSON = json.loads(localJSON)
            else:
                self._localJSON = None
            

    ## provides access to the data    
    # \returns  DataHolder with collected data   
    def getData(self):
        
        
        if  self._globalJSON and 'data' not in self._globalJSON.keys() :
            self._globalJSON = None

        if self._localJSON and 'data' not in self._localJSON.keys() :
            self._localJSON = None

        if self._globalJSON and self._localJSON:
            mergedJSON = json.loads(dict(self._globalJSON.items() + self._localJSON.items()))
        elif self._localJSON:
            mergedJSON = self._localJSON 
        elif self._globalJSON:
            mergedJSON = self._globalJSON 
        else:
            return None
            
        
        if self.name in mergedJSON['data']:
            rec = mergedJSON['data'][self.name]
            ntp = NTP()
            rank, rshape, pythonDType = ntp.arrayRankRShape(rec)
            if rank in NTP.rTf:
                return DataHolder(NTP.rTf[rank], rec, NTP.pTt[pythonDType.__name__], rshape.reverse())
            



## Sardana data source
class SardanaSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)

    ## provides access to the data    
    # \returns  DataHolder with collected data   
    def getData(self):
        pass


## Data source creator
class DataSourceFactory(Element):        
    ## constructor
    # \param name name of the tag
    # \param attrs dictionary with the tag attributes
    # \param last the last element on the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        ## dictionary with data source classes
        self._sourceClass = {"DB":DBaseSource, "TANGO":TangoSource,
                            "CLIENT":ClientSource, "SARDANA":SardanaSource}
        self.createDSource(name, attrs)

    ## creates data source   
    # \param name name of the tag
    # \param attrs dictionary with the tag attributes
    def createDSource(self, name, attrs):
        if "type" in attrs.keys():
            if attrs["type"] in self._sourceClass.keys():
                self._last.source = self._sourceClass[attrs["type"]]()
            else:
                print "Unknown data source"
                self._last.source = DataSource()
        else:
            print "Typeless data source"
            self._last.source = DataSource()



