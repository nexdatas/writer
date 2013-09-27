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

""" SAX parser for fetching name attributes of tags """

from xml import sax

import sys, os
from . import Streams

from .Errors import  XMLSyntaxError

## Type Name object
class TNObject(object):
    ## constructor
    # \param name name of the object
    # \param nxtype Nexus type of the object
    # \param object parent
    # \brief It sets default values of TNObject
    def __init__(self, name="root", nxtype=None, parent=None):
        ## object name
        self.name = name
        ## object Nexus type
        self.nxtype = nxtype
        ## object parent
        self.parent = parent
        ## object children
        self.children = []

        if hasattr(self.parent,"children"):
            self.parent.children.append(self)

    ## get child by name or nxtype
    def child(self, name='', nxtype=''):
        if name:
            found = None
            for ch in self.children:
                if ch.name == name.strip():
                    found = ch
                    break
            return found   
        elif nxtype:
            found = None
            for ch in self.children:
                if ch.nxtype == nxtype:
                    found = ch
                    break
            return found    
        else:
            if len(self.children)>0:
                return self.children[0]

    
## SAX2 parser 
class FetchNameHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser handler for fetching group names
    def __init__(self):
        sax.ContentHandler.__init__(self)

        ## tree of TNObjects with names and types
        self.groupTypes = TNObject()
        ## current object
        self.__current = self.groupTypes
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
            self.__current = TNObject(tname.strip(), ttype.strip(), 
                                      self.__current)
            self.__stack.append(name)
        elif name == "attribute" and self.__stack[-1] == "group":
            self.__content = []
            self.__attribute = True
            if "name" in attrs.keys() and attrs["name"] in ["name", "type"]:
                self.__attrName = attrs["name"]

    ## adds the tag content 
    # \param content partial content of the tag    
    def characters(self, content):
        if self.__attribute and self.__stack[-1] == "group":
            self.__content.append(content)



    ## parses an closing tag
    # \param name tag name
    def endElement(self, name):
        if name  == "group" :

            if not self.__current.nxtype or not self.__current.name:
                if self.__current.nxtype and len(self.__current.nxtype) > 2:
                    self.__current.name = self.__current.nxtype[2:]
                else:
                    if Streams.log_error:
                        print >> Streams.log_error, \
                            "FetchNameHandler::endElement() - "\
                            "The group type not defined"
                    raise XMLSyntaxError, "The group type not defined"        
            self.__current = self.__current.parent
            self.__stack.pop()
                
                
        if name == "attribute"  and self.__stack[-1] == "group":
            if self.__attrName :
                content = ("".join(self.__content)).strip()        
                if content:
                    if self.__attrName == "name":
                        self.__current.name = content.strip()
                    if self.__attrName == "type":
                        self.__current.nxtype = content.strip()
            
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
    
