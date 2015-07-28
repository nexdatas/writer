#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \file InnerXMLParser.py
# An example of SAX Nexus parser

""" SAX parser for taking XML string inside specified tag """

from xml import sax

import sys
import os


## SAX2 parser
class InnerXMLHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser handler for taking xml od datasources
    def __init__(self, xmlReader, contentHandler, name, attrs):
        sax.ContentHandler.__init__(self)
        ## xml string
        self.xml = None
        ## external contentHandler
        self.__contentHandler = contentHandler
        ## external xmlreader
        self.__xmlReader = xmlReader
        ## tag depth
        self.__depth = 1
        ## first tag
        self.__preXML = self.__openTag(name, attrs, eol=False)
        ## last tag
        self.__postXML = "</%s>" % name
        ## tag content
        self.__contentXML = ""

    ## replaces characters not allowed in xml string
    # \param string text
    # \returns converted text with special characters
    @classmethod
    def __replace(cls, string):
        return string.replace("&", "&amp;").\
            replace("<", "&lt;").replace(">", "&gt;")

    ## replaces characters not allowed in  xml attribute values
    # \param string text
    # \returns converted text with special characters
    def __replaceAttr(self, string):
        return self.__replace(string).replace("\"", "&quot;").\
            replace("'", "&apos;")

    ## creates opening tag
    # \param name tag name
    # \param attrs tag attributes
    def __openTag(self, name, attrs, eol=False):
        xml = ""
        if eol:
            xml += "\n<%s" % name
        else:
            xml += "<%s" % name

        for k in attrs.keys():
            xml += " %s=\"%s\"" % (k, self.__replaceAttr(attrs[k]))
        if eol:
            xml += ">\n"
        else:
            xml += ">"
        return xml

    ## parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
        self.__depth += 1
        self.__contentXML += self.__openTag(name, attrs)

    ## adds the tag content
    # \param content partial content of the tag
    def characters(self, content):
        self.__contentXML += self.__replace(content)

    ## parses an closing tag
    # \param name tag name
    def endElement(self, name):
        self.__depth -= 1
        if self.__depth == 0:
            self.xml = (self.__preXML, self.__contentXML, self.__postXML)
            self.__xmlReader.setContentHandler(self.__contentHandler)
        else:
            self.__contentXML += "</%s>" % name


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print "usage: InnerXMLParser.py  <XMLinput>"

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
