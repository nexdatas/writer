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

from numpy import * 
from collections import Iterable

from Types import *

## Array of the attributes
class AttributeArray(object):
    ## constructor
    # \param parents parent object
    # \param aName name of the field array
    # \param aType type of the field array
    def __init__(self, parents, aName , aType):
        ## parents
        
        self.parents = parents
        ## name of the attribute array
        self.name = aName
        ## name of the array type
        self.type = aType
        ## shape
        self.aObject=[]
        for f in parents:
            self.aObject.append(f.attr(aName,aType))
        
    ## gets the value
    # \returns the value from the first attribute object        
    def getvalue(self):
        if len(self.aObject)>0:
            return self.aObject[0].value

    ## sets the value
    # \param value value to be set to all attribute objects
    def setvalue(self,value):
        for a in self.aObject:
            a.value=value

    value=property(getvalue,setvalue)            

    
        
                                                                  

## Array of the string fields
class FieldArray:

    ## constructor
    # \param parent parent object
    # \param fName name of the field array
    # \param fType type of the field array
    # \param fShape shape of the field array
    def __init__(self, parent, fName , fType, fShape):
        ## parent
        self.parent = parent
        ## name of the field array
        self.name = fName
        ## type of the field array
        self.dtype = fType
        ## shape
        self.shape = fShape
        ##  list of fields
        self.fList = []
        ## attribute array
        self.aArray = None
        ## flatten dimensions
        self.fdim=len(fShape)-1
        if self.fdim < 1:
            self.fList.append(parent.create_field(fName.encode(),fType.encode(),self.shape))
        elif self.fdim == 1:
            if self.shape[1] == 1:
                self.fList.append(parent.create_field(fName.encode(),
                                                      fType.encode(),[self.shape[0]]))
            else:
                for i in range(self.shape[1]):
                    self.fList.append(parent.create_field(fName.encode()+"_"+str(i),
                                                          fType.encode(),[self.shape[0]]))
        elif self.fdim == 2:
            if self.shape[1] == 1 and self.shape[2] == 1 :
                self.fList.append(parent.create_field(fName.encode(),
                                                      fType.encode(),[self.shape[0]]))
            
            else:
                for i in range(self.shape[1]):
                    for j in range(self.shape[2]):
                        self.fList.append(parent.create_field(fName.encode()+"_"+str(i)+"_"+str(j),
                                                              fType.encode(),[self.shape[0]]))
        
            
        

    
    ## access to attrributes Array    
    # \param aName name of the attribute
    # \param aType type of the attribute
    def attr(self,aName,aType):
        if not self.aArray:
            self.aArray=AttributeArray(self.fList, aName , aType)
        return self.aArray

    ## gets item
    # \param key slice object
    def __getitem__(self, key):

        mkey=key
        
        if isinstance(key, Iterable):
            mkey=key
        else:
            mkey=[key]

        while mkey < len(self.shape):
            mkey.append(slice(0,self.shape[len(mkey)],1))

        if len(self.shape) >0 :
            kr=(range(self.shape[0])[mkey[0]])
            if isinstance(kr,int):  kr =[kr]
        if len(self.shape) >1 :
            ir=(range(self.shape[1])[mkey[1]])
            if isinstance(ir,int):  ir =[ir]
        if len(self.shape) >2 :
            jr=(range(self.shape[2])[mkey[2]])
            if isinstance(jr,int):  jr =[jr]
            
        if self.fdim == 0:
            return numpy.array([self.fList[0].__getitem__(k) for k in kr])
        elif self.fdim == 1:
            return numpy.array([[self.fList[k].__getitem__(i) for i  in ir] for k in kr])
        elif self.fdim == 2:
            return numpy.array([[[self.fList[i*len(self.shape(2))+j].__getitem__(k)  
                                for j  in jr] for i  in ir] for k in kr])
        else: 
            return None
           
            
    ## sets item
    # \param key slice object
    # \param value assigning value
    def __setitem__(self, key, value):
        
        if len(self.fList)<1:
            raise "array Field without elements"

        mkey=key
        
        if isinstance(key, Iterable):
            mkey=key
        else:
            mkey=[key]

        while mkey < len(self.shape):
            mkey.append(slice(0,self.shape[len(mkey)],1))

        ntp=NTP()    
        rank=ntp.arrayRank(value)            


        if len(self.shape) >0 :
            kr=(range(self.shape[0])[mkey[0]])
            if isinstance(kr,int):  kr =[kr]
        if len(self.shape) >1 :
            ir=(range(self.shape[1])[mkey[1]])
            if isinstance(ir,int):  ir =[ir]
        if len(self.shape) >2 :
            jr=(range(self.shape[2])[mkey[2]])
            if isinstance(jr,int):  jr =[jr]

        if self.fdim < 1 :
            for k in range(len(value)):
                self.fList[0].__setitem__(kr[k],value[k])
        elif self.fdim == 1:
            if rank == 2:
                for i in range(len(value[0])):
                    for k in range(len(value)):
                        self.fList[ir[i]].__setitem__(kr[k],value[k][i])
            elif rank == 1 :
                if len(ir) == 1:
                    for k in range(len(value)):
                        self.fList[ir[0]].__setitem__(kr[k],value[k])
                if len(kr) == 1:
                    for i in range(len(value)):
                        self.fList[ir[i]].__setitem__(kr[0],value[i])
            elif rank == 0 and len(ir) == 1 and len(kr) == 1:
                self.fList[ir[0]].__setitem__(kr[0],value)
        
        elif self.fdim == 2:
            if rank == 3:
                for k in range(len(value)):
                    for i in range(len(value[0])):
                        for j in range(len(value[0,0])):
                            self.fList[ir[i]*self.shape[2]+jr[j]].__setitem__([kr[k]],value[k][i][j])

            elif rank == 2:
                if len(kr) == 1:
                        for i in range(len(value)):
                            for j in range(len(value[0])):
                                self.fList[ir[i]*self.shape[2]+jr[j]][kr[0]]=value[i][j].encode()
                elif len(ir) == 1 :        
                    for k in range(len(value)):
                        for j in range(len(value[0])):
                            self.fList[ir[0]*self.shape[2]+jr[j]].__setitem__(kr[k],value[k][j])
                elif len(jr) == 1 :        
                    for k in range(len(value)):
                        for i in range(len(value[0])):
                            self.fList[ir[i]*self.shape[2]+jr[0]].__setitem__(kr[k],value[k][i])

            elif rank == 1:            
                if len(kr) == 1 and len(ir) == 1:
                        for j in range(len(value)):
                            self.fList[ir[0]*self.shape[2]+jr[j]].__setitem__(kr[0],value[j])
                if len(kr) == 1 and len(jr) == 1:
                        for i in range(len(value)):
                            self.fList[ir[i]*self.shape[2]+jr[0]].__setitem__(kr[0],value[i])
                if len(ir) == 1 and len(jr) == 1:
                    for k in range(len(value)):
                        self.fList[ir[0]*self.shape[2]+jr[0]].__setitem__(kr[k],value[k])
            elif rank == 0:
                    self.fList[ir[0]*self.shape[2]+jr[0]].__setitem__(kr[0],value)

                    

                    
        
    ## stores the field value
    # \param value the stored value
    def write(self,value):
        key=[]
        for k in range(len(self.shape)):
            key.append(slice(0,self.shape[k],1))

        if len(key)>0:
            elf.__setitem__(key,value)


    ## reads the field value
    # \brief It reads the whole field array
    def read(self):
        key=[]
        for k in range(len(self.shape)):
            key.append(slice(0,self.shape[k],1))

        if len(key)>0:
            return self.__getitem__(key)
    
                    
    ## growing method
    # \brief It enlage the field
    def grow(self,dim=0,ln=1):
        for f in self.fList:
            f.grow(dim,ln)
        self.shape[dim]=self.shape[dim]+ln
    

    ## closing method
    # \brief It closes all fields from the array    
    def close(self):
        for f in self.fList:
            f.close()

        

        
