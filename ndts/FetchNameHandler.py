#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \file FetchNameHandler.py
# An example of SAX Nexus parser
import pni.nx.h5 as nx
from xml import sax

import sys, os


## exception for syntax in XML settings
class XMLSyntaxError(Exception): pass

    
## SAX2 parser 
class FetchNameHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser handler for fetching group names
    def __init__(self):
        sax.ContentHandler.__init__(self)

        ## map of NXclass : name
        self.groupTypes = {"":""}

        ## stack with open tag type attributes
        self._tstack = []
        ## stack with open tag name attributes
        self._nstack = []
        ## stack with open tag names
        self._stack = []
        ## name of attribute tag
        self._attrName = "" 
        ## content of attribute tag
        self._content = []
        
        self._attribute = False

    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
        ttype = ""
        tname = ""
        
        
        if name  == "group":
            if "type" in attrs.keys():
                ttype = attrs["type"]
            if "name" in attrs.keys():
                tname = attrs["name"]
            self._tstack.append(ttype)
            self._nstack.append(tname)
            self._stack.append(name)
        elif name == "attribute" and self._stack[-1] == "group":
            self._content = []
            self._attribute = True
            if "name" in attrs.keys() and attrs["name"] in ["name", "type"]:
                self._attrName = attrs["name"]

    ## adds the tag content 
    # \param ch partial content of the tag    
    def characters(self, ch):
        if self._attribute and self._stack[-1] == "group":
            self._content.append(ch)



    ## parses an closing tag
    # \param name tag name
    def endElement(self, name):
        if name  == "group" :
            if self._tstack[-1] and self._nstack[-1]:
                self.groupTypes[self._tstack[-1]] = self._nstack[-1]
            elif self._tstack[-1] and len(self._tstack[-1]) > 2:
                self.groupTypes[self._tstack[-1]] = self._tstack[-1][2:]
                
            else:
                 raise XMLSyntaxError, "The group type not defined"        
            self._tstack.pop()
            self._nstack.pop()
            self._stack.pop()
                
                
        if name == "attribute"  and self._stack[-1] == "group":
            if self._attrName :
                content = ("".join(self._content)).strip()        
                if content:
                    if self._attrName == "name":
                        self._nstack[-1] = content
                    if self._attrName == "type":
                        self._tstack[-1] = content
            
            self._attribute = False
            self._content = []
            self._attrName = None
            
            




if __name__ == "__main__":

    if  len(sys.argv) <2:
        print "usage: FetchNameHadler.py  <XMLinput>"
        
    else:
        ## input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):

            ## a parser object
            parser = sax.make_parser()
            
            ## a SAX2 handler object
            handler = FetchNameHandler()
            parser.setContentHandler(handler)

            parser.parse(open(fi))
            print "GT:", handler.groupTypes
    
