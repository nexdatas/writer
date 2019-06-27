#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
#

""" SAX parser for taking XML string inside specified tag """

from xml import sax
import weakref


class InnerXMLHandler(sax.ContentHandler):

    """ Inner SAX2 parser
    """

    def __init__(self, xmlReader, contentHandler, name, attrs):
        """ constructor

        :brief: It constructs parser handler for taking xml of datasources
        :param xmlReader: NeXus xml sax reader
        :type xmlReader: :class:`xml.sax.xmlreader.XMLReader`
        :param contentHandler: NeXus XML content handler
        :type contentHandler: \
              :class:`nxswriter.NexusXMLHandler.NexusXMLHandler`
        :param name: tag name
        :type name: :obj:`str`
        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        """
        sax.ContentHandler.__init__(self)
        #: (:obj:`str`) xml string
        self.xml = None
        #: (:class:`nxswriter.NeXusXMLHandler.NeXusXMLHandler`) \
        #:       external contentHandler
        self.__contentHandler = weakref.ref(contentHandler)
        #: (:class:`xml.sax.xmlreader.XMLReader`) external xmlreader
        self.__xmlReader = weakref.ref(xmlReader)
        #: (:obj:`int`) tag depth
        self.__depth = 1
        #: (:obj:`str`) first tag
        self.__preXML = self.__openTag(name, attrs, eol=False)
        #: (:obj:`str`) last tag
        self.__postXML = "</%s>" % name
        #: (:obj:`str`) tag content
        self.__contentXML = ""

    @classmethod
    def __replace(cls, string):
        """ replaces characters not allowed in xml string

        :param string: text
        :type string: :obj:`str`
        :returns: converted text with special characters
        :rtype: :obj:`str`
        """
        return string.replace("&", "&amp;").\
            replace("<", "&lt;").replace(">", "&gt;")

    def __replaceAttr(self, string):
        """ replaces characters not allowed in  xml attribute values

        :param string: text
        :type string: :obj:`str`
        :returns: converted text with special characters
        :rtype: :obj: `str`
        """
        return self.__replace(string).replace("\"", "&quot;").\
            replace("'", "&apos;")

    def __openTag(self, name, attrs, eol=False):
        """ creates opening tag

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: tag attributes
        """
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

    def startElement(self, name, attrs):
        """ parses the opening tag

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: attribute dictionary
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        """
        self.__depth += 1
        self.__contentXML += self.__openTag(name, attrs)

    def characters(self, content):
        """ adds the tag content

        :param content: partial content of the tag
        :type content: :obj:`str`
        """
        self.__contentXML += self.__replace(content)

    def endElement(self, name):
        """ parses an closing tag

        :param name: tag name
        :type name: :obj:`str`
        """
        self.__depth -= 1
        if self.__depth == 0:
            self.xml = (self.__preXML, self.__contentXML, self.__postXML)
            self.__xmlReader().setContentHandler(self.__contentHandler())
        else:
            self.__contentXML += "</%s>" % name
