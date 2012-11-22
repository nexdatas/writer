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
# \file NexusXMLHandler.py
# An example of SAX Nexus parser
import pni.nx.h5 as nx
from xml import sax

import sys, os

from Element import Element
from H5Elements import (EGroup, EField, EAttribute, ELink, EDoc, ESymbol, EDimensions, EDim, EStrategy)
from DataSource import DataSourceFactory
from ThreadPool import ThreadPool
from collections import Iterable
from InnerXMLParser import InnerXMLHandler

## unsupported tag exception
class UnsupportedTagError(Exception): pass
    
## SAX2 parser 
class NexusXMLHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser and defines the H5 output file
    # \param fileElement file element
    # \param decoders decoder pool
    # \param groupTypes map of NXclass : name
    # \param parser instance of sax.xmlreader
    def __init__(self, fileElement, decoders=None, groupTypes=None , parser = None):
        sax.ContentHandler.__init__(self)

        
        ## map of NXclass : name 
        self._groupTypes = {"":""}
        ## if name fetching required
        self._fetching = True
        if groupTypes:
            self._groupTypes = groupTypes
            self._fetching = False

        ## stack with open tag elements
        self._stack = [fileElement]

        ## unsupported tag tracer
        self._unsupportedTag=""
        self._raiseUnsupportedTag=True

        ## xmlreader
        self._parser = parser
        self._innerHander = None

        ## tags with innerxml as its input
        self._withXMLinput = {'datasource':DataSourceFactory, 'doc':EDoc}
        ##  stored attributes
        self._storedAttrs = None
        ##  stored name
        self._storedName = None

        ## map of tag names to related classes
        self._elementClass = {'group':EGroup, 'field':EField, 'attribute':EAttribute,
                              'link':ELink,
                              'symbols':Element, 'symbol':ESymbol, 
                              'dimensions':EDimensions, 
                              'dim':EDim, 'enumeration':Element, 'item':Element,
                              'strategy':EStrategy
                              }

        ## transparent tags
        self._transparentTags = ['definition']


        ## thread pool with INIT elements
        self.initPool = ThreadPool()
        ## thread pool with STEP elements
        self.stepPool = ThreadPool()
        ## thread pool with FINAL elements
        self.finalPool = ThreadPool()

        ## map of pool names to related classes
        self._poolMap = {'INIT':self.initPool, 'STEP':self.stepPool, 'FINAL':self.finalPool}        
        ## collection of thread pool with triggered STEP elements
        self.triggerPools = {}

        ## pool with decoders
        self._decoders = decoders

        ## if innerparse was running
        self._inner = False

    ## the last stack element 
    # \returns the last stack element 
    def _last(self):
        if self._stack : 
            return self._stack[-1]
        else:
            return None


    ## adds the tag content 
    # \param ch partial content of the tag    
    def characters(self, ch):
        if self._inner == True:
#            print "XML:\n", self._innerHandler.xml
            self._createInnerTag(self._innerHandler.xml)
            self._inner = False
        if not self._unsupportedTag:
            self._last().content.append(ch)


    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
        if self._inner == True:
            print "XML:\n", self._innerHandler.xml
            self._createInnerTag(self._innerHandler.xml)
            self._inner = False
        if not self._unsupportedTag :
            if self._parser and  name in self._withXMLinput:
                self._storedAttrs = attrs
                self._storedName = name
                self._innerHandler = InnerXMLHandler(self._parser, self, name, attrs)
                self._parser.setContentHandler(self._innerHandler) 
                self._inner = True
            elif name in self._elementClass:
                self._stack.append(self._elementClass[name](name, attrs, self._last()))
                if self._fetching and hasattr(self._last(), "fetchName") and callable(self._last().fetchName):
                    self._last().fetchName(self._groupTypes)
                if hasattr(self._last(), "setDecoders") and callable(self._last().setDecoders):
                    self._last().setDecoders(self._decoders)
                if hasattr(self._last(), "createLink") and callable(self._last().createLink):
                    self._last().createLink(self._groupTypes)
            elif name not in self._transparentTags:
                if self._raiseUnsupportedTag:
                    raise UnsupportedTagError, "Unsupported tag: %s, %s " % ( name, attrs.keys())
                print "Unsupported tag: ", name ,attrs.keys()
                self._unsupportedTag = name
                

    ## parses an closing tag
    # \param name tag name
    def endElement(self, name):
        if self._inner == True:
            print "XML:\n", self._innerHandler.xml
            self._createInnerTag(self._innerHandler.xml)
            self._inner = False
        if not self._unsupportedTag and self._parser and  name in self._withXMLinput:
            print "innerxml"
            print "XML", self._innerHandler.xml
        elif not self._unsupportedTag and name in self._elementClass:
            res = self._last().store()
            if res:
                self._addToPool(res, self._last())
            self._stack.pop()
        elif name not in self._transparentTags:
            if self._unsupportedTag == name:
                self._unsupportedTag = ""


    ## addding to pool
    # \param res strategy or (strategy, trigger)
    def _addToPool(self, res, task):
            trigger = None
            strategy = None
            if res:
                if isinstance(res, Iterable):
                    strategy = res[0]
                    if len(res)>1 :
                        trigger = res[1]
                else:
                    strategy = res
        
            if trigger and strategy == 'STEP':
                if trigger not in self.triggerPools.keys():
                    self.triggerPools[trigger]=ThreadPool()
                self.triggerPools[trigger].append(task)
            elif strategy in self._poolMap.keys():
                self._poolMap[strategy].append(task)
                

   
    ## creates class instance of the current inner xml
    # \param xml inner xml
    def _createInnerTag(self, xml):
        if self._storedName in self._withXMLinput:
            inner = self._withXMLinput[self._storedName](self._storedName, self._storedAttrs, self._last())
            res = inner.store(xml)
            if res:
                self._addToPool(res, inner)

            
                

    ## closes the elements
    # \brief It goes through all stack elements closing them
    def close(self):
        for s in self._stack:
            if isinstance(s, FElement) and not isinstance(s, EFile):
                if hasattr(s.h5Object, "close") and callable(s.h5Object.close):
                    s.h5Object.close()
 



if __name__ == "__main__":

    if  len(sys.argv) <3:
        print "usage: simpleXMLtoh5.py  <XMLinput>  <h5output>"
        
    else:
        ## input XML file
        fi = sys.argv[1]
        if os.path.exists(fi):
            ## output h5 file
            fo = sys.argv[2]

            ## a parser object
            parser = sax.make_parser()
            
            ## file  handle
            nxFile = nx.create_file(self.self.fileName, overwrite=True)
            ## element file objects
            fileElement = EFile("NXfile", [], None, self.nxFile)
            ## a SAX2 handler object
            handler = NexusXMLHandler(fileElement)
            parser.setContentHandler(handler)

            parser.parse(open(fi))
            handler.close()
            nxFile.close()
    
