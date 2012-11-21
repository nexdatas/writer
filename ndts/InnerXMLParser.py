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
# \file InnerXMLParser.py
# An example of SAX Nexus parser
import pni.nx.h5 as nx
from xml import sax

import sys, os


## exception for syntax in XML settings
class XMLSyntaxError(Exception): pass

    
## SAX2 parser 
class InnerXMLHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser handler for fetching group names
    def __init__(self, xmlReader, contentHandler):
        sax.ContentHandler.__init__(self)
        ## xml string       
        self.xml = ""
        ## external contentHandler
        self._contentHandler = contentHandler
        ## external xmlreader
        self._xmlReader = xmlReader 
        ## tag depth
        self._depth = 1

    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
        self._depth +=1 
        self.xml += "< %s "% name
        for k in attrs.keys():
            self.xml += " %s  = \"%s\"" % (k, attrs[k].replace("\"","&quot;"))
        self.xml += " > "

    ## adds the tag content 
    # \param ch partial content of the tag    
    def characters(self, ch):
        self.xml += ch


    ## parses an closing tag
    # \param name tag name
    def endElement(self, name):
        self._depth -=1 
        if self._depth == 0:
            self._xmlReader.setContentHandler(self._contentHandler)
            print "E:", self.xml
        else:
            self.xml += "</ %s >" % name 
            
            
           




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
            handler = InnerXMLHandler()
            parser.setContentHandler(handler)

            parser.parse(open(fi))
            print "GT:", handler.xml
    
