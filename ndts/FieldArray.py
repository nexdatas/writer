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
## \file FieldArray.py
# FieldArray

import numpy

from Types import NTP

## exception for corrupted FieldArray
class CorruptedFieldArray(Exception): pass

## Array of the attributes
class AttributeArray(object):
    ## constructor
    # \param parents parent object
    # \param name name of the attribute array
    # \param dtype type of the attribute array
    def __init__(self, parents, name, dtype):
        ## parents
        
        self._parents = parents
        ## name of the attribute array
        self.name = name
        ## name of the array type
        self.dtype = dtype
        ## list of attributes
        self._aObject = []
        for f in parents:
            self._aObject.append(f.attr(name, dtype))
        
    ## gets the value
    # \returns the value from the first attribute object        
    def _getvalue(self):
        if self._aObject:
            return self._aObject[0].value

    ## sets the value
    # \param value value to be set to all attribute objects
    def _setvalue(self, value):
        for a in self._aObject:
            a.value = value

    ## attribute value       
    value = property(_getvalue, _setvalue)            

    
        
                                                                  

## Array of the string fields
class FieldArray(object):

    ## constructor
    # \param parent parent object
    # \param name name of the field array
    # \param dtype type of the field array
    # \param shape shape of the field array
    def __init__(self, parent, name, dtype, shape):
        ## name of the field array
        self.name = name
        ## type of the field array
        self.dtype = dtype
        ## shape
        self.shape = shape
        ## parent
        self._parent = parent
        ##  list of fields
        self._fList = []
        ## attribute array
        self._aArray = None
        ## flatten dimensions
        self._fdim = len(shape)-1

        if self._fdim < 1:
            self._fList.append(parent.create_field(name.encode(), dtype.encode(), self.shape))
        elif self._fdim == 1:
            if self.shape[1] == 1:
                self._fList.append(parent.create_field(name.encode(),
                                                      dtype.encode(), [self.shape[0]]))
            else:
                for i in range(self.shape[1]):
                    self._fList.append(parent.create_field(name.encode()+"_"+str(i),
                                                          dtype.encode(), [self.shape[0]]))
        elif self._fdim == 2:
            if self.shape[1] == 1 and self.shape[2] == 1 :
                self._fList.append(parent.create_field(name.encode(),
                                                      dtype.encode(), [self.shape[0]]))
            
            else:
                for i in range(self.shape[1]):
                    for j in range(self.shape[2]):
                        self._fList.append(parent.create_field(name.encode()+"_"+str(i)+"_"+str(j),
                                                              dtype.encode(), [self.shape[0]]))
        
            
        

    
    ## access to attrributes Array    
    # \param name name of the attribute
    # \param dtype type of the attribute
    def attr(self, name, dtype):
        if not self._aArray:
            self._aArray = AttributeArray(self._fList, name, dtype)
        return self._aArray

    ## fetches ranges from the field shape and key
    # \param key slice object
    # \returns 
    def _fetchRanges(self, key):
        mkey = key
        
        if hasattr(key, "__iter__"):
            mkey = key
        else:
            mkey = [key]

        while mkey < len(self.shape):
            mkey.append(slice(0,self.shape[len(mkey)], 1))
            
        kr = None
        ir = None
        jr = None
            
        if len(self.shape) >0 :
            kr = (range(self.shape[0])[mkey[0]])
            if isinstance(kr, int):  kr = [kr]
        if len(self.shape) >1 :
            ir = (range(self.shape[1])[mkey[1]])
            if isinstance(ir, int):  ir = [ir]
        if len(self.shape) >2 :
            jr = (range(self.shape[2])[mkey[2]])
            if isinstance(jr, int):  jr = [jr]
        
        return kr, ir, jr
            
            

    ## gets item
    # \param key slice object
    def __getitem__(self, key):

        kr, ir, jr = self._fetchRanges(key)
            
        if self._fdim == 0:
            return numpy.array([self._fList[0].__getitem__(k) for k in kr])
        elif self._fdim == 1:
            return numpy.array([[self._fList[k].__getitem__(i) for i  in ir] for k in kr])
        elif self._fdim == 2:
            return numpy.array([[[self._fList[i*len(self.shape(2))+j].__getitem__(k)  
                                for j  in jr] for i  in ir] for k in kr])
        else: 
            return None
           
            
    ## sets item
    # \param key slice object
    # \param value assigning value
    def __setitem__(self, key, value):
        
        if not self._fList:
            raise CorruptedFieldArray, "Field list without elements"

        kr, ir, jr = self._fetchRanges(key)

        ntp = NTP()    
        rank = ntp.arrayRank(value)            


        if self._fdim < 1 :
            for k in range(len(value)):
                self._fList[0].__setitem__(kr[k], value[k])
        elif self._fdim == 1:
            if rank == 2:
                for i in range(len(value[0])):
                    for k in range(len(value)):
                        self._fList[ir[i]].__setitem__(kr[k], value[k][i])
            elif rank == 1 :
                if len(ir) == 1:
                    for k in range(len(value)):
                        self._fList[ir[0]].__setitem__(kr[k], value[k])
                if len(kr) == 1:
                    for i in range(len(value)):
                        self._fList[ir[i]].__setitem__(kr[0], value[i])
            elif rank == 0 and len(ir) == 1 and len(kr) == 1:
                self._fList[ir[0]].__setitem__(kr[0], value)
        
        elif self._fdim == 2:
            if rank == 3:
                for k in range(len(value)):
                    for i in range(len(value[0])):
                        for j in range(len(value[0,0])):
                            self._fList[ir[i]*self.shape[2]+jr[j]].__setitem__([kr[k]], value[k][i][j])

            elif rank == 2:
                if len(kr) == 1:
                        for i in range(len(value)):
                            for j in range(len(value[0])):
                                self._fList[ir[i]*self.shape[2]+jr[j]][kr[0]] = value[i][j].encode()
                elif len(ir) == 1 :        
                    for k in range(len(value)):
                        for j in range(len(value[0])):
                            self._fList[ir[0]*self.shape[2]+jr[j]].__setitem__(kr[k], value[k][j])
                elif len(jr) == 1 :        
                    for k in range(len(value)):
                        for i in range(len(value[0])):
                            self._fList[ir[i]*self.shape[2]+jr[0]].__setitem__(kr[k], value[k][i])

            elif rank == 1:            
                if len(kr) == 1 and len(ir) == 1:
                        for j in range(len(value)):
                            self._fList[ir[0]*self.shape[2]+jr[j]].__setitem__(kr[0], value[j])
                if len(kr) == 1 and len(jr) == 1:
                        for i in range(len(value)):
                            self._fList[ir[i]*self.shape[2]+jr[0]].__setitem__(kr[0], value[i])
                if len(ir) == 1 and len(jr) == 1:
                    for k in range(len(value)):
                        self._fList[ir[0]*self.shape[2]+jr[0]].__setitem__(kr[k], value[k])
            elif rank == 0:
                    self._fList[ir[0]*self.shape[2]+jr[0]].__setitem__(kr[0], value)

                    

                    
        
    ## stores the field value
    # \param value the stored value
    def write(self, value):
        key = []
        for k in range(len(self.shape)):
            key.append(slice(0, self.shape[k], 1))

        if key:
            elf.__setitem__(key, value)


    ## reads the field value
    # \brief It reads the whole field array
    def read(self):
        key = []
        for k in range(len(self.shape)):
            key.append(slice(0, self.shape[k], 1))

        if key:
            return self.__getitem__(key)
    
                    
    ## growing method
    # \brief It enlage the field
    def grow(self, dim=0,ln=1):
        for f in self._fList:
            f.grow(dim, ln)
        self.shape[dim] = self.shape[dim] + ln
    

    ## closing method
    # \brief It closes all fields from the array    
    def close(self):
        for f in self._fList:
            f.close()

        

        
