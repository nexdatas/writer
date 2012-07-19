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
## \file Types.py
# Type converter
                       
from collections import Iterable
                                               
## type converter
class NTP(object):

    ## map of Python:Tango types
    pTt = {"int":"DevLong64", "float":"DevDouble", "str":"DevString"}

    ## map of Numpy:Tango types
    npTt = {"int":"DevLong64", "int64":"DevLong64", "int32":"DevLong", "uint":"DevULong64", 
            "uint64":"DevULong64", "uint32":"DevULong", "float":"DevDouble", 
            "float64":"DevDouble", "float32":"DevFloat", "string":"DevString"}

    ## map of NEXUS : numpy types 
    nTnp = {"NX_FLOAT32":"float32", "NX_FLOAT64":"float64", "NX_FLOAT":"float64", 
            "NX_NUMBER":"float64", "NX_INT":"int64", "NX_INT64":"int64", 
            "NX_INT32":"int32", "NX_UINT64":"uint64", "NX_UINT32":"uint32", 
            "NX_DATE_TIME":"string", "NX_CHAR":"string", "NX_BOOLEAN":"int32"}

    ## map of type : converting function
    convert = {"float32":float, "float64":float, "float":float, "int64":long, "int32":int, 
               "int":int, "uint64":long, "uint32":int, "uint":int, "string":str}

    ## map of tag attribute types 
    aTn = {"signal":"NX_INT", "axis":"NX_INT", "primary":"NX_INT32", "offset":"NX_INT", 
          "stride":"NX_INT", "vector":"NX_FLOATVECTOR", "file_time":"NX_DATE_TIME", 
          "file_update_time":"NX_DATE_TIME", "restricted":"NX_INT", 
          "ignoreExtraGroups":"NX_BOOLEAN", "ignoreExtraFields":"NX_BOOLEAN", 
          "ignoreExtraAttributes":"NX_BOOLEAN", "minOccus":"NX_INT", "maxOccus":"NX_INT"
        }

    ## map of rank : data format
    rTf = {0:"SCALAR", 1:"SPECTRUM", 2:"IMAGE"}

    ## array rank
    # \brief It calculates the rank of the array
    # \param array given array
    def arrayRank(self, array) :
        rank = 0
        if isinstance(array, Iterable) and not isinstance(array, str):       
            rank = 1 + self.arrayRank(array[0])
        return rank            


    ## array rank, inverse shape and type
    # \brief It calculates the rank, inverse shape and type of the first element of the array
    # \param array given array
    def arrayRankRShape(self, array):        
        rank = 0
        shape = []
        dtype = None
        if isinstance(array, Iterable) and not isinstance(array, str):
            rank,shape,dtype = self.arrayRankRShape(array[0])
            shape.append(len(array))
            rank += 1
        else:
           dtype = type(array)
        return (rank, shape, dtype)            
