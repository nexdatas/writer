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
## \package test nexdatas
## \file TestDataSource.py
# unittests for field Tags running Tango Server
#
import numpy

from ndts.Types import NTP
from ndts.DataSources import DataSource








## test datasource
class TestDataSource(DataSource):
        ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        ## flag for running getData
        self.dataTaken = False
        ## list of dimensions
        self.dims = [] 
        ## if numpy  datasource
        self.numpy = True
        ## validity
        self.valid = True
        ## returned Data
        self.value = None


    ## sets the parameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        pass


    ## access to data
    # \brief It is an abstract method providing data   
    def getData(self):
        if self.valid:
            self.dataTaken = True
            if self.value:
                return self.value
            elif len(self.dims) == 0:
                return {"format":NTP.rTf[0], "value":1, 
                        "tangoDType":"DevLong", "shape":[0,0]}
            elif numpy:
                return {"format":NTP.rTf[len(self.dims)], "value":numpy.ones(self.dims), 
                        "tangoDType":"DevLong", "shape":self.dims}
            elif len(self.dims) == 1:
                return {"format":NTP.rTf[1], "value":([1] * self.dims[0]), 
                        "tangoDType":"DevLong", "shape":[self.dims[0], 0]}
            elif len(self.dims) == 2:
                return {"format":NTP.rTf[2], "value":([[1] * self.dims[1]]*self.dims[0] ), 
                        "tangoDType":"DevLong", "shape":[self.dims[0], 0]}
                

    ## checks if the data is valid
    # \returns if the data is valid
    def isValid(self):
        return self.valid


    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return "Test DataSource"


