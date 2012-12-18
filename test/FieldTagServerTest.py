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


import ServerTestCase

## test fixture
class FieldTagServerTest(ServerTestCase.ServerTestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        ServerTestCase.ServerTestCase.__init__(self, methodName)

        self._counter =  [1, 2]
        self._mca1 = [e*0.1 for e in range(2048)]
        self._mca2 = [(float(e)/(100.+e)) for e in range(2048)]



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
        
        dp.Record('{"data": {"cnt":'+str(self._counter[0])+', "p09/mca/exp.02":'\
                      + str(self._mca1)+ '  } }')
        self.assertEqual(dp.state(),PyTango.DevState.EXTRACT)
        dp.Record('{"data": {"cnt":'+str(self._counter[1])+', "p09/mca/exp.02":'\
                      + str(self._mca2)+ '  } }')
        
        
        dp.CloseEntry()
        self.assertEqual(dp.state(),PyTango.DevState.OPEN)
        
        
        dp.CloseFile()
        self.assertEqual(dp.state(),PyTango.DevState.ON)
                
        
             # check the created file
        
        f = open_file(fname,readonly=True)
        self.assertEqual(f.path, fname)
        self.assertEqual(6, f.nattrs)
        self.assertEqual(f.attr("file_name").value, fname)
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
        
        #            ins = f.open("entry1/instrument:NXinstrument")    #bad exception
        #            ins = f.open("entry1/instrument")
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
        self.assertEqual(det.nchildren, 1)
        
        at = det.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXdetector")
        
        cnt = det.open("counter")
        self.assertTrue(cnt.valid)
        self.assertEqual(cnt.name,"counter")
        self.assertTrue(hasattr(cnt.shape, "__iter__"))
        self.assertEqual(len(cnt.shape), 1)
        self.assertEqual(cnt.shape, (2,))
        self.assertEqual(cnt.dtype, "int64")
        self.assertEqual(cnt.size, 2)
#            print cnt.read()
        value = cnt[:]
        for i in range(len(value)):
            self.assertEqual(self._counter[i], value[i])
            
            
            
        self.assertEqual(cnt.nattrs,3)
        
        
        
        
        at = cnt.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_INT")
        
        
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
        self.assertEqual(at.name,"nexdatas_source")
        
        

        
        f.close()
            
        os.remove(fname)
