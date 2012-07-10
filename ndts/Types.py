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
## \package ndts nexdatas
## \file Types.py
# Type converter
                       
from collections import Iterable
                                               
## type converter
class NTP:
    ## Tango types
    tTypes=["DevVoid",
            "DevBoolean",
            "DevShort",
            "DevLong",
            "DevFloat",
            "DevDouble",
            "DevUShort",
            "DevULong",
            "DevString",
            "DevVarCharArray",
            "DevVarShortArray",
            "DevVarLongArray",
            "DevVarFloatArray",
            "DevVarDoubleArray",
            "DevVarUShortArray",
            "DevVarULongArray",
            "DevVarStringArray",
            "DevVarLongStringArray",
            "DevVarDoubleStringArray",
            "DevState",
            "ConstDevString",
            "DevVarBooleanArray",
            "DevUChar",
            "DevLong64",
            "DevULong64",
            "DevVarLong64Array",
            "DevVarULong64Array",
            "DevInt",
            "DevEncoded"]
    
    ## NeXuS types corresponding to the Tango types
    nTypes=["NX_CHAR",
            "NX_BOOLEAN",
            "NX_INT32",
            "NX_INT32",
            "NX_FLOAT32",
            "NX_FLOAT64",
            "NX_UINT32",
            "NX_UINT32",
            "NX_CHAR",
            "NX_CHAR"
            "NX_INT32",
            "NX_INT32",
            "NX_FLOAT32",
            "NX_FLOAT64",
            "NX_UINT32",
            "NX_UINT32",
            "NX_CHAR",
            "NX_CHAR",
            "NX_CHAR",
            "NX_CHAR",
            "NX_CHAR",
            "NX_BOOLEAN",
            "NX_CHAR",
            "NX_INT64",
            "NX_UINT64",
            "NX_INT64",
            "NX_UINT64",
            "NX_INT32",
            "NX_CHAR"]

    ## map of Python:Tango types
    pTt={"int":"DevLong64", "float":"DevDouble", "str":"DevString"}

    ## map of NEXUS : pninx types 
    mt={"NX_FLOAT32":"float32","NX_FLOAT64":"float64","NX_FLOAT":"float64","NX_NUMBER":"float64","NX_INT":"int64","NX_INT64":"int64","NX_INT32":"int32","NX_UINT64":"uint64","NX_UINT32":"uint32","NX_DATE_TIME":"string","NX_CHAR":"string","NX_BOOLEAN":"int32"}

    ## map of tag attribute types 
    dA={"signal":"NX_INT","axis":"NX_INT","primary":"NX_INT32","offset":"NX_INT","stride":"NX_INT","vector":"NX_FLOATVECTOR",
        "file_time":"NX_DATE_TIME","file_update_time":"NX_DATE_TIME","restricted":"NX_INT","ignoreExtraGroups":"NX_BOOLEAN",
        "ignoreExtraFields":"NX_BOOLEAN","ignoreExtraAttributes":"NX_BOOLEAN","minOccus":"NX_INT","maxOccus":"NX_INT"


        }

    ## map of rank : data format
    rTf={0:"SCALAR",1:"SPECTRUM",2:"IMAGE"}

    ## array rank
    # \brief It calculates the rank of the array
    # \param array given array
    def arrayRank(self,array) :
        rank=0
        print "array:",array
        if isinstance(array,Iterable) and not isinstance(array,str):       
            rank=1+self.arrayRank(array[0])
        return rank            


    ## array rank ,inverse shape and type
    # \brief It calculates the rank, inverse shape and type of the first element of the array
    # \param array given array
    def arrayRankRShape(self,array):        
        rank=0
        shape=[]
        dtype=None
        if isinstance(array,Iterable) and not isinstance(array,str):
            rank,shape,dtype=self.arrayRankRShape(array[0])
            shape.append(len(array))
            rank=rank+1
        else:
           dtype=type(array)
        return (rank,shape,dtype)            
