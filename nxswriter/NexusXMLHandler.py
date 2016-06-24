#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

""" SAX parser for interpreting content of  XML configuration string """

import pni.io.nx.h5 as nx
from xml import sax

import sys
import os

from . import Streams

from .Element import Element
from .FElement import FElement
from .EGroup import EGroup
from .EField import EField
from .EAttribute import EAttribute
from .EStrategy import EStrategy
from .ELink import ELink
from .H5Elements import (
    EDoc, ESymbol, EDimensions, EDim, EFile)
from .DataSourceFactory import DataSourceFactory
from .ThreadPool import ThreadPool
from .InnerXMLParser import InnerXMLHandler
from .Errors import UnsupportedTagError
from .FetchNameHandler import TNObject


class NexusXMLHandler(sax.ContentHandler):
    """ SAX2 parser
    """

    def __init__(self, fileElement, datasources=None, decoders=None,
                 groupTypes=None, parser=None, globalJSON=None):
        """ constructor

        :brief: It constructs parser and defines the H5 output file
        :param fileElement: file element
        :type fileElement: :obj:`H5Elements.EFile`
        :param decoders: decoder pool
        :type decoders: :obj:`DecoderPool.DecoderPool`
        :param datasources: datasource pool
        :type datasources: :obj:`DataSourcePool.DataSourcePool`
        :param groupTypes: map of NXclass : name
        :type groupTypes: :obj:`TNObject`
        :param parser: instance of sax.xmlreader
        :type parser: :obj:`xml.sax.xmlreader.XMLReader`
        :param globalJSON: global json string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        sax.ContentHandler.__init__(self)

        #: (:obj:`TNObject`) map of NXclass : name
        self.__groupTypes = TNObject()
        #: (:obj:`bool`) if name fetching required
        self.__fetching = True
        if groupTypes:
            self.__groupTypes = groupTypes
            self.__fetching = False

        #: (:obj:`list` <:obj:`Element.Element`>) stack with open tag elements
        self.__stack = [fileElement]

        #: (:obj:`str`) traced unsupported tag name
        self.__unsupportedTag = ""
        #: (:obj:`bool`) True if raise exception on unsupported tag
        self.raiseUnsupportedTag = True

        #: (:obj:`xml.sax.xmlreader.XMLReader`) xmlreader
        self.__parser = parser
        #: (:obj:`InnerXMLHandler.InnerXMLHandler`) inner xml handler
        self.__innerHandler = None

        #: (:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>) \
        #:    global json string
        self.__json = globalJSON

        #: (:obj:`dict` <:obj:`str`: :obj:`Element.Element` > ) \
        #:     tags with inner xml as its input
        self.withXMLinput = {'datasource': DataSourceFactory,
                             'doc': EDoc}
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) stored attributes
        self.__storedAttrs = None
        #: (:obj:`str`) stored name
        self.__storedName = None

        #: (:obj:`dict` <:obj:`str`: :obj:`__class__` > ) \
        #: map of tag names to related classes
        self.elementClass = {
            'group': EGroup, 'field': EField,
            'attribute': EAttribute, 'link': ELink,
            'symbols': Element, 'symbol': ESymbol,
            'dimensions': EDimensions, 'dim': EDim,
            'enumeration': Element, 'item': Element,
            'strategy': EStrategy
        }

        #: (:obj:`list` <:obj:`str`>) transparent tags
        self.transparentTags = ['definition']

        #: (:obj:`ThreadPool.ThreadPool`) thread pool with INIT elements
        self.initPool = ThreadPool()
        #: (:obj:`ThreadPool.ThreadPool`) thread pool with STEP elements
        self.stepPool = ThreadPool()
        #: (:obj:`ThreadPool.ThreadPool`) thread pool with FINAL elements
        self.finalPool = ThreadPool()

        #: (:obj:`dict` <:obj:`str`, :obj:`ThreadPool.ThreadPool`> ) \
        #:    map of pool names to related classes
        self.__poolMap = {'INIT': self.initPool,
                          'STEP': self.stepPool,
                          'FINAL': self.finalPool}
        #: (:obj:`dict` <:obj:`str`, :obj:`ThreadPool.ThreadPool`> ) \
        #:     collection of thread pool with triggered STEP elements
        self.triggerPools = {}

        #: (:obj:`DecoderPool.DecoderPool`) pool with decoders
        self.__decoders = decoders

        #: (:obj:`DataSourcePool.DataSourcePool`) pool with datasources
        self.__datasources = datasources

        #: (:obj:`bool`) if innerparse was running
        self.__inner = False

    def __last(self):
        """ the last stack element

        :returns: the last stack element
        :rtype: :obj:`Element.Element`
        """
        if self.__stack:
            return self.__stack[-1]
        else:
            return None

    def characters(self, content):
        """ adds the tag content

        :param content: partial content of the tag
        :type content: :obj:`str`
        """
        if self.__inner is True:
            self.__createInnerTag(self.__innerHandler.xml)
            self.__inner = False
        if not self.__unsupportedTag:
            self.__last().content.append(content)

    def startElement(self, name, attrs):
        """ parses the opening tag

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: attribute dictionary
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        """
        if self.__inner is True:
            if hasattr(self.__innerHandler, "xml"):
                self.__createInnerTag(self.__innerHandler.xml)
            self.__inner = False
        if not self.__unsupportedTag:
            if self.__parser and name in self.withXMLinput:
                self.__storedAttrs = attrs
                self.__storedName = name
                self.__innerHandler = InnerXMLHandler(
                    self.__parser, self, name, attrs)
                self.__parser.setContentHandler(self.__innerHandler)
                self.__inner = True
            elif name in self.elementClass:
                self.__stack.append(
                    self.elementClass[name](attrs, self.__last()))
            elif name not in self.transparentTags:
                if self.raiseUnsupportedTag:
                    Streams.error(
                        "NexusXMLHandler::startElement() - "
                        "Unsupported tag: %s, %s "
                        % (name, attrs.keys()),
                        std=False)

                    raise UnsupportedTagError("Unsupported tag: %s, %s "
                                              % (name, attrs.keys()))
                Streams.warn(
                    "NexusXMLHandler::startElement() - "
                    "Unsupported tag: %s, %s " % (name, attrs.keys()))

                self.__unsupportedTag = name

    def endElement(self, name):
        """ parses the closing tag

        :param name: tag name
        :type name: :obj:`str`
        """
        if self.__inner is True:
            self.__createInnerTag(self.__innerHandler.xml)
            self.__inner = False
        if not self.__unsupportedTag and self.__parser \
                and name in self.withXMLinput:
            pass
        elif not self.__unsupportedTag and name in self.elementClass:
            if hasattr(self.__last(), "store") \
                    and callable(self.__last().store):
                res = self.__last().store()
                if res:
                    self.__addToPool(res, self.__last())
            if hasattr(self.__last(), "createLink") and \
               callable(self.__last().createLink):
                self.__last().createLink(self.__groupTypes)
            self.__stack.pop()
        elif name not in self.transparentTags:
            if self.__unsupportedTag == name:
                self.__unsupportedTag = ""

    def __addToPool(self, res, task):
        """ addding to pool

        :param res: strategy or (strategy, trigger)
        :type res: :obj:`str` or (:obj:`str`, :obj:`str`)
        :param task: Element with inner xml
        :type task: :obj:`Element.Element`
        """
        trigger = None
        strategy = None
        if res:
            if hasattr(res, "__iter__"):
                strategy = res[0]
                if len(res) > 1:
                    trigger = res[1]
            else:
                strategy = res

        if trigger and strategy == 'STEP':
            if trigger not in self.triggerPools.keys():
                self.triggerPools[trigger] = ThreadPool()
            self.triggerPools[trigger].append(task)
        elif strategy in self.__poolMap.keys():
            self.__poolMap[strategy].append(task)

    def __createInnerTag(self, xml):
        """ creates class instance of the current inner xml

        :param xml: inner xml
        :type xml: :obj:`str`
        """
        if self.__storedName in self.withXMLinput:
            res = None
            inner = self.withXMLinput[self.__storedName](
                self.__storedAttrs, self.__last())
            if hasattr(inner, "setDataSources") \
                    and callable(inner.setDataSources):
                inner.setDataSources(self.__datasources)
            if hasattr(inner, "store") and callable(inner.store):
                res = inner.store(xml, self.__json)
            if hasattr(inner, "setDecoders") and callable(inner.setDecoders):
                inner.setDecoders(self.__decoders)
            if res:
                self.__addToPool(res, inner)

    def close(self):
        """ closes the elements

        :brief: It goes through all stack elements closing them
        """
        for s in self.__stack:
            if isinstance(s, FElement) and not isinstance(s, EFile):
                if hasattr(s.h5Object, "close") and callable(s.h5Object.close):
                    s.h5Object.close()


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("usage: NexusXMLHandler.py  <XMLinput>  <h5output>")

    else:
        #: (:obj:`str`) input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):
            #: (:obj:`str`) output h5 file
            fo = sys.argv[2]

            #: (:obj:`xml.sax.xmlreader.XMLReader`) parser object
            mparser = sax.make_parser()

            #: (:obj:`pni.io.nx.h5._nxh5.nxfile`) file handle
            nxFile = nx.create_file(fo, overwrite=True).root()
            #: (:object:`H5Elements.EFile`) element file objects
            mfileElement = EFile([], None, nxFile)
            #: (:obj:`NexusXMLHandler`) SAX2 handler object
            mhandler = NexusXMLHandler(mfileElement)
            mparser.setContentHandler(mhandler)

            mparser.parse(open(fi))
            mhandler.close()
            nxFile.close()
