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
## \file DataSourcePool.py
# datasource classes

import struct
import numpy

import DataSources


## DataSource pool
class DataSourcePool(object):        


    ## constructor
    # \brief It creates know datasources    
    # \param configJSON string with datasources    
    def __init__(self, configJSON = None):
        self.__pool = {"DB":DataSources.DBaseSource, "TANGO":DataSources.TangoSource,
                      "CLIENT":DataSources.ClientSource, "PYEVAL":DataSources.PyEvalSource}
        self.__appendUserDataSources(configJSON)
        ## global variables for specific datasources
        self.common = {}
        ## step counter: INIT: -1; STEP: 1,2,3...; FINAL: -2; 
        self.counter = 0

    ## loads user datasources
    # \param configJSON string with datasources    
    def __appendUserDataSources(self, configJSON):
        if configJSON and 'datasources' in configJSON.keys() and  hasattr(configJSON['datasources'],'keys'):
            for dk in configJSON['datasources'].keys():
                pkl = configJSON['datasources'][dk].split(".")
                dec =  __import__(".".join(pkl[:-1]), globals(), locals(), pkl[-1])  
                self.append(getattr(dec, pkl[-1]), dk)
            

            
    ## checks it the datasource is registered        
    # \param datasource the given datasource
    # \returns True if it the datasource is registered        
    def hasDataSource(self, datasource):
        return True if datasource in self.__pool.keys() else False


    ## checks it the datasource is registered        
    # \param datasource the given datasource name
    # \returns datasource type if it the datasource is registered        
    def get(self, datasource):
        if datasource in self.__pool.keys():
            return self.__pool[datasource]

    
    ## adds additional datasource
    # \param name name of the adding datasource
    # \param datasource instance of the adding datasource
    # \returns name of datasource
    def append(self, datasource, name):
        self.__pool[name] = datasource
        if not hasattr(datasource,"setup") or not hasattr(datasource,"getData") \
                or not hasattr(datasource,"isValid"):
            self.pop(name)
            return 
        return name


    ## adds additional datasource
    # \param name name of the adding datasource
    def pop(self, name):
        self.__pool.pop(name, None)

        
