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
## \file TangoFieldTagWirterTest.py
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

import SimpleServerSetUp

## test fixture
class TangoFieldTagWriterTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()

        self._counter =  [1,-2,6,-8,9,-11]
        self._bools =  ["TruE","0","1","False","false", "True"]
        self._fcounter =  [1.1,-2.4,6.54,-8.456,9.456,-0.46545]
        self._dcounter =  [0.1,-2342.4,46.54,-854.456,9.243456,-0.423426545]
        self._logical =  [[True,False,True,False], [True,False,False,True], [False,False,True,True]]

        self._sc = Checker(self)
        self._mca1 = [[random.randint(-100, 100) for e in range(256)] for i in range(3)]
        self._mca2 = [[random.randint(0, 100) for e in range(256)] for i in range(3)]
        self._fmca1 = [self._sc.nicePlot(1024, 10) for i in range(4)]
#        self._fmca2 = [(float(e)/(100.+e)) for e in range(2048)]

        self._dates = [["1996-07-31T21:15:22.123+0600","2012-11-14T14:05:23.2344-0200",
                        "2014-02-04T04:16:12.43-0100","2012-11-14T14:05:23.2344-0200"],
                       ["1956-05-23T12:12:32.123+0400","1212-12-12T12:25:43.1267-0700",
                        "914-11-04T04:13:13.44-0000","1002-04-03T14:15:03.0012-0300"],                 
                       ["1966-02-21T11:22:02.113+0200","1432-12-11T11:23:13.1223-0300",
                        "1714-11-10T14:03:13.12-0400","1001-01-01T14:11:11.0011-0100"]]

        self._pco1 = [[[random.randint(0, 100) for e1 in range(8)]  for e2 in range(10)] for i in range(3)]
        self._fpco1 = [self._sc.nicePlot2D(20, 30, 5) for i in range(4)]
        self._encoded =[67305728,1413689632, 336793872 ]


    ## test starter
    # \brief Common set up
    def setUp(self):
        self._simps.setUp()

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        self._simps.tearDown()

    ## opens writer
    # \param fname file name     
    # \param xml XML settings
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
    def test_tangoScalar(self):
        print "Run: %s.test_tangoScalar() " % self.__class__.__name__
        fname= '%s/tangoscalar.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

       <field units="m" type="NX_BOOLEAN" name="ScalarBoolean">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarBoolean"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT8" name="ScalarUChar">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarUChar"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT16" name="ScalarShort">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT16" name="ScalarUShort">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarUShort"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT" name="ScalarLong">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarLong"/>
          </datasource>
        </field>

        <field units="m" type="NX_UINT" name="ScalarULong">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarULong"/>
          </datasource>
        </field>

        <field units="m" type="NX_INT64" name="ScalarLong64">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarLong64"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT32" name="ScalarFloat">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarFloat"/>
          </datasource>
        </field>

        <field units="m" type="NX_FLOAT64" name="ScalarDouble">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarDouble"/>
          </datasource>
        </field>


        <field units="m" type="NX_CHAR" name="ScalarString">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="ScalarString"/>
          </datasource>
        </field>

        <field units="m" type="NX_CHAR" name="ScalarEncoded">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
            <record name="ScalarEncoded"/>
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" encoding="UTF8"/>
          </datasource>
        </field>

        <field units="m" type="NX_CHAR" name="ScalarState">
          <strategy mode="STEP"/>
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="State"/>
          </datasource>
        </field>


      </group>
    </group>
  </group>
