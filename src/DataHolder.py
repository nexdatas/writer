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
## \package nexdatas
## \file DataHolder.py
#
                         
import numpy

## Holder for passing data 
class DataHolder:

    ## constructor
    # \param dFormat format of the data, i.e. SCALAR, SPECTRUM, IMAGE
    # \param dValue value of the data. It may be also 1D and 2D array
    # \param dType type of the data
    # \param dShape shape of the data
    def __init__(self,dFormat,dValue,dType,dShape):

        ## data format
        self.format=dFormat
        ## data value
        self.value=dValue
        ## data type
        self.type=dType
        ## data shape
        self.shape=dShape

    ## typeless array   
    # \returns numpy array when the data is not SCALAR
    def typeless_array(self):
        if str(self.format).split('.')[-1] == "SPECTRUM":
            return numpy.array(self.value)
        
        if str(self.format).split('.')[-1] == "IMAGE":
            return numpy.array(self.value)

    ## array with a type    
    # \param tp type of the data    
    # \returns numpy array of defined type when the data is not SCALAR 
    def array(self,tp):
        if str(self.format).split('.')[-1] == "SPECTRUM":
            return numpy.array(self.value,dtype=tp)
        
        if str(self.format).split('.')[-1] == "IMAGE":
            return numpy.array(self.value,dtype=tp)


