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
## \file FieldArray.py
# FieldArray

from numpy import *

## Array of the attributes
class AttributeArray:
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
        
    
    ##  gets the attribute
    # \param name attribute name    
    def __getattr__(self, name):
        if name == 'value':
            return self.aObject[0].value
        elif name in self.__dict__.keys():
            return self.__dict__[name]
        else:
            print "getattr: ", name 
            raise AttributeError

    ##  sets the attribute
    # \param name attribute name    
    # \param value attribute value
    def __setattr__(self, name, value):
        if name == 'value':
            for a in self.aObject:
                a.value=value
        else:
            self.__dict__[name] = value        
            print "setattr: ", name , value
#            raise AttributeError
        
                                                                  

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
            for i in range(self.shape[1]):
                self.fList.append(parent.create_field(fName.encode()+"_"+str(i),
                                                      fType.encode(),[self.shape[0]]))
        elif self.fdim == 2:
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
        if len(self.shape) >0 :
            kr=(range(self.shape[0])[key[0]])
            if isinstance(kr,int):  kr =[kr]
        if len(self.shape) >1 :
            ir=(range(self.shape[1])[key[1]])
            if isinstance(ir,int):  ir =[ir]
        if len(self.shape) >2 :
            jr=(range(self.shape[2])[key[2]])
            if isinstance(jr,int):  ir =[jr]


        if len(kr) == 1:
            return self.fList[kr[0]].__getitem__(key[1:-1])            
        else:
            return numpy.array([self.fList[kr[k]].__getitem__(key[1:-1]) for k in kr])
            
    ## sets item
    # \param key slice object
    # \param value assigning value
    def __setitem__(self, key, value):
#        print "key:", key 
#        print "value:", value 
#        print "fdim:", self.fdim
#        print "shape", self.shape
#        print "len fList", len(self.fList)
        


        rank=0
        arlist=(list,tuple,ndarray)
 #       print "first type:", type(value)
        if isinstance(value,arlist):
            rank=rank+1
 #           print "secound type:", type(value[0])
            if len(value) > 0 and isinstance(value[0],arlist):
                rank=rank+1
                if len(value[0]) > 0 and isinstance(value[0,0],arlist):
                    rank=rank+1
 #       print "rank: ", rank

        if len(self.shape) >0 :
            kr=(range(self.shape[0])[key[0]])
            if isinstance(kr,int):  kr =[kr]
        if len(self.shape) >1 :
            ir=(range(self.shape[1])[key[1]])
            if isinstance(ir,int):  ir =[ir]
        if len(self.shape) >2 :
            jr=(range(self.shape[2])[key[2]])
            if isinstance(jr,int):  ir =[jr]
            print "kr:", kr
            print "ir:", ir
            print "jr:", jr
         
        
        
        if self.fdim < 1:
            self.fList[0].__setitem__(key,value)
        elif self.fdim == 1:
            if rank == 2:
                for i in range[len(value[0])]:
                    self.fList[ir[i]].__setitem__([key[0]],value[:][i])
            elif rank == 1 :
                if len(ir) == 1:
                    self.fList[ir[0]].__setitem__([key[0]],value[:])
                if len(kr) == 1:
                    for i in range[len(value[0])]:
                        self.fList[ir[i]].__setitem__([key[0]],value[i])
            elif rank == 0 and len(ir) == 1 and len(kr) == 1:
                self.fList[ir[0]].__setitem__([key[0]],value)
        
        elif self.fdim == 2:
            if rank == 3:
                for i in range(len(value[0])):
                    for j in range(len(value[0,0])):
                        self.fList[ir[i]*self.shape[2]+jr[j]].__setitem__([key[0]],value[:][i][j])

            elif rank == 2:
                if len(kr) == 1:
                    for i in range(len(value)):
                        for j in range(len(value[0])):

                            print "fL index: ",ir[i]*self.shape[2]+jr[j]
                            print "key: " ,key[0]
                            print "range",range(self.shape[0])
                            print "key shape: " , (range(self.shape[0])[key[0]])
                            print "value: " ,value[i][j]
                            
                            self.fList[ir[i]*self.shape[2]+jr[j]].__setitem__([key[0]],value[i][j])
                elif len(ir) == 1 :        
                    for j in range(len(value[0])):
                        self.fList[ir[0]*self.shape[2]+jr[j]].__setitem__([key[0]],value[:][j])
                elif len(jr) == 1 :        
                    for i in range(len(value[0])):
                        self.fList[ir[i]*self.shape[2]+jr[0]].__setitem__([key[0]],value[:][i])

            elif rank == 1:            
                if len(kr) == 1 and len(ir) == 1:
                        for j in range(len(value )):
                            self.fList[ir[0]*self.shape[2]+jr[j]].__setitem__([key[0]],value[j])
                if len(kr) == 1 and len(jr) == 1:
                        for i in range(len(value )):
                            self.fList[ir[i]*self.shape[2]+jr[0]].__setitem__([key[0]],value[i])
                if len(ir) == 1 and len(jr) == 1:
                    self.fList[ir[0]*self.shape[2]+jr[0]].__setitem__([key[0]],value[:])
            elif rank == 0:
                    self.fList[ir[0]*self.shape[2]+jr[0]].__setitem__([key[0]],value)

                    

                    
        
    ## stores the field value
    # \param value the stored value
    def write(self,value):
        if self.fdim < 1:
            self.fList[0].write(value)
        elif self.fdim == 1:
            for i in range(self.shape[1]):
                self.fList[i].write(value[:][i])
        elif self.fdim == 2:
            for i in range(self.shape[1]):
                for j in range(self.shape[2]):
                    self.fList[i*self.shape[2]+j].write(value[:][i][j])
                    
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

        

        
