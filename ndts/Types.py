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
## \file Types.py
# Type converter
                     
## set of converters
class Converters(object):

    ## converts to bool
    # \param cls class instance
    # \param value variable to convert
    # \returns result in bool type
    @classmethod
    def toBool(cls, value):
        if type(value).__name__ == 'str' or type(value).__name__ == 'unicode':
            lvalue = value.strip().lower()
            if lvalue == 'false' or lvalue == '0':
                return False
            else:
                return True
        elif value:
            return True
        return False


  
## type converter
class NTP(object):




    ## map of Python:Tango types
#    pTt = {"int":"DevLong64", "float":"DevDouble", "str":"DevString"}
    pTt = {"int":"DevLong64", "float":"DevDouble", "str":"DevString", "unicode":"DevString", 
           "bool":"DevBoolean"}

    ## map of Numpy:Tango types
    npTt = {"int":"DevLong64", "int64":"DevLong64", "int32":"DevLong",
            "int16":"DevShort", "int8":"DevUChar", "uint":"DevULong64", 
            "uint64":"DevULong64", "uint32":"DevULong", "uint16":"DevUShort", 
            "uint8":"DevUChar", "float":"DevDouble", "float64":"DevDouble", 
            "float32":"DevFloat", "string":"DevString", "bool":"DevBoolean"}

    ## map of NEXUS : numpy types 
    nTnp = {"NX_FLOAT32":"float32", "NX_FLOAT64":"float64", "NX_FLOAT":"float64", 
            "NX_NUMBER":"float64", "NX_INT":"int64", "NX_INT64":"int64", 
            "NX_INT32":"int32", "NX_INT16":"int16", "NX_INT8":"int8", 
            "NX_UINT64":"uint64", "NX_UINT32":"uint32", "NX_UINT16":"uint16", "NX_UINT8":"uint8", 
            "NX_UINT":"uint64", "NX_POSINT":"uint64", 
            "NX_DATE_TIME":"string", "ISO8601":"string", "NX_CHAR":"string", "NX_BOOLEAN":"bool"}

    ## map of type : converting function
    convert = {"float32":float, "float64":float, "float":float, "int64":long, "int32":int,  
               "int16":long, "int8":int, "int":int, "uint64":long, "uint32":int, "uint16":long,
               "uint8":int, "uint":int, "string":str, "bool":Converters.toBool}

    ## map of tag attribute types 
    aTn = {"signal":"NX_INT", "axis":"NX_INT", "primary":"NX_INT32", "offset":"NX_INT", 
          "stride":"NX_INT", "file_time":"NX_DATE_TIME", 
          "file_update_time":"NX_DATE_TIME", "restricts":"NX_INT", 
          "ignoreExtraGroups":"NX_BOOLEAN", "ignoreExtraFields":"NX_BOOLEAN", 
          "ignoreExtraAttributes":"NX_BOOLEAN", "minOccus":"NX_INT", "maxOccus":"NX_INT"
        }

    ## map of vector tag attribute types 
    aTnv = {"vector":"NX_FLOAT"}

    ## map of rank : data format
    rTf = {0:"SCALAR", 1:"SPECTRUM", 2:"IMAGE"}

    ## array rank
    # \brief It calculates the rank of the array
    # \param array given array
    def arrayRank(self, array) :
        rank = 0
        if hasattr(array, "__iter__") and not isinstance(array, str):       
            rank = 1 + self.arrayRank(array[0])
        return rank            

    

    ## array rank, inverse shape and type
    # \brief It calculates the rank, inverse shape and type of the first element of the array
    # \param array given array
    def arrayRankRShape(self, array):        
        rank = 0
        shape = []
        pythonDType = None
        if hasattr(array, "__iter__") and not isinstance(array, str):
            rank, shape, pythonDType = self.arrayRankRShape(array[0])
            shape.append(len(array))
            rank += 1
        else:
            pythonDType = type(array)
        return (rank, shape, pythonDType)            
