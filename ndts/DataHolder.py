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
## \file DataHolder.py
#
                         
from Types import *

import numpy

## Holder for passing data 
class DataHolder(object):

    ## constructor
    # \param format format of the data, i.e. SCALAR, SPECTRUM, IMAGE
    # \param value value of the data. It may be also 1D and 2D array
    # \param tangoDType type of the data
    # \param shape shape of the data
    def __init__(self, format, value, tangoDType, shape):

        ## data format
        self.format = format
        ## data value
        self.value = value
        ## data type
        self.tangoDType = tangoDType
        ## data shape
        self.shape = shape


    ## casts the data into given type
    # \param tp given type of data
    # \returns numpy array of defined type or list for strings or value for SCALAR
    def cast(self, tp):
        if str(self.format).split('.')[-1] == "SCALAR":
            if tp in NTP.npTt.keys() and NTP.npTt[tp] == str(self.tangoDType):
                return self.value
            else:
#                print "casting ", self.tangoDType ," to ", tp
                return NTP.convert[tp](self.value)

        else:
            if tp in NTP.npTt.keys() and NTP.npTt[tp] == str(self.tangoDType) and tp != "string":
                    return numpy.array(self.value, dtype=tp)
            else:    
#                print "casting ", self.tangoDType ," to ", tp
                if str(self.format).split('.')[-1] == "SPECTRUM":
                    if tp == "string":
                        return [ NTP.convert[tp](el) for el in self.value]
                    else:
                        return numpy.array([ NTP.convert[tp](el) for el in self.value], dtype=tp)
                
                if str(self.format).split('.')[-1] == "IMAGE":
                    if tp == "string":
                        return [ [ NTP.convert[tp](self.value[j][i]) \
                                       for i in range(len(self.value[j])) ] \
                                     for j in range(len(self.value)) ]
                    else:
                        return numpy.array([ [ NTP.convert[tp](self.value[j][i]) \
                                                   for i in range(len(self.value[j])) ] \
                                                 for j in range(len(self.value)) ], dtype=tp)

        

