#!/usr/bin/env python3
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
# \file NexusXMLHandler.py
# An example of SAX Nexus parser

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


## SAX2 parser
class NexusXMLHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser and defines the H5 output file
    # \param fileElement file element
    # \param decoders decoder pool
    # \param datasources datasource pool
    # \param groupTypes map of NXclass : name
    # \param parser instance of sax.xmlreader
    # \param globalJSON global json string
    def __init__(self, fileElement, datasources=None, decoders=None,
                 groupTypes=None, parser=None, globalJSON=None):
        sax.ContentHandler.__init__(self)

        ## map of NXclass : name
        self.__groupTypes = TNObject()
        ## if name fetching required
        self.__fetching = True
        if groupTypes:
            self.__groupTypes = groupTypes
            self.__fetching = False

        ## stack with open tag elements
        self.__stack = [fileElement]

        ## unsupported tag tracer
        self.__unsupportedTag = ""
        ## True if raise exception on unsupported tag
        self.raiseUnsupportedTag = True

        ## xmlreader
        self.__parser = parser
        self.__innerHandler = None

        self.__json = globalJSON

        ## tags with innerxml as its input
        self.withXMLinput = {'datasource': DataSourceFactory,
                             'doc': EDoc}
        ##  stored attributes
        self.__storedAttrs = None
        ##  stored name
        self.__storedName = None

        ## map of tag names to related classes
        self.elementClass = {
            'group': EGroup, 'field': EField,
            'attribute': EAttribute, 'link': ELink,
            'symbols': Element, 'symbol': ESymbol,
            'dimensions': EDimensions, 'dim': EDim,
            'enumeration': Element, 'item': Element,
            'strategy': EStrategy
        }

        ## transparent tags
        self.transparentTags = ['definition']

        ## thread pool with INIT elements
        self.initPool = ThreadPool()
        ## thread pool with STEP elements
        self.stepPool = ThreadPool()
        ## thread pool with FINAL elements
        self.finalPool = ThreadPool()

        ## map of pool names to related classes
        self.__poolMap = {'INIT': self.initPool,
                          'STEP': self.stepPool,
                          'FINAL': self.finalPool}
        ## collection of thread pool with triggered STEP elements
        self.triggerPools = {}

        ## pool with decoders
        self.__decoders = decoders

        ## pool with datasources
        self.__datasources = datasources

        ## if innerparse was running
        self.__inner = False

    ## the last stack element
    # \returns the last stack element
    def __last(self):
        if self.__stack:
            return self.__stack[-1]
        else:
            return None

    ## adds the tag content
    # \param content partial content of the tag
    def characters(self, content):
        if self.__inner is True:
            self.__createInnerTag(self.__innerHandler.xml)
            self.__inner = False
        if not self.__unsupportedTag:
            self.__last().content.append(content)

    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
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

    ## parses the closing tag
    # \param name tag name
    def endElement(self, name):
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

    ## addding to pool
    # \param res strategy or (strategy, trigger)
    def __addToPool(self, res, task):
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

    ## creates class instance of the current inner xml
    # \param xml inner xml
    def __createInnerTag(self, xml):
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

    ## closes the elements
    # \brief It goes through all stack elements closing them
    def close(self):
        for s in self.__stack:
            if isinstance(s, FElement) and not isinstance(s, EFile):
                if hasattr(s.h5Object, "close") and callable(s.h5Object.close):
                    s.h5Object.close()


if __name__ == "__main__":

    if len(sys.argv) < 3:
        print("usage: NexusXMLHandler.py  <XMLinput>  <h5output>")

    else:
        ## input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):
            ## output h5 file
            fo = sys.argv[2]

            ## a parser object
            mparser = sax.make_parser()

            ## file  handle
            nxFile = nx.create_file(fo, overwrite=True).root()
            ## element file objects
            mfileElement = EFile([], None, nxFile)
            ## a SAX2 handler object
            mhandler = NexusXMLHandler(mfileElement)
            mparser.setContentHandler(mhandler)

            mparser.parse(open(fi))
            mhandler.close()
            nxFile.close()
