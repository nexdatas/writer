#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxswriter nexdatas
## \file FieldArray.py
# FieldArray

""" splits string arrays to one dimensional ones """

import numpy

from . import Streams

from .Types import NTP
from .Errors import CorruptedFieldArrayError


## Array of the attributes
class AttributeArray(object):
    ## constructor
    # \param parents parent object
    # \param name name of the attribute array
    # \param dtype type of the attribute array
    def __init__(self, parents, name, dtype):
        ## parents
        self.__parents = parents
        ## name of the attribute array
        self.name = name
        ## name of the array type
        self.dtype = dtype
        ## list of attributes
        self.__aObject = []
        for f in parents:
            self.__aObject.append(f.attr(name, dtype))
        
    ## gets the value
    # \returns the value from the first attribute object        
    def __getvalue(self):
        if self.__aObject:
            return self.__aObject[0].value

    ## sets the value
    # \param value value to be set to all attribute objects
    def __setvalue(self, value):
        for a in self.__aObject:
            a.value = value

    ## attribute value       
    value = property(__getvalue, __setvalue, 
                     doc = 'attribute value')            

    
        
                                                                  

## Array of the string fields
class FieldArray(object):

    ## constructor
    # \param parent parent object
    # \param name name of the field array
    # \param dtype type of the field array
    # \param shape shape of the field array
    # \param chunk chunk of the field array
    def __init__(self, parent, name, dtype, shape, chunk = None):
        ## name of the field array
        self.name = name
        ## type of the field array
        self.dtype = dtype
        ## shape
        self.shape = tuple(shape)
        ## chunk
        self.chunk = chunk
        ## parent
        self.__parent = parent
        ##  list of fields
        self.__fList = []
        ## attribute array
        self.__aArray = {}
        ## flatten dimensions
        self.__fdim = len(shape)-1


        if self.__fdim < 1:
            self.__fList.append(
                parent.create_field(name.encode(), 
                                    dtype.encode(), self.shape))

        elif self.__fdim == 1:
            if self.shape[1] == 1:
                self.__fList.append(
                    parent.create_field(name.encode(),
                                        dtype.encode(), [self.shape[0]]))
            else:
                for i in range(self.shape[1]):
                    self.__fList.append(
                        parent.create_field(name.encode()+"_"+str(i),
                                            dtype.encode(), [self.shape[0]]))
        elif self.__fdim == 2:
            if self.shape[1] == 1 and self.shape[2] == 1 :
                self.__fList.append(
                    parent.create_field(name.encode(),
                                        dtype.encode(), [self.shape[0]]))
            
            else:
                for i in range(self.shape[1]):
                    for j in range(self.shape[2]):
                        self.__fList.append(
                            parent.create_field(
                                name.encode()+"_"+str(i)+"_"+str(j),
                                dtype.encode(), [self.shape[0]]))
        
        
    
    ## access to attrributes Array    
    # \param name name of the attribute
    # \param dtype type of the attribute
    def attr(self, name, dtype):
        if name not in self.__aArray :
            self.__aArray[name] = AttributeArray(self.__fList, name, dtype)
        return self.__aArray[name]

    ## fetches ranges from the field shape and key
    # \param key slice object
    # \returns 
    def __fetchRanges(self, key):
        mkey = key
        
        if hasattr(key, "__iter__"):
            mkey = key
        else:
            mkey = [key]

        while mkey < len(self.shape):
            mkey.append(slice(0, self.shape[len(mkey)], 1))
            
        kr = None
        ir = None
        jr = None
            
        if len(self.shape) >0 :
            kr = (range(self.shape[0])[mkey[0]])
            if isinstance(kr, int):  
                kr = [kr]
        if len(self.shape) >1 :
            ir = (range(self.shape[1])[mkey[1]])
            if isinstance(ir, int):  
                ir = [ir]
        if len(self.shape) >2 :
            jr = (range(self.shape[2])[mkey[2]])
            if isinstance(jr, int):  
                jr = [jr]
        
        return kr, ir, jr
            
            

    ## gets item
    # \param key slice object
    def __getitem__(self, key):

        kr, ir, jr = self.__fetchRanges(key)
            

        if self.__fdim == 0:
            return numpy.array(
                [self.__fList[0].__getitem__(k) for k in kr])
        elif self.__fdim == 1: 
            return numpy.array(
                [[self.__fList[i].__getitem__(k) for i  in ir] for k in kr])
        elif self.__fdim == 2:
            return numpy.array(
                [[[self.__fList[i*self.shape[2]+j].__getitem__(k)  
                   for j  in jr] for i  in ir] for k in kr])
        else: 
            return None
           
            
    ## sets item
    # \param key slice object
    # \param value assigning value
    def __setitem__(self, key, value):
        
        if not self.__fList:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "FieldArray::__setitem__() - Field list without elements"

            raise CorruptedFieldArrayError, \
                "Field list without elements"

        kr, ir, jr = self.__fetchRanges(key)

        ntp = NTP()    
        rank = ntp.arrayRank(value)            

        if self.__fdim < 1 :
            if type(value).__name__ == 'str':
                self.__fList[0].__setitem__(kr[0], value)
            else:
                for k in range(len(value)):
                    self.__fList[0].__setitem__(kr[k], value[k])
        elif self.__fdim == 1:
            if rank == 2:
                for i in range(len(value[0])):
                    for k in range(len(value)):
                        self.__fList[ir[i]].__setitem__(kr[k], value[k][i])
            elif rank == 1 :
                if len(ir) == 1:
                    for k in range(len(value)):
                        self.__fList[ir[0]].__setitem__(kr[k], value[k])
                if len(kr) == 1:
                    for i in range(len(value)):
                        self.__fList[ir[i]].__setitem__(kr[0], value[i])
            elif rank == 0 and len(ir) == 1 and len(kr) == 1:
                self.__fList[ir[0]].__setitem__(kr[0], value)
        
        elif self.__fdim == 2:
            if rank == 3:
                for k in range(len(value)):
                    for i in range(len(value[0])):
                        for j in range(len(value[0][0])):
                            self.__fList[
                                ir[i]*self.shape[2]+jr[j]
                                ].__setitem__(kr[k], value[k][i][j])

            elif rank == 2:
                if len(kr) == 1:
                    for i in range(len(value)):
                        for j in range(len(value[0])):
                            if hasattr(value[i][j],"encode"):
                                self.__fList[
                                    ir[i]*self.shape[2]+jr[j]
                                    ][kr[0]] = value[i][j].encode()
                            else:
                                self.__fList[
                                    ir[i]*self.shape[2]+jr[j]
                                    ][kr[0]] = value[i][j]
                elif len(ir) == 1 :        
                    for k in range(len(value)):
                        for j in range(len(value[0])):
                            self.__fList[
                                ir[0]*self.shape[2]+jr[j]
                                ].__setitem__(kr[k], value[k][j])
                elif len(jr) == 1 :        
                    for k in range(len(value)):
                        for i in range(len(value[0])):
                            self.__fList[
                                ir[i]*self.shape[2]+jr[0]
                                ].__setitem__(kr[k], value[k][i])

            elif rank == 1:            
                if len(kr) == 1 and len(ir) == 1:
                    for j in range(len(value)):
                        self.__fList[
                            ir[0]*self.shape[2]+jr[j]
                            ].__setitem__(kr[0], value[j])
                if len(kr) == 1 and len(jr) == 1:
                    for i in range(len(value)):
                        self.__fList[
                            ir[i]*self.shape[2]+jr[0]
                            ].__setitem__(kr[0], value[i])
                if len(ir) == 1 and len(jr) == 1:
                    for k in range(len(value)):
                        self.__fList[
                            ir[0]*self.shape[2]+jr[0]
                            ].__setitem__(kr[k], value[k])
            elif rank == 0:
                self.__fList[
                    ir[0]*self.shape[2]+jr[0]
                    ].__setitem__(kr[0], value)

                    

                    
        
    ## stores the field value
    # \param value the stored value
    def write(self, value):
        key = []
        for k in range(len(self.shape)):
            key.append(slice(0, self.shape[k], 1))

        if key:
            self.__setitem__(key, value)
        else:
            self.__fList[0].write( value)
            


    ## reads the field value
    # \brief It reads the whole field array
    def read(self):
        key = []
        for k in range(len(self.shape)):
            key.append(slice(0, self.shape[k], 1))
        if key:
            return self.__getitem__(key)
        else:
            return self.__fList[0].read()

    ## growing method
    # \brief It enlage the field
    # \param dim growing dimension
    # \param ext a number of grow units    
    def grow(self, dim=0, ext=1):
        if dim:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "FieldArray::grow() - dim >0  not supported"
            raise ValueError, \
                "dim >0  not supported by FieldArray.grow "
        for f in self.__fList:
            f.grow(dim, ext)
        shape = list(self.shape)    
        if shape:
            shape[dim] = shape[dim] + ext
        else:
            shape = [1 + ext]
        self.shape = tuple(shape)

    ## closing method
    # \brief It closes all fields from the array    
    def close(self):
        for f in self.__fList:
            f.close()

        

        
