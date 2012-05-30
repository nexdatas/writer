#!/usr/bin/env python
"""@package docstring
@file TangoDataWriter.py
Nexus H5 Writer
"""

from NeXusXMLHandler import *

import pni.nx.h5 as nx

from numpy  import * 
from xml import sax

import sys,os
from H5Elements import *



class TangoDataWriter:
    def __init__(self,name):
        self.name=name
        self.xmlSettings=""
        self.json=""
#        self.handler = None
        self.initPool=None
        self.stepPool=None
        self.finalPool=None
        self.nxFile=None

    def open(self):
        print 'open:'
        if len(self.xmlSettings)>0:
            parser = sax.make_parser()
        
            handler = NexusXMLHandler(self.name)
            sax.parseString(self.xmlSettings,handler)
            
            self.initPool=handler.initPool
            self.stepPool=handler.stepPool
            self.finalPool=handler.finalPool
            
            self.initPool.runAndWait()
            self.nxFile=handler.getNXFile()

            
    def setXML(self,xmlSettings):
        self.xmlSettings=xmlSettings
        print 'setXML'

    def getXML(self):
        print 'getXML'
        return self.xmlSettings

    def setJSON(self,json):
        self.json=json
        print 'setJSON'

    def getJSON(self):
        print 'getJSON'
        return self.json

    def record(self):
        print 'record:'
        if self.stepPool:
            self.stepPool.runAndWait()


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


    # Create a TDW object
    tdw = TangoDataWriter("TDW")
    