</definition>
"""


        tdw = self.openWriter(fname, xml)

        for i in range(min(len(self._counter), len(self._fcounter), len(self._bools))):
            self._simps.dp.ScalarBoolean = Types.Converters.toBool(self._bools[i])
            self._simps.dp.ScalarUChar = abs(self._counter[i])
            self._simps.dp.ScalarShort = self._counter[i]
            self._simps.dp.ScalarUShort = abs(self._counter[i])
            self._simps.dp.ScalarLong = self._counter[i]
            self._simps.dp.ScalarULong = abs(self._counter[i])
            self._simps.dp.ScalarLong64 = self._counter[i]
            self._simps.dp.ScalarFloat = self._fcounter[i]
            self._simps.dp.ScalarDouble = self._dcounter[i]
            self._simps.dp.ScalarString = self._bools[i]
            ## attributes of DevULong64, DevUChar, DevState type are not supported by PyTango 7.2.3
 #           self._simps.dp.ScalarULong64 = abs(self._counter[i])
            self.record(tdw,'{}')
#            self._fcounter[i] = self._simps.dp.ScalarFloat 
#            self._dcounter[i] = self._simps.dp.ScalarDouble 

        self.closeWriter(tdw)
        
        # check the created file
        
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkScalarTree(f, fname , 12)
        self._sc.checkScalarField(det, "ScalarBoolean", "bool", "NX_BOOLEAN", self._bools)
        self._sc.checkScalarField(det, "ScalarUChar", "uint8", "NX_UINT8", [abs(c) for c in self._counter])
        self._sc.checkScalarField(det, "ScalarShort", "int16", "NX_INT16", self._counter)
        self._sc.checkScalarField(det, "ScalarUShort", "uint16", "NX_UINT16", [abs(c) for c in self._counter])
        self._sc.checkScalarField(det, "ScalarLong", "int64", "NX_INT", self._counter)
        self._sc.checkScalarField(det, "ScalarULong", "uint64", "NX_UINT", [abs(c) for c in self._counter])
        self._sc.checkScalarField(det, "ScalarLong64", "int64", "NX_INT64", self._counter)
#        self._sc.checkScalarField(det, "ScalarULong64", "uint64", "NX_UINT64", [abs(c) for c in self._counter])
        self._sc.checkScalarField(det, "ScalarFloat", "float32", "NX_FLOAT32", self._fcounter, error = 1e-6)
        self._sc.checkScalarField(det, "ScalarDouble", "float64", "NX_FLOAT64", self._dcounter, error = 1e-14)
        self._sc.checkScalarField(det, "ScalarString", "string", "NX_CHAR", self._bools)
        self._sc.checkScalarField(det, "ScalarEncoded", "string", "NX_CHAR", ["Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b"  for c in self._bools])
        self._sc.checkScalarField(det, "ScalarState", "string", "NX_CHAR", ["ON"  for c in self._bools])
        
        # writing encoded attributes not supported for PyTango 7.2.3

        f.close()
        os.remove(fname)




    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_tangoSpectrum(self):
        print "Run: %s.test_tangoSpectrum() " % self.__class__.__name__
        fname= '%s/tangospectrum.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

       <field units="" type="NX_BOOLEAN" name="SpectrumBoolean">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumBoolean"/>
          </datasource>
        </field>


       <field units="" type="NX_UINT8" name="SpectrumUChar">
          <strategy mode="STEP"  compression="true"  grows="2" shuffle="false" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumUChar"/>
          </datasource>
        </field>

       <field units="" type="NX_INT16" name="SpectrumShort">
          <strategy mode="STEP"  compression="true"  grows="3" shuffle="True" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumShort"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT16" name="SpectrumUShort">
          <strategy mode="STEP"   grows="2" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumUShort"/>
          </datasource>
        </field>



       <field units="" type="NX_INT32" name="SpectrumLong">
          <strategy mode="STEP"  compression="true"   shuffle="false" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong"/>
          </datasource>
        </field>

       <field units="" type="NX_UINT32" name="SpectrumULong">
          <strategy mode="STEP"   compression="true"  grows="1" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumULong"/>
          </datasource>
        </field>




       <field units="" type="NX_INT64" name="SpectrumLong64">
          <strategy mode="STEP"  compression="true"  grows="2" shuffle="True"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT32" name="SpectrumFloat">
          <strategy mode="STEP" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumFloat"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT64" name="SpectrumDouble">
          <strategy mode="STEP"  compression="true"  grows="1" shuffle="false"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumDouble"/>
          </datasource>
        </field>

       <field units="" type="NX_CHAR" name="SpectrumString">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumString"/>
          </datasource>
        </field>

        <field units="" type="NX_INT32" name="SpectrumEncoded">
          <strategy mode="STEP"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
            <record name="SpectrumEncoded"/>
            <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" encoding="UINT32"/>
          </datasource>
        </field>



       <field units="" type="NX_INT64" name="InitSpectrumLong64">
          <strategy mode="INIT"  compression="true"  shuffle="True"/>
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumLong64"/>
          </datasource>
        </field>


       <field units="" type="NX_FLOAT32" name="FinalSpectrumFloat">
          <strategy mode="FINAL" />
          <dimensions rank="1" />
          <datasource type="TANGO">
           <device hostname="localhost" member="attribute" name="stestp09/testss/s1r228" port="10000" />
           <record name="SpectrumFloat"/>
          </datasource>
        </field>


      </group>
    </group>
  </group>
</definition>
"""

        self._simps.dp.SpectrumBoolean = self._logical[0]
        self._simps.dp.SpectrumUChar = self._mca2[0]
        self._simps.dp.SpectrumShort = self._mca1[0]
        self._simps.dp.SpectrumUShort = self._mca2[0]
        self._simps.dp.SpectrumLong = self._mca1[0]
        self._simps.dp.SpectrumULong = self._mca2[0]
        self._simps.dp.SpectrumLong64 = self._mca1[0]
