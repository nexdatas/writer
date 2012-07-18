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
class TangoDataWriter(object):
    ## constructor
    # \brief It initialize the data writer for the H5 output file
    # \param fileName name of the H5 output file
    def __init__(self, fileName):
        ## output file name
        self.fileName = fileName
        ## XML string with file settings
        self.xmlSettings = ""
        ## global JSON string with data records
        self.json = "{}"
        ## thread pool with INIT elements
        self._initPool = None
        ## thread pool with STEP elements
        self._stepPool = None
        ## thread pool with FINAL elements
        self._finalPool = None
        ## H5 file handle
        self._nxFile = None
        ## maximal number of threads
        self.numThreads = 100
        ## element file objects
        self._eFile = None
       
    ## the H5 file opening
    # \brief It opens the H5 file       
    def openNXFile(self):
        ## file handle
        self._nxFile = nx.create_file(self.fileName, overwrite=True)
        ## element file objects
        self._eFile = EFile("NXfile", [], None, self._nxFile)



    ## the H5 file handle 
    # \returns the H5 file handle 
    def getNXFile(self):
        return self._nxFile            


    ## the H5 file closing
    # \brief It closes the H5 file       
    def closeNXFile(self):
        self._nxFile.close()
        

    ##  opens the data entry corresponding to a new XML settings
    # \brief It parse the XML settings, creates thread pools and runs the INIT pool.
    def openEntry(self):
        if self.xmlSettings:
            parser = sax.make_parser()
        
            handler = NexusXMLHandler(self._eFile)
            sax.parseString(self.xmlSettings, handler)
            
            self._initPool = handler.initPool
            self._stepPool = handler.stepPool
            self._finalPool = handler.finalPool
            
            self._initPool.numThreads = self.numThreads
            self._stepPool.numThreads = self.numThreads
            self._finalPool.numThreads = self.numThreads
           

            self._initPool.setJSON(self.json)
            self._initPool.runAndWait()


    ## close the data writer        
    # \brief It runs threads from the STEP pool
    # \param json local JSON string with data records      
    def record(self,json=None):
        if self._stepPool:
            self._stepPool.setJSON(self.json, json)
            self._stepPool.runAndWait()


    ## closes the data entry        
    # \brief It runs threads from the FINAL pool and
    #  removes the thread pools 
    def closeEntry(self):

        if self._finalPool:
            self._finalPool.setJSON(self.json)
            self._finalPool.runAndWait()


        if self._initPool:
            self._initPool.close()
            

        if self._stepPool:
            self._stepPool.close()
                
        if self._finalPool: 
            self._finalPool.close()

#        if self._nxFile:
#            self._nxFile.flush()

        self._initPool = None
        self._stepPool = None
        self._finalPool = None



        



if __name__ == "__main__":

    import time

    # Create a TDW object
    ## instance of TangoDataWriter
    tdw = TangoDataWriter("test.h5")

    tdw.numThreads = 1

    ## xml file name
#    xmlf = "../XMLExamples/test.xml"
    xmlf = "../XMLExamples/MNI.xml"

    print "usage: TangoDataWriter.py  <XMLfile1>  <XMLfile2>  ...  <XMLfileN>  <H5file>"

    ## No arguments
    argc = len(sys.argv)
    if argc > 2:
        tdw.fileName = sys.argv[argc-1]

    print "opening the H5 file"
    tdw.openNXFile()


    if argc > 1:

        for i in range(1, argc-1):
            xmlf = sys.argv[i]
        
            ## xml string    
            xml = open(xmlf, 'r').read()
            tdw.xmlSettings = xml

            print "opening the data entry "
            tdw.openEntry()
            
            print "recording the H5 file"
            tdw.record()
            
            print "sleeping for 1s"
            time.sleep(1)
            print "recording the H5 file"
            tdw.record()
            print "sleeping for 1s"
            time.sleep(1)
            print "recording the H5 file"
            tdw.record()
            print "closing the data entry "
            tdw.closeEntry()


    print "closing the H5 file"
    tdw.closeNXFile()
            
                
    
