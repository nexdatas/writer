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
## \file Element.py
# Element
                                                                      

## Tag element stored on our stack 
class Element:

    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last=None):
        ## Stored tag name
        self.tName=name
        ## tag attributes
        self.tAttrs=attrs
        ## stored tag content
        self.content=[]
        ## doc string
        self.doc=""
        ## the previous element
        self.last=last


    ## last H5 file object
    # \returns H5 file object of the previous element    
    def lastObject(self):
        if hasattr(self.last,"fObject"):
            return self.last.fObject
        else:
            print "H5 Object not found  "
            None


    ## before last stack element
    # \returns  before last element placed on the stack
    def beforeLast(self):
        if self.last:
            return self.last.last
        else:
            return None

        
    ## stores the tag
    # \brief abstract method to store the tag element    
    def store(self,name):
        pass
