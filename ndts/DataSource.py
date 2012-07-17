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
# \file DataSource.py

                                                                      
from Element import *

from PyTango import *

from DataHolder import *

from Types import *

DB_AVAILABLE=[]

try:
    import MySQLdb
    DB_AVAILABLE.append("MYSQL")
except ImportError,e:
    print "MYSQL not available: %s" % e
    
try:
    import psycopg2
    DB_AVAILABLE.append("PGSQL")
except ImportError,e:
    print "PGSQL not available: %s" % e



try:
    import cx_Oracle
    DB_AVAILABLE.append("ORACLE")
except ImportError,e:
    print "ORACLE not available: %s" % e


import json

## Data source
class DataSource(object):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        ## strategy, i.e. INIT, STEP of FINAL
        self.strategy=None
        ## name of the host with the data source
        self.hostname=None
        ## port related to the host
        self.port=None
        ## name of data
        self.name=None

    ## access to data
    # \brief It is an abstract method providing data   
    def getData(self):
        pass

    ## checks if the data is valid
    # \returns if the data is valid
    def isValid(self):
        return True

## Tango data source
class TangoSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of the tango device
        self.device=None
        ## type of the data, i.e. attribute, property,...
        self.type=None

    ## data provider
    # \returns DataHolder with collected data  
    def getData(self):
        if self.device and self.type and self.name:
            proxy=DeviceProxy(self.device.encode())
            da=None
            if self.type == "attribute":
                alist=proxy.get_attribute_list()

                if self.name.encode() in alist:
                    da=proxy.read_attribute( self.name.encode())
                    if str(da.data_format).split('.')[-1] == "SPECTRUM":
                        print "Spectrum Device: ", self.device.encode()
                    if str(da.data_format).split('.')[-1] == "IMAGE":
                        print "Image Device: ", self.device.encode()
                    return DataHolder(da.data_format,da.value,da.type,[da.dim_x,da.dim_y])

            elif self.type == "property":
                print "getting the property: ", self.name
                plist=proxy.get_property_list('*')
                if self.name.encode() in plist:
                    da=proxy.get_property(self.name.encode())[self.name.encode()][0]
                    return DataHolder("SCALAR",da,"DevString",[1,0])
            elif self.type == "command":
                print "calling the command: ", self.name
		clist=[cm.cmd_name for cm in proxy.command_list_query()]
                if self.name in clist:
                    cd = proxy.command_query(self.name.encode())
                    da=proxy.command_inout(self.name.encode())
                    return DataHolder("SCALAR",da,cd.out_type,[1,0])
                    
                        

## DataBase data source
class DBaseSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## database query
        self.query=None
        ## DSN string
        self.dsn=None
        ## database type, i.e. MYSQL, PGSQL, ORACLE
        self.dbtype=None
        ## oracle database mode
        self.mode=None
        ## database name
        self.dbname=None
        ## database user
        self.user=None
        ## database password
        self.passwd=None
        ## mysql database configuration file
        self.mycnf='/etc/my.cnf'
        ## record format, i.e. SCALAR, SPECTRUM, IMAGE
        self.format=None

        ## map 
        self.dbConnect={"MYSQL":self.connectMYSQL, 
                        "PGSQL":self.connectPGSQL,
                        "ORACLE":self.connectORACLE}

    ## connects to MYSQL database    
    # \returns open database object
    def connectMYSQL(self):
        args={}
        if self.mycnf:
            args["read_default_file"]=self.mycnf.encode()
        if self.dbname:
            args["db"]=self.dbname.encode()
        if self.user:
            args["user"]=self.user.encode()
        if self.passwd:
            args["passwd"]=self.passwd.encode()
        if self.hostname:
            args["host"]=self.hostname.encode()
        if self.port:
            args["port"]=int(self.port)
            
        return MySQLdb.connect(**args)

    ## connects to PGSQL database    
    # \returns open database object
    def connectPGSQL(self):
        args={}

        if self.dbname:
            args["database"]=self.dbname.encode()
        if self.user:
            args["user"]=self.user.encode()
        if self.passwd:
            args["password"]=self.passwd.encode()
        if self.hostname:
            args["host"]=self.hostname.encode()
        if self.port:
            args["port"]=int(self.port)
            
        return psycopg2.connect(**args)

    ## connects to ORACLE database    
    # \returns open database object
    def connectORACLE(self):
        args={}
        if self.user:
            args["user"]=self.user.encode()
        if self.passwd:
            args["password"]=self.passwd.encode()
        if self.dsn:
            args["dsn"]=self.dsn.encode()
        if self.mode:
            args["mode"]=self.mode.encode()
            
        return  cx_Oracle.connect(**args)

    ## provides access to the data    
    # \returns  DataHolder with collected data   
    def getData(self):

        db=None

        if self.dbtype in self.dbConnect.keys() and self.dbtype in DB_AVAILABLE:
            db=self.dbConnect[self.dbtype]()
                

        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
                data = cursor.fetchone()
                dh=DataHolder("SCALAR",data[0],"DevString",[1,0])
            elif self.format == 'SPECTRUM':
                data = cursor.fetchall()
                if len(data[0]) == 1:
                    ldata=list(el[0] for el in data)
                else:
                    ldata=list(el for el in data[0])
                dh=DataHolder("SPECTRUM",ldata,"DevString",[len(ldata),0])
            else:
                data = cursor.fetchall()
                ldata=list(list(el) for el in data)
                dh=DataHolder("IMAGE",ldata,"DevString",[len(ldata),len(ldata[0])])
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
        self.JSON=None
        ## the current  dynamic JSON object
        self.lJSON=None
        
    ## sets JSON string
    # \brief It sets the currently used  JSON string
    # \param sJSON static JSON string    
    # \param lJSON dynamic JSON string    
    def setJSON(self,sJSON,lJSON=None):
        self.JSON=json.loads(sJSON)
        if lJSON:
            self.lJSON=json.loads(lJSON)
        else:
            self.lJSON=None
    
    ## provides access to the data    
    # \returns  DataHolder with collected data   
    def getData(self):
        
        
        if  self.JSON and 'data' not in self.JSON.keys() :
            self.JSON= None

        if self.lJSON and 'data' not in self.lJSON.keys() :
            self.lJSON= None

        if self.JSON and  self.lJSON:
            myJSON=json.loads(dict(self.JSON.items() + self.lJSON.items()))
        elif self.lJSON:
            myJSON=self.lJSON 
        elif self.JSON:
            myJSON=self.JSON 
        else:
            return None
            
        

        if self.name in myJSON['data']:
            rec=myJSON['data'][self.name]
            ntp=NTP()
            rank,rshape,dtype=ntp.arrayRankRShape(rec)
            if rank in NTP.rTf:
                return DataHolder(NTP.rTf[rank],rec,NTP.pTt[dtype.__name__],rshape.reverse())
            



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
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        ## dictionary with data source classes
        self.sourceClass={"DB":DBaseSource,"TANGO":TangoSource,
                          "CLIENT":ClientSource,"SARDANA":SardanaSource}
        self.createDSource(name,attrs)

    ## creates data source   
    # \param name name of the tag
    # \param attrs dictionary with the tag attributes
    def createDSource(self, name, attrs):
        if "type" in attrs.keys():
            if attrs["type"] in self.sourceClass.keys():
                self.last.source=self.sourceClass[attrs["type"]]()
            else:
                print "Unknown data source"
                self.last.source=DataSource()
        else:
            print "Typeless data source"
            self.last.source=DataSource()

        if "strategy" in attrs.keys():
            self.last.source.strategy=attrs["strategy"]


