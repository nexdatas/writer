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
## \file H5Elements.py
# NeXus runnable elements

""" Definitions of tag evaluation classes """

import sys

import numpy

from .DataHolder import DataHolder
from .Element import Element
from .FElement import FElement
from .FieldArray import FieldArray
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)
from . import Streams

import pni.io.nx.h5 as nx


## file H5 element        
class EFile(FElement):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    # \param h5fileObject H5 file object
    def __init__(self, attrs, last, h5fileObject):
        FElement.__init__(self, "file", attrs, last, h5fileObject)



## doc tag element        
class EDoc(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "doc", attrs, last)

    ## stores the tag content
    # \param xml xml setting
    # \param globalJSON global JSON string
    def store(self, xml = None, globalJSON = None):
        if self._beforeLast():
            self._beforeLast().doc +=  "".join(xml[1])            


## symbol tag element        
class ESymbol(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "symbol", attrs, last)
        ## dictionary with symbols
        self.symbols = {}

    ## stores the tag content
    # \param xml xml setting2
    # \param globalJSON global JSON string
    def store(self, xml = None, globalJSON = None):
        if "name" in self._tagAttrs.keys():
            self.symbols[self._tagAttrs["name"]] = self.last.doc


 
## dimensions tag element        
class EDimensions(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "dimensions", attrs, last)
        if "rank" in attrs.keys():
            self.last.rank = attrs["rank"]


## dim tag element        
class EDim(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "dim", attrs, last)
        if ("index"  in attrs.keys()) and  ("value"  in attrs.keys()) :
            self._beforeLast().lengths[attrs["index"]] = attrs["value"]


