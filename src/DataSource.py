#!/usr/bin/env python
"""@package docstring
@file DataSource.py
"""
                                                                      
from Element import *



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
#        return False


class TangoSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.device=None
        self.type=None
        self.data=None
    def getData(self):
        pass


class DBaseSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)
        self.query=None
        self.dbname=None
    def getData(self):
        pass

class ClientSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)
        pass
    def getData(self):
        pass

class SardanaSource(DataSource):
    def __init__(self):
        DataSource.__init__(self)

    def getData(self):
        pass


class DataSourceFactory(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        self.createDSource(name,attrs)

        
    def createDSource(self, name, attrs):
        if "type" in attrs.keys():
            if attrs["type"] == "DB" :
                self.last.source=DBaseSource()
                if "dbname" in attrs.keys():
                    self.last.source.dbname=attrs["dbname"]
                if "query" in attrs.keys():
                    self.last.source.query=attrs["query"]
            elif attrs["type"] == "TANGO" :
                self.last.source=TangoSource()
                if "device" in attrs.keys():
                    self.last.source.device=attrs["device"]
            elif attrs["type"] == "CLIENT" :
                self.last.source=ClientSource()
            elif attrs["type"] == "SARDANA" :
                self.last.source=SardanaSource()
                if "door" in attrs.keys():
                    self.last.source.device=attrs["door"]
            else:
                print "Unknown data source"
                self.last.source=DataSource()
        else:
            print "Unknown data source"
            self.last.source=DataSource()
                    
            


        if "strategy" in attrs.keys():
            self.last.strategy=attrs["strategy"]

        if "hostname" in attrs.keys():
            self.last.hostname=attrs["hostname"]

        if "port" in attrs.keys():
            self.last.port=attrs["port"]


