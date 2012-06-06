#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""@package docstring
@file DataSource.py
"""
                                                                      
from Element import *

from PyTango import *

from DataHolder import *

import MySQLdb


class DataSource:
    def __init__(self):
        self.strategy=None
        self.hostname=None
        self.port=None
        self.name=None

    def getData(self):
        pass

    def isValid(self):
        return True


class TangoSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.device=None
        self.type=None
# @TODO
        self.data=None

    def getData(self):
        if self.device and self.type and self.name:
            proxy=DeviceProxy(self.device.encode())
            if self.type == "attribute":
                alist=proxy.get_attribute_list()
#                print alist
                if self.name.encode() in alist:
                    da=proxy.read_attribute( self.name.encode())
#                    print "Atribute: ",da
#                    print "Atribute: ",(da.data_format,da.value,da.type,[da.dim_x,da.dim_y])
                    if str(da.data_format).split('.')[-1] == "SPECTRUM":
                        print "Spectrum Device: ", self.device.encode()
#                        print "Atribute: ",da
#                        print "Atribute: ",(da.data_format,da.value,da.type,[da.dim_x,da.dim_y])
                    if str(da.data_format).split('.')[-1] == "IMAGE":
                        print "Image Device: ", self.device.encode()
                        print "Atribute: ",da

                    return DataHolder(da.data_format,da.value,da.type,[da.dim_x,da.dim_y])

class DBaseSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.query=None
        self.dbname=None
        self.user=None
        self.passwd=None
        self.mycnf='/etc/my.cnf'
        self.format=None

    def getData(self):
        print "QUERY: ", self.query
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
        
        print "ARGS", args
        print "FORMAT", self.format
        db = MySQLdb.connect(**args)
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
        print "DB DH:" , dh.value    
        return dh

class ClientSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.myJSON="{}"
        
    def setJSON(self,json):
        self.myJSON=json
    
    def getData(self):
        print "JSON:", self.myJSON

class SardanaSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)

    def getData(self):
        pass


class DataSourceFactory(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        self.sourceClass={"DB":DBaseSource,"TANGO":TangoSource,
                          "CLIENT":ClientSource,"SARDANA":SardanaSource}
        self.createDSource(name,attrs)
        
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
        if "hostname" in attrs.keys():
            self.last.source.hostname=attrs["hostname"]
        if "port" in attrs.keys():
            self.last.source.port=attrs["port"]


