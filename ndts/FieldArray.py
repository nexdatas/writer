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

## Array of the attributes
class AttributeArray:
    ## constructor
    # \param parent parent object
    # \param fName name of the field array
    # \param fType type of the field array
    def __init__(self, parents, aName , aType):
        ## parent
        self.parent = parent
        ## name of the attribute array
        self.name = aName
        ## name of the array type
        self.type = fType
        ## shape
        self.aObject=[]
        for f in parents:
            self.aObject.append(f.attr(aName,aType))
        
    
    ##  gets the attribute
    # \param name attribute name    
    def __getattr__(self, name):
        if name == 'value':
            return self.aObject[0].value
        else:
            raise AttributeError

    ##  sets the attribute
    # \param name attribute name    
    # \param value attribute value
    def __setattr__(self, name, value):
        if name == 'value':
            for a in self.aObject:
                a.value=value
        else:
            raise AttributeError
        
                                                                  

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
        

    
    ## access to attrributes Array    
    # \param aName name of the attribute
    # \param aType type of the attribute
    def attr(self,aName,aType):
        if not self.aArray:
            self.aArray=AttributeArray(self.fList, fName , fType, fShape)
        return self.aArray

    ## gets item
    # \param key slice object
    def __getitem__(self, key):
        pass

    ## sets item
    # \param key slice object
    # \param value assigning value
    def __setitem__(self, key, value):
        pass
        
    ## stores the field value
    # \param value the stored value
    def write(self,value):
        pass
    
    ## growing method
    # \brief It enlage the field
    def grow(self,ln=1,dim=0):
        for f in fList:
            f.grow(ln,dim)
    

    ## closing method
    # \brief It closes all fields from the array    
    def close(self):
        for f in fList:
            f.close()

        

        
