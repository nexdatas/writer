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
## \file Element.py
# Element
                                                                      

## Tag element stored on our stack 
class Element(object):

    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last=None):
        ## stored tag name
        self.tagName = name
        ## tag attributes
        self._tagAttrs = attrs
        ## stored tag content
        self.content = []
        ## doc string
        self.doc = ""
        ## the previous element
        self._last = last


    ## last H5 file object
    # \returns H5 file object of the previous element    
    def _lastObject(self):
        if hasattr(self._last, "h5Object"):
            return self._last.h5Object
        else:
            print "H5 Object not found :", self.tagName


    ## before last stack element
    # \returns  before last element placed on the stack
    def _beforeLast(self):
        if self._last:
            return self._last._last
        else:
            return None

        
    ## stores the tag
    # \brief abstract method to store the tag element    
    # \param xml tuple of xml code    
    def store(self, xml = None):
        pass
