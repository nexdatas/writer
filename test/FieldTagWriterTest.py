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
## \package test nexdatas
## \file FieldTagServerTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess

import PyTango
import time
from pni.nx.h5 import open_file
from  xml.sax import SAXParseException


from ndts import TangoDataWriter 
from ndts.TangoDataWriter  import TangoDataWriter 


## test fixture
class FieldTagWriterTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._counter =  [1,-2,6,-8,9,-11]
        self._mca1 = [e*0.1 for e in range(2048)]
        self._mca2 = [(float(e)/(100.+e)) for e in range(2048)]


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientIntScalar(self):
        print "Run: FieldTagWriterTest.test_scanRecord() "
        fname= '%s/clientintscalar.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_INT" name="counter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT8" name="counter8">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_8"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT16" name="counter16">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_16"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT32" name="counter32">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_32"/>
          </datasource>
        </field>
        <field units="m" type="NX_INT64" name="counter64">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT" name="ucounter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT8" name="ucounter8">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u8"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT16" name="ucounter16">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u16"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT32" name="ucounter32">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u32"/>
          </datasource>
        </field>
        <field units="m" type="NX_UINT64" name="ucounter64">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_u64"/>
          </datasource>
        </field>

      </group>
    </group>
  </group>
</definition>
"""
        

        tdw = TangoDataWriter(fname)

        tdw.openNXFile()
        
        tdw.xmlSettings = xml
        
        tdw.openEntry()
            
        for c in self._counter:
            uc = abs(c)
            tdw.record('{"data": {"cnt":'+str(c) 
                       + ', "cnt_8":'+str(c) 
                       + ', "cnt_16":'+str(c) 
                       + ', "cnt_32":' + str(c) 
                       + ',  "cnt_64":' + str(c) 
                       + ', "cnt_u":'+str(uc) 
                       + ', "cnt_u8":'+str(uc) 
                       + ', "cnt_u16":'+str(uc) 
                       + ', "cnt_u32":' + str(uc) 
                       + ',  "cnt_u64":' + str(uc)+ 
                       '  } }')
        
        tdw.closeEntry()
        
        tdw.closeNXFile()
            

        
#        os.remove(fname)
