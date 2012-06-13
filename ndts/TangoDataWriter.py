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
## \file TangoDataWriter.py
# NeXuS H5 Data Writer
#


from NexusXMLHandler import *

import pni.nx.h5 as nx

from numpy  import * 
from xml import sax

import sys,os
from H5Elements import *



## NeXuS data writer
class TangoDataWriter:
    ## constructor
    # \brief It initialize the data writer for the H5 output file
    # \param fName name of the H5 output file
    def __init__(self,fName):
        ## output file name
        self.fileName=fName
        ## XML string with file settings
        self.xmlSettings=""
        ## JSON string with data settings
        self.json="{}"
        ## thread pool with INIT elements
        self.initPool=None
        ## thread pool with STEP elements
        self.stepPool=None
        ## thread pool with FINAL elements
        self.finalPool=None
        ## H5 file handle
        self.nxFile=None

    ##  opens the data writer
    # \brief It parse the XML settings, creates thread pools and runs the INIT pool.
    def open(self):
        print 'open:'
        if len(self.xmlSettings)>0:
            parser = sax.make_parser()
        
            handler = NexusXMLHandler(self.fileName)
            sax.parseString(self.xmlSettings,handler)
            
            self.initPool=handler.initPool.setJSON(self.json)
            self.stepPool=handler.stepPool.setJSON(self.json)
            self.finalPool=handler.finalPool.setJSON(self.json)
            
            self.initPool.runAndWait()
            self.nxFile=handler.getNXFile()

            
    ## defines the XML string with settings
    # \param xmlSettings XML string       
    def setXML(self,xmlSettings):
        self.xmlSettings=xmlSettings
        print 'setXML'

    ## provides the XML setting string
    # \returns the XML string with settings
    def getXML(self):
        print 'getXML'
        return self.xmlSettings

    ## defines the JSON data string 
    # \param json JSON data string 
    def setJSON(self,json):
        self.json=json
        print 'setJSON'

    ## provides the JSON data string
    # \returns the JSON data string 
    def getJSON(self):
        print 'getJSON'
        return self.json

    ## close the data writer        
    # \brief It runs threads from the STEP pool
    def record(self):
        print 'record:'
        if self.stepPool:
            self.stepPool.runAndWait()


    ## closes the data writer        
    # \brief It runs threads from the FINAL pool and
    #  removes the thread pools 
    def close(self):
        print 'close:'


        if self.finalPool:
            self.finalPool.runAndWait()


        if self.initPool:
            self.initPool.close()
            

        if self.stepPool:
            self.stepPool.close()
                
        if self.finalPool: 
            self.finalPool.close()

        self.initPool=None
        self.stepPool=None
        self.finalPool=None



        if self.nxFile:
            self.nxFile.close()
        
        self.nxFile=None



if __name__ == "__main__":

    import time

    # Create a TDW object
    ## instance of TangoDataWriter
    tdw = TangoDataWriter("test.h5")

    ## xml file name
#    xmlf="../XMLExamples/test.xml"
    xmlf="../XMLExamples/MNI.xml"

    print "usage: TangoDataWriter.py  <XMLfile>  <H5file>"

    if len(sys.argv)>2:
        tdw.fileName=sys.argv[2]
    if len(sys.argv)>1:
        xmlf=sys.argv[1]

    ## xml string    
    xml = open(xmlf, 'r').read()
    tdw.setXML(xml)

    tdw.open()
    
    print "recording H5 file"
    tdw.record()
    
    print "sleeping for 1s"
    time.sleep(1)
    print "recording H5 file"
    tdw.record()
    print "sleeping for 1s"
    time.sleep(1)
    print "recording H5 file"
    tdw.record()
    print "closing H5 file"
    tdw.close()
            
                
    
