#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""@package docstring
@file NexusXMLHandler.py
An example of SAX Nexus parser
"""
                                                                      
import pni.nx.h5 as nx

from numpy  import * 
from xml import sax

import sys,os
from H5Elements import *

from ThreadPool import *


    
class NexusXMLHandler(sax.ContentHandler):
    """A SAX2 parser  """
    def __init__(self,fname):
        """ Constructor """
        sax.ContentHandler.__init__(self)
        ## A map of NXclass : name
        self.groupTypes={"":""}
        ## An H5 file name
        self.fname=fname
        self.nxFile=nx.create_file(self.fname,overwrite=True)
        ## A stack with open tag elements
        self.stack=[EFile("NXfile",[],None,self.nxFile)]


        self.elementClass={'group':EGroup, 'field':EField, 'attribute':EAttribute,
                           'link':ELink, 'doc':EDoc,
                           'symbols':Element, 'symbol':ESymbol, 
                           'dimensions':EDimensions, 
                           'dim':EDim, 'enumeration':Element, 'item':Element,
                           'datasource':DataSourceFactory,'record':ERecord }

#                           'definition':Element, 

        self.symbols={}

        self.initPool=ThreadPool()
        self.stepPool=ThreadPool()
        self.finalPool=ThreadPool()

        self.poolMap={'INIT':self.initPool,'STEP':self.stepPool,'FINAL':self.finalPool}


        
    def nWS(text):
        """  cleans whitespaces  """
        return ' '.join(text.split())
        
    def lastObject(self):
        """  returns an object from the last stack elements """
        if len(self.stack) > 0: 
            return self.stack[-1].fObject
        else:
            return None
        

    def last(self):
        """  returns the last stack elements """
        if len(self.stack) > 0: 
            return self.stack[-1]
        else:
            return None

    def beforeLast(self):
        """  returns the last stack elements """
        if len(self.stack) > 0: 
            return self.stack[-2]
        else:
            return None


    def characters(self, ch):
        """  adds the tag content """
        self.last().content.append(ch)

    def startElement(self, name, attrs):
        """  parses an opening tag"""
        self.content=""
        if name in self.elementClass:
            print "Calling: ", name, attrs.keys()
            print "MYType" , type(self.last())
            self.stack.append(self.elementClass[name](name, attrs, self.last()))
            if hasattr(self.last(),"fetchName"):
                self.last().fetchName(self.groupTypes)
            if hasattr(self.last(),"createLink"):
                self.last().createLink(self.groupTypes)
        else:
            print 'Unsupported tag:', name, attrs.keys()


    def endElement(self, name):
        """  parses an closing tag"""
        print 'End of element:', name , "last:" ,  self.last().tName
        if self.last().tName == name :
            if name in self.elementClass:
                print "Closing: ", name
                strategy=self.last().store(name)
                if strategy:
                    print "strategy", strategy
                if strategy in self.poolMap.keys():
                    print "adding to pool"
                    self.poolMap[strategy].append(self.last())
                print 'Content:' , "".join(self.last().content)    
                print "poping"
                self.stack.pop()

    def getNXFile(self):
        return self.nxFile            

    def closeStack(self):
        """  closes the H5 file """
        for s in self.stack:
            if isinstance(s, FElement):
                if hasattr(s.lastObject(),"close"):
                    s.lastObject().close()
        if self.nxFile:
            print "nxClosing"
            self.nxFile.close()


    def closeFile(self):
        """  closes the H5 file """
        self.closeStack()
        if self.nxFile:
            print "nxClosing"
            self.nxFile.close()



if __name__ == "__main__":

    if  len(sys.argv) <3:
        print "usage: simpleXMLtoh5.py  <XMLinput>  <h5output>"
        
    else:
        fi=sys.argv[1]
        if os.path.exists(fi):
            fo=sys.argv[2]

        # Create a parser object
            parser = sax.make_parser()
            
            handler = NexusXMLHandler(fo)
            parser.setContentHandler( handler )

            parser.parse(open(fi))
            handler.closeFile()
    
