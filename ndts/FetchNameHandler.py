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
# \file FetchNameHandler.py
# An example of SAX Nexus parser
try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx
from xml import sax

import sys, os
import Streams

from Errors import  XMLSyntaxError

    
## SAX2 parser 
class FetchNameHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser handler for fetching group names
    def __init__(self):
        sax.ContentHandler.__init__(self)

        ## map of NXclass : name
        self.groupTypes = {"":""}

        ## stack with open tag type attributes
        self.__tstack = []
        ## stack with open tag name attributes
        self.__nstack = []
        ## stack with open tag names
        self.__stack = []
        ## name of attribute tag
        self.__attrName = "" 
        ## content of attribute tag
        self.__content = []
        
        self.__attribute = False

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
            self.__tstack.append(ttype)
            self.__nstack.append(tname)
            self.__stack.append(name)
        elif name == "attribute" and self.__stack[-1] == "group":
            self.__content = []
            self.__attribute = True
            if "name" in attrs.keys() and attrs["name"] in ["name", "type"]:
                self.__attrName = attrs["name"]

    ## adds the tag content 
    # \param ch partial content of the tag    
    def characters(self, ch):
        if self.__attribute and self.__stack[-1] == "group":
            self.__content.append(ch)



    ## parses an closing tag
    # \param name tag name
    def endElement(self, name):
        if name  == "group" :
            if self.__tstack[-1] and self.__nstack[-1]:
                self.groupTypes[self.__tstack[-1]] = self.__nstack[-1]
            elif self.__tstack[-1] and len(self.__tstack[-1]) > 2:
                self.groupTypes[self.__tstack[-1]] = self.__tstack[-1][2:]
                
            else:
                if Streams.log_error:
                    print >> Streams.log_error, "FetchNameHandler::endElement() - The group type not defined"
                raise XMLSyntaxError, "The group type not defined"        
            self.__tstack.pop()
            self.__nstack.pop()
            self.__stack.pop()
                
                
        if name == "attribute"  and self.__stack[-1] == "group":
            if self.__attrName :
                content = ("".join(self.__content)).strip()        
                if content:
                    if self.__attrName == "name":
                        self.__nstack[-1] = content
                    if self.__attrName == "type":
                        self.__tstack[-1] = content
            
            self.__attribute = False
            self.__content = []
            self.__attrName = None
            
            




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
    
