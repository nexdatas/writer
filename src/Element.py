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
"""@package docstring
@file Element.py
"""
                                                                      

class Element:
    """A tag element stored on our stack  """
    def __init__(self,name,attrs,last=None):
        """ Constructor """
        ## Stored tag name
        self.tName=name
        self.tAttrs=attrs
        ## Stored tag content
        self.doc=""
        self.content=[]
        self.last=last


    def lastObject(self):
        if hasattr(self.last,"fObject"):
            return self.last.fObject
        else:
            print "H5 Object not found  "
            None

    def beforeLast(self):
        if self.last:
            return self.last.last
        else:
            return None

        
    def store(self,name):
        pass
