#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
import Streams
try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx

from xml import sax

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

import json
import sys, os
import gc

from H5Elements import EFile
from DecoderPool import DecoderPool
from DataSourcePool import DataSourcePool

## NeXuS data writer
class TangoDataWriter(object):
    ## constructor
    # \brief It initialize the data writer for the H5 output file
    # \param server Tango server
    def __init__(self, server = None):
        ## output file name
        self.fileName = ""
        ## Tango server
        self.__server = server
        ## XML string with file settings
        self.__xmlSettings = ""
        ## global JSON string with data records
        self.__json = "{}"
        ## maximal number of threads
        self.numThreads = 100
#        self.numThreads = 1

        ## thread pool with INIT elements
        self.__initPool = None
        ## thread pool with STEP elements
        self.__stepPool = None
        ## thread pool with FINAL elements
        self.__finalPool = None
        ## collection of thread pool with triggered STEP elements
        self.__triggerPools = {}
        ## H5 file handle
        self.__nxFile = None
        ## element file objects
        self.__eFile = None

        ## pool with decoders
        self.__decoders = DecoderPool()

        ## pool with decoders
        self.__datasources = DataSourcePool()

        ## group name parser
        self.__fetcher = None


        ## adding logs
        self.addingLogs = True
        ## counter for open entries
        self.__entryCounter = 0
        ## group with Nexus log Info
        self.__logGroup = None

        if server:
            if  hasattr(self.__server, "log_fatal"):
                Streams.log_fatal = server.log_fatal
            if  hasattr(self.__server, "log_error"):
                Streams.log_error = server.log_error
            if  hasattr(self.__server, "log_warn"):
                Streams.log_warn = server.log_warn
            if  hasattr(self.__server, "log_info"):
                Streams.log_info = server.log_info
            if  hasattr(self.__server, "log_debug"):
                Streams.log_debug = server.log_debug
    
    ## get method for thejson attribute
    # \returns value of thejson            
    def __getJSON(self):
        return self.__json

    ## set method for thejson attribute
    # \param jsonstring value of thejson            
    def __setJSON(self, jsonstring):
        self.__decoders = DecoderPool(json.loads(jsonstring))            
        self.__datasources = DataSourcePool(json.loads(jsonstring))            
        self.__json = jsonstring

    ## del method for thejson attribute
    def __delJSON(self):
        del self.__json 

    ## the json data string
    thejson = property(__getJSON, __setJSON, __delJSON)



    ## get method for xmlSettings attribute
    # \returns value of thejson            
    def __getXML(self):
        return self.__xmlSettings

    ## set method for xmlSettings attribute
    # \param xml xml settings
    def __setXML(self, xml):
        self.__fetcher = FetchNameHandler()
        sax.parseString(xml, self.__fetcher)
        self.__xmlSettings = xml

    ## del method for xmlSettings attribute
    def __delXML(self):
        del self.__xmlSettings 

    ## the xmlSettings
    xmlSettings = property(__getXML, __setXML, __delXML)


    ## the H5 file handle 
    # \returns the H5 file handle 
    def getNXFile(self):
        return self.__nxFile            

       

    ## the H5 file opening
    # \brief It opens the H5 file       
    def openNXFile(self):
        ## file handle
        self.closeNXFile() 
        self.__nxFile = None
        self.__eFile = None
        self.__initPool = None
        self.__stepPool = None
        self.__finalPool = None
        self.__triggerPools = {}
        ## file handle
        self.__nxFile = nx.create_file(self.fileName, overwrite=True)
        ## element file objects
        self.__eFile = EFile([], None, self.__nxFile)
        if self.addingLogs:    
            self.__logGroup = self.__nxFile.create_group("NexusConfigurationLogs")



    ##  opens the data entry corresponding to a new XML settings
    # \brief It parse the XML settings, creates thread pools and runs the INIT pool.
    def openEntry(self):
        if self.xmlSettings:
            # flag for INIT mode
            self.__datasources.counter = -1
            errorHandler = sax.ErrorHandler()
            parser = sax.make_parser()
 
            handler = NexusXMLHandler(self.__eFile, self.__datasources, self.__decoders, 
                                      self.__fetcher.groupTypes, parser, json.loads(self.thejson))
            parser.setContentHandler(handler)
            parser.setErrorHandler(errorHandler)

            inpsrc = sax.InputSource()
            inpsrc.setByteStream(StringIO(self.xmlSettings))
            parser.parse(inpsrc)

            
            self.__initPool = handler.initPool
            self.__stepPool = handler.stepPool
            self.__finalPool = handler.finalPool
            self.__triggerPools = handler.triggerPools
            
            self.__initPool.numThreads = self.numThreads
            self.__stepPool.numThreads = self.numThreads
            self.__finalPool.numThreads = self.numThreads

            for pool in self.__triggerPools.keys():
                self.__triggerPools[pool].numThreads = self.numThreads

            self.__initPool.setJSON(json.loads(self.thejson))
            self.__initPool.runAndWait()
            self.__initPool.checkErrors()

            if self.addingLogs:    
                self.__entryCounter += 1
                lfield = self.__logGroup.create_field("Nexus__entry__%s_XML" % str(self.__entryCounter),"string")
                lfield.write(self.xmlSettings)
                lfield.close()
            if self.__nxFile and hasattr(self.__nxFile, "flush"):
                self.__nxFile.flush()

    ## close the data writer        
    # \brief It runs threads from the STEP pool
    # \param jsonstring local JSON string with data records      
    def record(self, jsonstring=None):
        # flag for STEP mode
        if self.__datasources.counter>0:
            self.__datasources.counter +=1
        else:
            self.__datasources.counter = 1
        localJSON = None
        if jsonstring:
            localJSON = json.loads(jsonstring)
            
        if self.__stepPool:
            if Streams.log_info:
                print >> Streams.log_info , "TangoDataWriter::record() - Default trigger"
            print "TangoDataWriter::record() - Default trigger"
            self.__stepPool.setJSON(json.loads(self.thejson), localJSON)
            self.__stepPool.runAndWait()
            self.__stepPool.checkErrors()
       
        triggers = None    
        if localJSON and 'triggers' in localJSON.keys():
            triggers = localJSON['triggers']

        if hasattr(triggers, "__iter__"):
            for pool in triggers:
                if pool in self.__triggerPools.keys():
                    if Streams.log_info:
                        print >> Streams.log_info , "TangoDataWriter:record() - Trigger: %s" % pool 
                    print "TangoDataWriter:record() - Trigger: %s" % pool 
                    self.__triggerPools[pool].setJSON(json.loads(self.thejson), localJSON)
                    self.__triggerPools[pool].runAndWait()
                    self.__triggerPools[pool].checkErrors()

        if self.__nxFile and hasattr(self.__nxFile, "flush"):
            self.__nxFile.flush()
