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
        self._fcounter =  [1.1,-2.4,6.54,-8.456,9.456,-0.46545]
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


    ## checks scalar tree
    # \param f pninx file object    
    # \param fname file name
    # \returns detector group object    
    def _checkScalarTree(self, f, fname, children):
        self.assertEqual("%s/%s" % ( os.getcwd(), f.name), fname)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        self.assertEqual(f.nchildren, 2)
            
        en = f.open("entry1")
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry1")
        self.assertEqual(en.nattrs,1)
        self.assertEqual(en.nchildren, 1)

        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")

        ins = en.open("instrument")
        self.assertTrue(ins.valid)
        self.assertEqual(ins.name,"instrument")
        self.assertEqual(ins.nattrs,1)
        self.assertEqual(ins.nchildren, 1)
        
            
        at = ins.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXinstrument")

        det = ins.open("detector")
        self.assertTrue(det.valid)
        self.assertEqual(det.name,"detector")
        self.assertEqual(det.nattrs,1)
        self.assertEqual(det.nchildren, children)
            
        at = det.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXdetector")
            
        return det




    ## checks  scalar counter
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param unsigned flag if value is integer
    def _checkScalarCounter(self, det, name, dtype, nxtype, values, error = 0):

        cnt = det.open(name)
        self.assertTrue(cnt.valid)
        self.assertEqual(cnt.name,name)
        self.assertTrue(hasattr(cnt.shape, "__iter__"))
        self.assertEqual(len(cnt.shape), 1)
        self.assertEqual(cnt.shape, (6,))
        self.assertEqual(cnt.dtype, dtype)
        self.assertEqual(cnt.size, 6)
        value = cnt.read()
        for i in range(len(value)):
#            print values[i].__repr__(),  value[i].__repr__(), values[i] - value[i]
            self.assertTrue(abs(values[i]- value[i]) <= error)
                        
        self.assertEqual(cnt.nattrs,3)

        at = cnt.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,nxtype)
        

        at = cnt.attr("units")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"units")
        self.assertEqual(at.value,"m")
        
        at = cnt.attr("nexdatas_source")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        

    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientIntScalar(self):
        print "Run: FieldTagWriterTest.test_clientIntScalar() "
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
            tdw.record('{"data": {"cnt":' + str(c) 
                       + ', "cnt_8":' + str(c) 
                       + ', "cnt_16":' + str(c) 
                       + ', "cnt_32":' + str(c) 
                       + ', "cnt_64":' + str(c) 
                       + ', "cnt_u":' + str(uc) 
                       + ', "cnt_u8":' + str(uc) 
                       + ', "cnt_u16":' + str(uc) 
                       + ', "cnt_u32":' + str(uc) 
                       + ',  "cnt_u64":' + str(uc)
                       + ' } }')
        
        tdw.closeEntry()
        
        tdw.closeNXFile()
            


        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._checkScalarTree(f, fname , 10)
        self._checkScalarCounter(det, "counter", "int64", "NX_INT", self._counter)
        self._checkScalarCounter(det, "counter8", "int8", "NX_INT8", self._counter)
        self._checkScalarCounter(det, "counter16", "int16", "NX_INT16", self._counter)
        self._checkScalarCounter(det, "counter32", "int32", "NX_INT32", self._counter)
        self._checkScalarCounter(det, "counter64", "int64", "NX_INT64", self._counter)
        self._checkScalarCounter(det, "ucounter", "uint64", "NX_UINT", [abs(c) for c in self._counter])
        self._checkScalarCounter(det, "ucounter8", "uint8", "NX_UINT8", [abs(c) for c in self._counter]) 
        self._checkScalarCounter(det, "ucounter16", "uint16", "NX_UINT16", [abs(c) for c in self._counter]) 
        self._checkScalarCounter(det, "ucounter32", "uint32", "NX_UINT32", [abs(c) for c in self._counter]) 
        self._checkScalarCounter(det, "ucounter64", "uint64", "NX_UINT64", [abs(c) for c in self._counter]) 

        
        f.close()



    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_clientFloatScalar(self):
        print "FLOAT"
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

      </group>
    </group>
  </group>
</definition>
"""
        

        tdw = TangoDataWriter(fname)

        tdw.openNXFile()
        
        tdw.xmlSettings = xml
        
        tdw.openEntry()
            
        for c in self._fcounter:
            tdw.record('{"data": {"cnt":' + str(c) 
                       + ', "cnt_32":' + str(c) 
                       + ', "cnt_64":' + str(c) 
                       + ' } }')
        
        tdw.closeEntry()
        
        tdw.closeNXFile()
            


        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._checkScalarTree(f, fname, 3)
        self._checkScalarCounter(det, "counter", "float64", "NX_FLOAT", self._fcounter, 1.0e-14)
        self._checkScalarCounter(det, "counter_64", "float64", "NX_FLOAT64", self._fcounter, 1.0e-14)
        self._checkScalarCounter(det, "counter_32", "float32", "NX_FLOAT32", self._fcounter, 1.0e-06)

        
        f.close()

            

        
#        os.remove(fname)
