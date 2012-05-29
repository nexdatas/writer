#!/usr/bin/env python
"""@package docstring
@file DataSource.py
"""
                                                                      
from Element import *


class DataSource(Element):
    def __init__(self,name,attrs):
        Element.__init__(self,name,attrs)
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
    def __init__(self,name,attrs):
        DataSource.__init__(self,name,attrs)
        self.device=None
        self.type=None
        self.data=None
    def getData(self):
        pass


class DBaseSource(DataSource):
    def __init__(self,name,attrs):
        DataSource.__init__(self,name,attrs)
        self.query=None
        self.dbname=None
    def getData(self):
        pass

class ClientSource(DataSource):
    def __init__(self,name,attrs):
        DataSource.__init__(self,name,attrs)
        pass
    def getData(self):
        pass

class SardanaSource(DataSource):
    def __init__(self,name,attrs):
        DataSource.__init__(self,name,attrs)

    def getData(self):
        pass

