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
## \package ndts nexdatas
# \file NexusXMLHandler.py
# An example of SAX Nexus parser
import pni.nx.h5 as nx
from xml import sax

import sys,os

from H5Elements import *
from ThreadPool import *


    
## SAX2 parser 
class NexusXMLHandler(sax.ContentHandler):

    ## constructor
    # \brief It constructs parser and defines the H5 output file
    # \param fname name of the H5 output file
    def __init__(self,fname):
        sax.ContentHandler.__init__(self)

        ## map of NXclass : name
        self.groupTypes={"":""}
        ## H5 file name
        self.fname=fname
        ## file handle
        self.nxFile=nx.create_file(self.fname,overwrite=True)
        ## stack with open tag elements
        self.stack=[EFile("NXfile",[],None,self.nxFile)]

        ## the current content of the tag 
        self.content=""

        ## map of tag names to related classes
        self.elementClass={'group':EGroup, 'field':EField, 'attribute':EAttribute,
                           'link':ELink, 'doc':EDoc,
                           'symbols':Element, 'symbol':ESymbol, 
                           'dimensions':EDimensions, 
                           'dim':EDim, 'enumeration':Element, 'item':Element,
                           'datasource':DataSourceFactory,'record':ERecord , 'query':EQuery, 
                           'device':EDevice, 'door':EDoor}



        ## thread pool with INIT elements
        self.initPool=ThreadPool()
        ## thread pool with STEP elements
        self.stepPool=ThreadPool()
        ## thread pool with FINAL elements
        self.finalPool=ThreadPool()

        ## map of pool names to related classes
        self.poolMap={'INIT':self.initPool,'STEP':self.stepPool,'FINAL':self.finalPool}

    ## PNINX file object of the last stack element
    # \returns an object from the last stack element 
    #    
    def lastObject(self):
        if len(self.stack) > 0: 
            return self.stack[-1].fObject
        else:
            return None
        

    ## the last stack element 
    # \returns the last stack element 
    def last(self):
        if len(self.stack) > 0: 
            return self.stack[-1]
        else:
            return None

    ## the before last stack element 
    # \returns the before last stack element 
    def beforeLast(self):
        if len(self.stack) > 0: 
            return self.stack[-2]
        else:
            return None


    ## adds the tag content 
    # \param ch partial content of the tag    
    def characters(self, ch):
        self.last().content.append(ch)

    ##  parses the opening tag
    # \param name tag name
    # \param attrs attribute dictionary
    def startElement(self, name, attrs):
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


    ## parses an closing tag
    # \param name tag name
    def endElement(self, name):
        print 'End of element:', name , "last:" ,  self.last().tName
        if self.last().tName == name :
            if name in self.elementClass:
                print "Closing: ", name
                strategy=self.last().store(name)

                if strategy in self.poolMap.keys():
                    print "adding to pool"
                    self.poolMap[strategy].append(self.last())
                print 'Content:' , "".join(self.last().content)    
                print "poping"
                self.stack.pop()

    ## the H5 file handle 
    # \returns the H5 file handle 
    def getNXFile(self):
        return self.nxFile            

    ## closes the stack
    # \brief It goes through all stack elements closing them
    def closeStack(self):
        for s in self.stack:
            if isinstance(s, FElement):
                if hasattr(s.fObject,"close"):
                    s.fObject.close()
        if self.nxFile:
            print "nxClosing the stack"
            self.nxFile.close()
 
    ## the H5 file closing
    # \brief It closes the H5 file       
    def closeFile(self):
        self.closeStack()
        if self.nxFile:
            print "nxClosing NXFile"
            self.nxFile.close()



if __name__ == "__main__":

    if  len(sys.argv) <3:
        print "usage: simpleXMLtoh5.py  <XMLinput>  <h5output>"
        
    else:
        ## input XML file
        fi=sys.argv[1]
        if os.path.exists(fi):
            ## output h5 file
            fo=sys.argv[2]

            ## a parser object
            parser = sax.make_parser()
            
            ## a SAX2 handler object
            handler = NexusXMLHandler(fo)
            parser.setContentHandler( handler )

            parser.parse(open(fi))
            handler.closeFile()
    
