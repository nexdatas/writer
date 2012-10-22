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
from H5Elements import (EGroup, EField, EAttribute,
                        ELink, EDoc, ESymbol, EDimensions, EDim, 
                              ERecord, EStrategy ,EQuery, 
                              EDatabase, EDevice, EDoor)
from DataSource import DataSourceFactory
from ThreadPool import ThreadPool
from collections import Iterable


## unsupported tag exception
class UnsupportedTagError(Exception): pass
    
## SAX2 parser 
class NexusXMLHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser and defines the H5 output file
    # \param fileElement file element
    def __init__(self, fileElement):
        sax.ContentHandler.__init__(self)

        ## map of NXclass : name
        self._groupTypes = {"":""}

        ## stack with open tag elements
        self._stack = [fileElement]

        ## unsupported tag tracer
        self._unsupportedTag=""
        self._raiseUnsupportedTag=True


        ## map of tag names to related classes
        self._elementClass = {'group':EGroup, 'field':EField, 'attribute':EAttribute,
                              'link':ELink, 'doc':EDoc,
                              'symbols':Element, 'symbol':ESymbol, 
                              'dimensions':EDimensions, 
                              'dim':EDim, 'enumeration':Element, 'item':Element,
                              'datasource':DataSourceFactory, 'record':ERecord,'strategy':EStrategy , 'query':EQuery, 
                              'database':EDatabase, 
                              'device':EDevice, 'door':EDoor}

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
        if not self._unsupportedTag:
            self._last().content.append(ch)

    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
        if not self._unsupportedTag :
            if name in self._elementClass:
                self._stack.append(self._elementClass[name](name, attrs, self._last()))
                if hasattr(self._last(), "fetchName") and callable(self._last().fetchName):
                    self._last().fetchName(self._groupTypes)
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
        if not self._unsupportedTag and name in self._elementClass:
#            if self._last().tagName == name :
            res = self._last().store(name)
            trigger = None
            strategy = None
            if res :
                if isinstance(res, Iterable):
                    strategy = res[0]
                    if len(res)>1 :
                        trigger = res[1]
                else:
                    strategy = res
        
            if trigger and strategy == 'STEP':
                if trigger not in self.triggerPools.keys():
                    self.triggerPools[trigger]=ThreadPool()
                self.triggerPools[trigger].append(self._last())
            elif strategy in self._poolMap.keys():
                self._poolMap[strategy].append(self._last())
            self._stack.pop()
        elif name not in self._transparentTags:
            if self._unsupportedTag == name:
                self._unsupportedTag = ""
   
            

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
    
