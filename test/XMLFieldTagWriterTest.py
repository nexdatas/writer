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
## \package test nexdatas
## \file XMLFieldTagWriterTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random

from pni.nx.h5 import open_file
from  xml.sax import SAXParseException


from ndts import TangoDataWriter, Types
from ndts.TangoDataWriter  import TangoDataWriter 
from Checkers import Checker

## test fixture
class XMLFieldTagWriterTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._counter =  [1,-2,6,-8,9,-11]
        self._fcounter =  [1.1,-2.4,6.54,-8.456,9.456,-0.46545]
        self._sc = Checker(self)
        self._mca1 = [[random.randint(-100, 100) for e in range(256)] for i in range(3)]
        self._mca2 = [[random.randint(0, 100) for e in range(256)] for i in range(3)]
        self._fmca1 = [self._sc.nicePlot(1024, 10) for i in range(4)]
#        self._fmca2 = [(float(e)/(100.+e)) for e in range(2048)]
        self._pco1 = [[[random.randint(0, 100) for e1 in range(8)]  for e2 in range(10)] for i in range(3)]
        self._fpco1 = [self._sc.nicePlot2D(20, 30, 5) for i in range(4)]

    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## opens writer
    # \param fname file name     
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer instance   
    def openWriter(self, fname, xml, json = None):
        tdw = TangoDataWriter(fname)
        tdw.openNXFile()
        tdw.xmlSettings = xml
        if json:
            tdw.json = json
        tdw.openEntry()
        return tdw

    ## closes writer
    # \param tdw Tango Data Writer instance
    # \param json JSON Record with client settings
    def closeWriter(self, tdw, json = None):
        if json:
            tdw.json = json
        tdw.closeEntry()
        tdw.closeNXFile()

    ## performs one record step
    def record(self, tdw, string):
        tdw.record(string)


    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_xmlScalar(self):
        print "Run: %s.test_xmlScalar() " % self.__class__.__name__
        fname= '%s/xmlscalar.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_INT" name="counter">
          -12
        </field>
        <field units="m" type="NX_INT8" name="counter8">
          -12
        </field>
        <field units="m" type="NX_INT16" name="counter16">
          -12
        </field>
        <field units="m" type="NX_INT32" name="counter32">
          -12
        </field>
        <field units="m" type="NX_INT64" name="counter64">
          -12
        </field>
        <field units="m" type="NX_UINT" name="ucounter">
          12
        </field>
        <field units="m" type="NX_POSINT" name="pcounter">
          12
        </field>
        <field units="m" type="NX_UINT8" name="ucounter8">
          12
        </field>
        <field units="m" type="NX_UINT16" name="ucounter16">
          12
        </field>
        <field units="m" type="NX_UINT32" name="ucounter32">
          12
        </field>
        <field units="m" type="NX_UINT64" name="ucounter64">
          12
        </field>

      </group>
    </group>
  </group>
</definition>
"""

        uc = 12
        tdw = self.openWriter(fname, xml)

        flip = True    
        for c in self._counter:
            uc = abs(c)
            self.record(tdw,'{ }')
            flip = not flip

        uc = abs(self._counter[0])
        self.closeWriter(tdw)
        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkFieldTree(f, fname , 11)
        self._sc.checkXMLScalarField(det, "counter", "int64", "NX_INT", -uc)
        self._sc.checkXMLScalarField(det, "counter8", "int8", "NX_INT8", -uc)
        self._sc.checkXMLScalarField(det, "counter16", "int16", "NX_INT16", -uc)
        self._sc.checkXMLScalarField(det, "counter32", "int32", "NX_INT32", -uc)
        self._sc.checkXMLScalarField(det, "counter64", "int64", "NX_INT64", -uc)
        self._sc.checkXMLScalarField(det, "ucounter", "uint64", "NX_UINT", uc)
        self._sc.checkXMLScalarField(det, "ucounter8", "uint8", "NX_UINT8", uc)
        self._sc.checkXMLScalarField(det, "ucounter16", "uint16", "NX_UINT16", uc)
        self._sc.checkXMLScalarField(det, "ucounter32", "uint32", "NX_UINT32", uc)
        self._sc.checkXMLScalarField(det, "ucounter64", "uint64", "NX_UINT64",uc)
       
        f.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