#        gc.collect()


    ## closes the data entry        
    # \brief It runs threads from the FINAL pool and
    #  removes the thread pools 
    def closeEntry(self):
        # flag for FINAL mode
        self.__datasources.counter = -2

        if self.addingLogs and self.__logGroup:    
            self.__logGroup.close()
            self.__logGroup = None

        if self.__finalPool:
            self.__finalPool.setJSON(json.loads(self.thejson))
            self.__finalPool.runAndWait()
            self.__finalPool.checkErrors()


        if self.__initPool:
            self.__initPool.close()
        self.__initPool = None
            

        if self.__stepPool:
            self.__stepPool.close()
        self.__stepPool = None
                
        if self.__finalPool: 
            self.__finalPool.close()
        self.__finalPool = None

        if self.__triggerPools: 
            for pool in self.__triggerPools.keys(): 
                self.__triggerPools[pool].close()
            self.__triggerPools = {}

        if self.addingLogs and self.__logGroup:    
            self.__logGroup.close()

        if self.__nxFile and hasattr(self.__nxFile, "flush"):
            self.__nxFile.flush()

        gc.collect()


    ## the H5 file closing
    # \brief It closes the H5 file       
    def closeNXFile(self):

        if self.__initPool:
            self.__initPool.close()
            self.__initPool = None         
   
        if self.__stepPool:
            self.__stepPool.close()
            self.__stepPool = None         
                
        if self.__finalPool: 
            self.__finalPool.close()
            self.__finalPool = None         


        if self.__triggerPools: 
            for pool in self.__triggerPools.keys(): 
                self.__triggerPools[pool].close()
            self.__triggerPools = {}

        if self.__nxFile:    
            self.__nxFile.close()
            
        self.__nxFile = None
        self.__eFile = None
        gc.collect()

        



if __name__ == "__main__":

    import time

    # Create a TDW object
    ## instance of TangoDataWriter
    tdw = TangoDataWriter()
    tdw.fileName = 'test.h5'

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
            
                
    
