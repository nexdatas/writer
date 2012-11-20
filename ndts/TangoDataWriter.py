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


from NexusXMLHandler import NexusXMLHandler
from FetchNameHandler import FetchNameHandler

import pni.nx.h5 as nx

from xml import sax
import json
import sys, os
import gc
from collections import Iterable

from H5Elements import EFile
from DecoderPool import DecoderPool

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
        ## maximal number of threads
        self.numThreads = 100

        ## thread pool with INIT elements
        self._initPool = None
        ## thread pool with STEP elements
        self._stepPool = None
        ## thread pool with FINAL elements
        self._finalPool = None
        ## collection of thread pool with triggered STEP elements
        self._triggerPools = {}
        ## H5 file handle
        self._nxFile = None
        ## element file objects
        self._eFile = None

        ## pool with decoders
        self._decoders = DecoderPool()


        ## adding logs
        self.addingLogs = True
        ## counter for open entries
        self._entryCounter = 0
        ## group with Nexus log Info
        self._logGroup = None

        

    ## the H5 file handle 
    # \returns the H5 file handle 
    def getNXFile(self):
        return self._nxFile            

       

    ## the H5 file opening
    # \brief It opens the H5 file       
    def openNXFile(self):
        ## file handle
        self.closeNXFile() 
        self._nxFile = None
        self._eFile = None
        self._initPool = None
        self._stepPool = None
        self._finalPool = None
        self._triggerPools = {}
        ## file handle
        self._nxFile = nx.create_file(self.fileName, overwrite=True)
        ## element file objects
        self._eFile = EFile("NXfile", [], None, self._nxFile)
        if self.addingLogs:    
            self._logGroup = self._nxFile.create_group("NexusConfigurationLogs")



    ##  opens the data entry corresponding to a new XML settings
    # \brief It parse the XML settings, creates thread pools and runs the INIT pool.
    def openEntry(self):
        if self.xmlSettings:
            self._decoders = DecoderPool(json.loads(self.json))            

            parser = sax.make_parser()
        
            fetcher = FetchNameHandler()
            sax.parseString(self.xmlSettings, fetcher)
            
            handler = NexusXMLHandler(self._eFile, self._decoders, fetcher.groupTypes)
            sax.parseString(self.xmlSettings, handler)
            
            self._initPool = handler.initPool
            self._stepPool = handler.stepPool
            self._finalPool = handler.finalPool
            self._triggerPools = handler.triggerPools
            
            self._initPool.numThreads = self.numThreads
            self._stepPool.numThreads = self.numThreads
            self._finalPool.numThreads = self.numThreads

            for pool in self._triggerPools.keys():
                self._triggerPools[pool].numThreads = self.numThreads


            self._initPool.setJSON(json.loads(self.json))
            self._initPool.runAndWait()
            self._initPool.checkErrors()

            if self.addingLogs:    
                self._entryCounter += 1
                lfield = self._logGroup.create_field("Nexus__entry__%s_XML" % str(self._entryCounter),"string")
                lfield.write(self.xmlSettings)
            

    ## close the data writer        
    # \brief It runs threads from the STEP pool
    # \param jsonstring local JSON string with data records      
    def record(self, jsonstring=None):
        localJSON = None
        if jsonstring:
            localJSON = json.loads(jsonstring)
            
        if self._stepPool:
            print "Default trigger"
            self._stepPool.setJSON(json.loads(self.json), localJSON)
            self._stepPool.runAndWait()
            self._stepPool.checkErrors()
       
        triggers = None    
        if localJSON and 'triggers' in localJSON.keys():
            triggers = localJSON['triggers']

        if isinstance(triggers, Iterable):
            for pool in triggers:
                if pool in self._triggerPools.keys():
                    print "Trigger: %s" % pool 
                    self._triggerPools[pool].setJSON(self.json, json)
                    self._triggerPools[pool].runAndWait()
                    self._triggerPools[pool].checkErrors()
        gc.collect()


    ## closes the data entry        
    # \brief It runs threads from the FINAL pool and
    #  removes the thread pools 
    def closeEntry(self):

        if self._finalPool:
            self._finalPool.setJSON(json.loads(self.json))
            self._finalPool.runAndWait()
            self._finalPool.checkErrors()


        if self._initPool:
            self._initPool.close()
        self._initPool = None
            

        if self._stepPool:
            self._stepPool.close()
        self._stepPool = None
                
        if self._finalPool: 
            self._finalPool.close()
        self._finalPool = None

        if self._triggerPools: 
            for pool in self._triggerPools.keys(): 
                self._triggerPools[pool].close()
            self._triggerPools = {}


#        if self._nxFile:
#            self._nxFile.flush()

        gc.collect()


    ## the H5 file closing
    # \brief It closes the H5 file       
    def closeNXFile(self):

        if self._initPool:
            self._initPool.close()
            self._initPool = None         
   
        if self._stepPool:
            self._stepPool.close()
            self._stepPool = None         
                
        if self._finalPool: 
            self._finalPool.close()
            self._finalPool = None         


        if self._triggerPools: 
            for pool in self._triggerPools.keys(): 
                self._triggerPools[pool].close()
            self._triggerPools = {}

        if self._nxFile:    
            self._nxFile.close()
            
        self._nxFile = None
        self._eFile = None
        gc.collect()

        



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

    if argc > 1:
        print "opening the H5 file"
        tdw.openNXFile()



        for i in range(1, argc-1):
            xmlf = sys.argv[i]
        
            ## xml string    
            xml = open(xmlf, 'r').read()
            tdw.xmlSettings = xml

            print "opening the data entry "
            tdw.openEntry()
            
            print "recording the H5 file"
            tdw.record('{"data": {"emittance_x": 0.8} ,  "triggers":["trigger1", "trigger2"] }')
            
            print "sleeping for 1s"
            time.sleep(1)
            print "recording the H5 file"
            tdw.record('{"data": {"emittance_x": 1.2}  ,  "triggers":["trigger2"] }')

            print "sleeping for 1s"
            time.sleep(1)
            print "recording the H5 file"
            tdw.record('{"data": {"emittance_x": 1.1}  ,  "triggers":["trigger1"] }')


            print "sleeping for 1s"
            time.sleep(1)
            print "recording the H5 file"
            tdw.record('{"data": {"emittance_x": 0.7} }')

            print "closing the data entry "
            tdw.closeEntry()


        print "closing the H5 file"
        tdw.closeNXFile()
            
                
    