# ULong64 not supported by PyTango 7.2.3
#        self._simps.dp.SpectrumULong64 = self._mca2[0]
        self._simps.dp.SpectrumFloat = self._fmca1[0]
        self._simps.dp.SpectrumDouble = self._fmca1[0]
        self._simps.dp.SpectrumString = self._dates[0]

#        print self._fmca1[0]
        tdw = self.openWriter(fname, xml)

        import PyTango
        dp = PyTango.DeviceProxy("stestp09/testss/s1r228")

        steps = min(len(self._logical), len(self._mca1), len(self._mca2), len(self._dates))
        for i in range(steps):
            self._simps.dp.SpectrumBoolean = self._logical[i]
            self._simps.dp.SpectrumUChar = self._mca2[i]
            self._simps.dp.SpectrumShort = self._mca1[i]
            self._simps.dp.SpectrumUShort = self._mca2[i]
            self._simps.dp.SpectrumLong = self._mca1[i]
            self._simps.dp.SpectrumULong = self._mca2[i]
            self._simps.dp.SpectrumLong64 = self._mca1[i]
            self._simps.dp.SpectrumFloat = self._fmca1[i]
            self._simps.dp.SpectrumDouble = self._fmca1[i]
            self._simps.dp.SpectrumString = self._dates[i]

            self.record(tdw,'{}')

        self.closeWriter(tdw)
        
        # check the created file
        
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkScalarTree(f, fname , 16)
        self._sc.checkSpectrumField(det, "SpectrumBoolean", "bool", "NX_BOOLEAN", self._logical[:steps])
        self._sc.checkSpectrumField(det, "SpectrumUChar", "uint8", "NX_UINT8", self._mca2[:steps], 
                                    grows = 2)
        self._sc.checkSpectrumField(det, "SpectrumShort", "int16", "NX_INT16", self._mca1[:steps], 
                                    grows = 3)
        self._sc.checkSpectrumField(det, "SpectrumUShort", "uint16", "NX_UINT16", self._mca2[:steps], 
                                    grows = 2)
        self._sc.checkSpectrumField(det, "SpectrumLong", "int32", "NX_INT32", self._mca1[:steps])
        self._sc.checkSpectrumField(det, "SpectrumULong", "uint32", "NX_UINT32", self._mca2[:steps],
                                    grows = 1)
        self._sc.checkSpectrumField(det, "SpectrumLong64", "int64", "NX_INT64", self._mca1[:steps], 
                                    grows = 2)
        self._sc.checkSpectrumField(det, "SpectrumFloat", "float32", "NX_FLOAT32", self._fmca1[:steps], 
                                    error = 1e-6)
        self._sc.checkSpectrumField(det, "SpectrumDouble", "float64", "NX_FLOAT64", self._fmca1[:steps], 
                                    grows = 1, error = 1e-14)
        self._sc.checkSpectrumField(det, "SpectrumDouble", "float64", "NX_FLOAT64", self._fmca1[:steps], 
                                    error = 1e-14)
        
        self._sc.checkStringSpectrumField(det, "SpectrumString", "string", "NX_CHAR", self._dates[:steps])
        # writing encoded attributes not supported for PyTango 7.2.3

        self._sc.checkSpectrumField(det, "SpectrumEncoded", "int32", "NX_INT32", [self._encoded for c in range(steps)])

        self._sc.checkSingleSpectrumField(det, "InitSpectrumLong64", "int64", "NX_INT64", self._mca1[0])

        self._sc.checkSingleSpectrumField(det, "FinalSpectrumFloat", "float32", "NX_FLOAT32", self._fmca1[steps-1],
                                          error =1.0e-06)

        f.close()
#        os.remove(fname)




if __name__ == '__main__':
    unittest.main()
