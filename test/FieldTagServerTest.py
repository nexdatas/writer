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

from Checkers import Checker

import ServerTestCase

## test fixture
class FieldTagServerTest(ServerTestCase.ServerTestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        ServerTestCase.ServerTestCase.__init__(self, methodName)

        self._counter =  [1, 2]
        self._fcounter =  [1.1,-2.4,6.54,-8.456,9.456,-0.46545]
        self._sc = Checker(self)



    ## test starter
    # \brief Common set up of Tango Server
    def setUp(self):
        ServerTestCase.ServerTestCase.setUp(self)

    ## test closer
    # \brief Common tear down oif Tango Server
    def tearDown(self): 
        ServerTestCase.ServerTestCase.tearDown(self)
        


    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientIntScalar(self):
        print "Run: FieldTagServerTest.test_scanRecord() "
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
        <field units="m" type="NX_POSINT" name="pcounter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_p"/>
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



        dp = PyTango.DeviceProxy("testp09/testtdw/testr228")
            #        print 'attributes', dp.attribute_list_query()
        dp.FileName = fname
        self.assertEqual(dp.state(),PyTango.DevState.ON)
        
        dp.OpenFile()
        
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        dp.TheXMLSettings = xml
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        
        dp.OpenEntry()
        self.assertEqual(dp.state(),PyTango.DevState.EXTRACT)
        


        for c in self._counter:
            uc = abs(c)
            dp.Record('{"data": {"cnt":' + str(c) 
                      + ', "cnt_8":' + str(c) 
                      + ', "cnt_16":' + str(c) 
                      + ', "cnt_32":' + str(c) 
                      + ', "cnt_64":' + str(c) 
                      + ', "cnt_u":' + str(uc) 
                      + ', "cnt_p":' + str(uc) 
                      + ', "cnt_u8":' + str(uc) 
                      + ', "cnt_u16":' + str(uc) 
                      + ', "cnt_u32":' + str(uc) 
                      + ',  "cnt_u64":' + str(uc)
                      + ' } }')
            
        self.assertEqual(dp.state(),PyTango.DevState.EXTRACT)

        
        dp.CloseEntry()
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        
        dp.CloseFile()
        self.assertEqual(dp.state(),PyTango.DevState.ON)
                




        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkScalarTree(f, fname , 11)
        self._sc.checkScalarCounter(det, "counter", "int64", "NX_INT", self._counter)
        self._sc.checkScalarCounter(det, "counter8", "int8", "NX_INT8", self._counter)
        self._sc.checkScalarCounter(det, "counter16", "int16", "NX_INT16", self._counter)
        self._sc.checkScalarCounter(det, "counter32", "int32", "NX_INT32", self._counter)
        self._sc.checkScalarCounter(det, "counter64", "int64", "NX_INT64", self._counter)
        self._sc.checkScalarCounter(det, "ucounter", "uint64", "NX_UINT", [abs(c) for c in self._counter])
        self._sc.checkScalarCounter(det, "ucounter8", "uint8", "NX_UINT8", [abs(c) for c in self._counter]) 
        self._sc.checkScalarCounter(det, "ucounter16", "uint16", "NX_UINT16", [abs(c) for c in self._counter]) 
        self._sc.checkScalarCounter(det, "ucounter32", "uint32", "NX_UINT32", [abs(c) for c in self._counter]) 
        self._sc.checkScalarCounter(det, "ucounter64", "uint64", "NX_UINT64", [abs(c) for c in self._counter]) 

        
        f.close()
        os.remove(fname)


    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientFloatScalar(self):
        print "Run: FieldTagWriterTest.test_clientFloatScalar() "
        fname= '%s/clientfloatscalar.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT32" name="counter_32">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_32"/>
          </datasource>
        </field>
        <field units="m" type="NX_FLOAT64" name="counter_64">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>
        <field units="m" type="NX_NUMBER" name="counter_nb">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="cnt_64"/>
          </datasource>
        </field>
      </group>
    </group>
  </group>
</definition>
"""
        




        dp = PyTango.DeviceProxy("testp09/testtdw/testr228")
            #        print 'attributes', dp.attribute_list_query()
        dp.FileName = fname
        self.assertEqual(dp.state(),PyTango.DevState.ON)
        
        dp.OpenFile()
        
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        dp.TheXMLSettings = xml
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        
        dp.OpenEntry()
        self.assertEqual(dp.state(),PyTango.DevState.EXTRACT)
        


        for c in self._fcounter:
            uc = abs(c)
            dp.Record('{"data": {"cnt":' + str(c) 
                       + ', "cnt_32":' + str(c) 
                       + ', "cnt_64":' + str(c) 
                       + ' } }')

        self.assertEqual(dp.state(),PyTango.DevState.EXTRACT)

        
        dp.CloseEntry()
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        
        dp.CloseFile()
        self.assertEqual(dp.state(),PyTango.DevState.ON)
                
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkScalarTree(f, fname, 4)
        self._sc.checkScalarCounter(det, "counter", "float64", "NX_FLOAT", self._fcounter, 1.0e-14)
        self._sc.checkScalarCounter(det, "counter_64", "float64", "NX_FLOAT64", self._fcounter, 1.0e-14)
        self._sc.checkScalarCounter(det, "counter_32", "float32", "NX_FLOAT32", self._fcounter, 1.0e-06)
        self._sc.checkScalarCounter(det, "counter_nb", "float64", "NX_NUMBER", self._fcounter, 1.0e-14)

        
        f.close()
        os.remove(fname)


    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientScalar(self):
        print "Run: FieldTagWriterTest.test_clientFloatScalar() "
        fname= '%s/clientscalar.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_DATE_TIME" name="time">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="timestamp"/>
          </datasource>
        </field>
        <field units="m" type="ISO8601" name="isotime">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="timestamp"/>
          </datasource>
        </field>
        <field units="m" type="NX_CHAR" name="string_time">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="timestamp"/>
          </datasource>
        </field>
        <field units="m" type="NX_BOOLEAN" name="flags">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="logical"/>
          </datasource>
        </field>

      </group>
    </group>
  </group>
</definition>
"""
        dates = [
            "1996-07-31T21:15:22.123+0600","2012-11-14T14:05:23.2344-0200",
            "2014-02-04T04:16:12.43-0100","2012-11-14T14:05:23.2344-0200",
            "1996-07-31T21:15:22.123+0600","2012-11-14T14:05:23.2344-0200",
            "2014-02-04T04:16:12.43-0100","2012-11-14T14:05:23.2344-0200",
            ]
        logical = ["1","0","true","false","True","False","TrUe","FaLsE"]
        


        dp = PyTango.DeviceProxy("testp09/testtdw/testr228")
            #        print 'attributes', dp.attribute_list_query()
        dp.FileName = fname
        self.assertEqual(dp.state(),PyTango.DevState.ON)
        
        dp.OpenFile()
        
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        dp.TheXMLSettings = xml
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        
        dp.OpenEntry()
        self.assertEqual(dp.state(),PyTango.DevState.EXTRACT)
        

        for i in range(min(len(dates),len(logical))):
            dp.Record('{"data": {"timestamp":"' + str(dates[i]) 
                       + '", "logical":"' + str(logical[i])
                       + '" } }')

        self.assertEqual(dp.state(),PyTango.DevState.EXTRACT)

        
        dp.CloseEntry()
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        
        dp.CloseFile()
        self.assertEqual(dp.state(),PyTango.DevState.ON)
                
            
            


        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkScalarTree(f, fname, 4)
        self._sc.checkScalarCounter(det, "time", "string", "NX_DATE_TIME", dates)
        self._sc.checkScalarCounter(det, "isotime", "string", "ISO8601", dates)
        self._sc.checkScalarCounter(det, "string_time", "string", "NX_CHAR", dates)
        self._sc.checkScalarCounter(det, "flags", "bool", "NX_BOOLEAN", logical)

        
        f.close()
        os.remove(fname)
