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
## \package nxswriter nexdatas
## \file EStrategy.py
# NeXus runnable elements

""" Definitions of strategy evaluation classes """

import sys

from .Element import Element
from . import Streams


## query tag element        
class EStrategy(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "strategy", attrs, last)

        if "mode" in attrs.keys():
            self.last.strategy = attrs["mode"]
        if "trigger" in attrs.keys():
            self.last.trigger = attrs["trigger"]
            if Streams.log_info:
                print >> Streams.log_info, "TRIGGER" , attrs["trigger"]
            else:
                print >> sys.stdout,  "TRIGGER" , attrs["trigger"]
        if "grows" in attrs.keys() and hasattr(self.last,"grows"):
            self.last.grows = int(attrs["grows"])
            if self.last.grows < 1:
                self.last.grows = 1
        if "canfail" in attrs.keys():
            self.last.canfail = True \
                if attrs["canfail"].upper() == "TRUE" else False
        if "compression" in attrs.keys() and hasattr(self.last,"compression"):
            self.last.compression = True \
                if attrs["compression"].upper() == "TRUE" else False
            if self.last.compression:
                if "rate" in attrs.keys() and hasattr(self.last,"rate"):
                    self.last.rate = int(attrs["rate"])
                    if self.last.rate < 0:
                        self.last.rate = 0
                    if self.last.rate > 9:
                        self.last.rate = 9
                if "shuffle" in attrs.keys() and hasattr(self.last,"shuffle"):
                    self.last.shuffle = False \
                        if attrs["shuffle"].upper() == "FALSE" else True
                
            


    ## stores the tag content
    # \param xml xml setting 
    # \param globalJSON global JSON string
    def store(self, xml = None, globalJSON = None):
        self.last.postrun = ("".join(self.content)).strip()   
