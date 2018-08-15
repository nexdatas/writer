#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \package test nexdatas
# \file XMLFieldTagWriterTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct

try:
    from pni.io.nx.h5 import open_file
except:
    from pni.nx.h5 import open_file

from xml.sax import SAXParseException


from nxswriter import Types
from nxswriter.TangoDataWriter import TangoDataWriter
from Checkers import Checker


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class XMLFieldTagWriterTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._sc = Checker(self)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")
        print("CHECKER SEED = %s" % self._sc.seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # opens writer
    # \param fname file name
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer instance
    def openWriter(self, fname, xml, json=None):
        tdw = TangoDataWriter()
        tdw.fileName = fname
        tdw.openFile()
        tdw.xmlsettings = xml
        if json:
            tdw.jsonrecord = json
        tdw.openEntry()
        return tdw

    # closes writer
    # \param tdw Tango Data Writer instance
    # \param json JSON Record with client settings
    def closeWriter(self, tdw, json=None):
        if json:
            tdw.jsonrecord = json
        tdw.closeEntry()
        tdw.closeFile()

    # performs one record step
    def record(self, tdw, string):
        tdw.record(string)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_xmlScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
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
        <field units="m" type="NX_FLOAT" name="float">
         -12.3
        </field>
        <field units="m" type="NX_FLOAT32" name="float32">
         -12.3
        </field>
        <field units="m" type="NX_FLOAT64" name="float64">
         -12.3
        </field>
        <field units="m" type="NX_NUMBER" name="number">
         -12.3
        </field>

        <field units="m" type="NX_DATE_TIME" name="time">
             string, string
        </field>
        <field units="m" type="ISO8601" name="isotime">
             string, string
        </field>
        <field units="m" type="NX_CHAR" name="string_time">
             string, string
        </field>
        <field units="m" type="NX_BOOLEAN" name="flags">
          True
        </field>


      </group>
    </group>
  </group>
</definition>
"""

        uc = 12
        mc = -12
        fc = -12.3
        string = "string, string"
        tdw = self.openWriter(fname, xml)

        flip = True
        for c in range(4):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file

        f = open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 19)
        self._sc.checkXMLScalarField(det, "counter", "int64", "NX_INT", mc,
                                     attrs={"type": "NX_INT", "units": "m"})
        self._sc.checkXMLScalarField(det, "counter8", "int8", "NX_INT8", mc,
                                     attrs={"type": "NX_INT8", "units": "m"})
        self._sc.checkXMLScalarField(det, "counter16", "int16", "NX_INT16", mc,
                                     attrs={"type": "NX_INT16", "units": "m"})
        self._sc.checkXMLScalarField(det, "counter32", "int32", "NX_INT32", mc,
                                     attrs={"type": "NX_INT32", "units": "m"})
        self._sc.checkXMLScalarField(det, "counter64", "int64", "NX_INT64", mc,
                                     attrs={"type": "NX_INT64", "units": "m"})
        self._sc.checkXMLScalarField(det, "ucounter", "uint64", "NX_UINT", uc,
                                     attrs={"type": "NX_UINT", "units": "m"})
        self._sc.checkXMLScalarField(det, "ucounter8", "uint8", "NX_UINT8", uc,
                                     attrs={"type": "NX_UINT8", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "ucounter16", "uint16", "NX_UINT16", uc,
                                     attrs={"type": "NX_UINT16", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "ucounter32", "uint32", "NX_UINT32", uc,
                                     attrs={"type": "NX_UINT32", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "ucounter64", "uint64", "NX_UINT64", uc,
                                     attrs={"type": "NX_UINT64", "units": "m"})

        self._sc.checkXMLScalarField(
            det, "float", "float64", "NX_FLOAT", fc, 1.0e-14,
                                     attrs={"type": "NX_FLOAT", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "float64", "float64", "NX_FLOAT64", fc, 1.0e-14,
                                     attrs={"type": "NX_FLOAT64", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "float32", "float32", "NX_FLOAT32", fc, 1.0e-06,
                                     attrs={"type": "NX_FLOAT32", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "number", "float64", "NX_NUMBER", fc, 1.0e-14,
                                     attrs={"type": "NX_NUMBER", "units": "m"})

        self._sc.checkXMLScalarField(
            det, "time", "string", "NX_DATE_TIME", string,
                                     attrs={"type": "NX_DATE_TIME", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "isotime", "string", "ISO8601", string,
                                     attrs={"type": "ISO8601", "units": "m"})
        self._sc.checkXMLScalarField(
            det, "string_time", "string", "NX_CHAR", string,
                                     attrs={"type": "NX_CHAR", "units": "m"})
        self._sc.checkXMLScalarField(det, "flags", "bool", "NX_BOOLEAN", True,
                                     attrs={"type": "NX_BOOLEAN", "units": "m"})

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_xmlAttrScalar(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <attribute type="NX_FLOAT" name="scalar_float">
            -1.3e-1
        </attribute>
        <attribute type="NX_CHAR" name="scalar_string">
          Let's go.
        </attribute>
        <attribute type="NX_INT" name="scalar_int">
          -12
        </attribute>
        <attribute type="NX_BOOLEAN" name="flag">
           True
        </attribute>
      </group>
      <field type="NX_FLOAT" name="counter">
        <attribute type="NX_FLOAT32" name="scalar_float32">
            -1.3e-1
        </attribute>
        <attribute type="NX_CHAR" name="scalar_string">
          Let's go.
        </attribute>
        <attribute type="NX_INT8" name="scalar_int8">
          -12
        </attribute>
        1.2
      </field>
    </group>
  </group>
</definition>
"""
        fls = -1.3e-1
        ins = -12
        sts = "Let's go."
        ls = True

        tdw = self.openWriter(fname, xml)
        for i in range(3):
            self.record(tdw, '{}')

        self.closeWriter(tdw)

        # check the created file
        f = open_file(fname, readonly=True)
        det, field = self._sc.checkAttributeTree(f, fname, 4, 3)
        self._sc.checkScalarAttribute(
            det, "scalar_float", "float64", fls, error=1.e-14)
        self._sc.checkScalarAttribute(det, "scalar_string", "string", sts)
        self._sc.checkScalarAttribute(det, "scalar_int", "int64", ins)
        self._sc.checkScalarAttribute(det, "flag", "bool", ls)
        self._sc.checkScalarAttribute(
            field, "scalar_float32", "float32", fls, error=1.e-6)
        self._sc.checkScalarAttribute(field, "scalar_string", "string", sts)
        self._sc.checkScalarAttribute(field, "scalar_int8", "int8", ins)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_xmlSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_INT" name="mca_int">
          <dimensions rank="1">
            <dim value="5" index="1"/>
          </dimensions>
            1 2 3 4 5
        </field>
        <field units="" type="NX_INT8" name="mca_int8">
          <strategy mode="INIT" compression="true"/>
          <dimensions rank="1">
            <dim value="5" index="1"/>
          </dimensions>
            1 2 3 4 5
        </field>
        <field units="" type="NX_INT16" name="mca_int16">
          <dimensions rank="1" />
            1 2 3 4 5
        </field>
        <field units="" type="NX_INT32" name="mca_int32">
          <dimensions rank="1">
            <dim value="5" index="1"/>
          </dimensions>
            1 2 3 4 5
        </field>
        <field units="" type="NX_INT64" name="mca_int64">
          <dimensions rank="1"/>
            1 2 3 4 5
        </field>

        <field units="" type="NX_UINT" name="mca_uint">
          <strategy mode="INIT" compression="true" rate="2"/>
          <dimensions rank="1">
            <dim value="5" index="1"/>
          </dimensions>
            1 2 3 4 5
        </field>
        <field units="" type="NX_UINT8" name="mca_uint8">
          <dimensions rank="1"/>
            1 2 3 4 5
        </field>
        <field units="" type="NX_UINT16" name="mca_uint16">
          <dimensions rank="1">
            <dim value="5" index="1"/>
          </dimensions>
            1 2 3 4 5
        </field>
        <field units="" type="NX_UINT32" name="mca_uint32">
          <dimensions rank="1">
          </dimensions>
            1 2 3 4 5
        </field>
        <field units="" type="NX_UINT64" name="mca_uint64">
          <strategy mode="INIT" compression="true" rate="5" shuffle="false"/>
          <dimensions rank="1">
            <dim value="5" index="1"/>
          </dimensions>
            1 2 3 4 5
        </field>

        <field units="" type="NX_INT64" name="mca_int64_dim">
          <dimensions rank="1"/>
            1 2 3 4 5
        </field>



        <field units="" type="NX_FLOAT" name="mca_float">
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="INIT" compression="true" rate="3"/>
           2.344e-4 234.34 -34.4e+3  -0.34
        </field>
        <field units="" type="NX_FLOAT32" name="mca_float32">
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="INIT" compression="true" grows="2" shuffle="true"/>
           2.344e-4 234.34 -34.4e+3  -0.34
        </field>
        <field units="" type="NX_FLOAT64" name="mca_float64">
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="INIT" grows="2"/>
           2.344e-4 234.34 -34.4e+3  -0.34
        </field>
        <field units="" type="NX_NUMBER" name="mca_number">
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="INIT" />
           2.344e-4 234.34 -34.4e+3  -0.34
        </field>

        <field units="" type="NX_FLOAT" name="mca_float_dim">
          <dimensions rank="1"/>
          <strategy mode="FINAL" />
           2.344e-4 234.34 -34.4e+3  -0.34
        </field>

        <field units="" type="NX_DATE_TIME" name="time">
          <strategy mode="INIT" compression="true" rate="3"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          Let's us check it,.
        </field>



        <field units="" type="ISO8601" name="isotime">
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          Let's us check it,.
        </field>
        <field units="" type="NX_CHAR" name="string_time">
          <strategy mode="STEP" grows="2"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          Let's us check it,.
        </field>



        <field units="" type="NX_BOOLEAN" name="flags">
          <strategy mode="STEP"/>
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="STEP" />
          True False 1  0
        </field>

        <field units="" type="NX_BOOLEAN" name="flags_dim">
          <dimensions rank="1" />
          <strategy mode="STEP" />
          True False 1  0
        </field>

        <field units="" type="NX_CHAR" name="string_time_dim">
          <strategy mode="STEP" grows="2"/>
          <dimensions rank="1"/>
          Let's us check it,.
        </field>








      </group>
    </group>
  </group>
</definition>
"""

        spec = [2.344e-4, 234.34, -34.4e+3, -0.34]
        string = ["Let's", "us", "check", "it,."]

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{}')

        self.closeWriter(tdw)

        # check the created file

        f = open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 22)
        self._sc.checkXMLSpectrumField(
            det, "mca_int", "int64", "NX_INT", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_INT", "units": ""})
        self._sc.checkXMLSpectrumField(
            det, "mca_int8", "int8", "NX_INT8", [1, 2, 3, 4, 5])
        self._sc.checkXMLSpectrumField(
            det, "mca_int16", "int16", "NX_INT16", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_INT16", "units": ""})
        self._sc.checkXMLSpectrumField(
            det, "mca_int32", "int32", "NX_INT32", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_INT32", "units": ""})
        self._sc.checkXMLSpectrumField(
            det, "mca_int64", "int64", "NX_INT64", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_INT64", "units": ""})
        self._sc.checkXMLSpectrumField(
            det, "mca_uint", "uint64", "NX_UINT", [1, 2, 3, 4, 5])
        self._sc.checkXMLSpectrumField(
            det, "mca_uint8", "uint8", "NX_UINT8", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_UINT8", "units": ""})
        self._sc.checkXMLSpectrumField(
            det, "mca_uint16", "uint16", "NX_UINT16", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_UINT16", "units": ""})
        self._sc.checkXMLSpectrumField(
            det, "mca_uint32", "uint32", "NX_UINT32", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_UINT32", "units": ""})
        self._sc.checkXMLSpectrumField(
            det, "mca_uint64", "uint64", "NX_UINT64", [1, 2, 3, 4, 5])
        self._sc.checkXMLSpectrumField(
            det, "mca_int64_dim", "int64", "NX_INT64", [1, 2, 3, 4, 5],
                                     attrs={"type": "NX_INT64", "units": ""})

        self._sc.checkXMLSpectrumField(
            det, "mca_float", "float64", "NX_FLOAT", spec,
                                    error=1.0e-14)
        self._sc.checkXMLSpectrumField(
            det, "mca_float_dim", "float64", "NX_FLOAT", spec,
                                    error=1.0e-14)
        self._sc.checkXMLSpectrumField(
            det, "mca_float32", "float32", "NX_FLOAT32", spec,
                                    error=1.0e-5)
        self._sc.checkXMLSpectrumField(
            det, "mca_float64", "float64", "NX_FLOAT64", spec,
                                    error=1.0e-14)
        self._sc.checkXMLSpectrumField(
            det, "mca_number", "float64", "NX_NUMBER", spec,
                                    error=1.0e-14)

        self._sc.checkXMLSpectrumField(det, "flags", "bool", "NX_BOOLEAN",
                                       [True, False, True, False])
        self._sc.checkXMLSpectrumField(
            det, "time", "string", "NX_DATE_TIME", string)
        self._sc.checkXMLSpectrumField(
            det, "string_time", "string", "NX_CHAR", string)
        self._sc.checkXMLSpectrumField(
            det, "isotime", "string", "ISO8601", string)
        self._sc.checkXMLSpectrumField(
            det, "string_time_dim", "string", "NX_CHAR", string)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_xmlAttrSpectrum(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <attribute type="NX_FLOAT" name="spectrum_float">
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
           2.344e-4 234.34 -34.4e+3  -0.34
        </attribute>
        <attribute type="NX_INT32" name="init_spectrum_int32">
          <dimensions rank="1" />
          <strategy mode="INIT"/>
            1 2 3 4 5
        </attribute>
        <attribute type="NX_BOOLEAN" name="spectrum_bool">
          <dimensions rank="1">
            <dim value="4" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          True False 1  0
        </attribute>

      </group>
      <field type="NX_FLOAT" name="counter">
        <attribute type="NX_FLOAT32" name="spectrum_float32">
          <dimensions rank="1" />
          <strategy mode="STEP"/>
           2.344e-4 234.34 -34.4e+3  -0.34
        </attribute>
        <attribute type="NX_UINT64" name="final_spectrum_uint64">
          <dimensions rank="1">
            <dim value="5" index="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
            1 2 3 4 5
        </attribute>
        <attribute type="NX_BOOLEAN" name="final_spectrum_bool">
          <dimensions rank="1" />
          <strategy mode="FINAL"/>
          True False 1  0
        </attribute>
        1.2
      </field>
    </group>
  </group>
</definition>
"""

#        <attribute type="NX_CHAR" name="flag_spectrum_string">
#          <dimensions rank="1">
#            <dim value="8" index="1"/>
#          </dimensions>
#        </attribute>

        spec = [2.344e-4, 234.34, -34.4e+3, -0.34]
        ins = [1, 2, 3, 4, 5]
        ls = [True, False, True, False]

        tdw = self.openWriter(fname, xml)
        for i in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file
        f = open_file(fname, readonly=True)
        det, field = self._sc.checkAttributeTree(f, fname, 3, 3)
        self._sc.checkSpectrumAttribute(det, "spectrum_float", "float64", spec,
                                        error=1.e-14)
        self._sc.checkSpectrumAttribute(
            det, "init_spectrum_int32", "int32", ins)
        self._sc.checkSpectrumAttribute(det, "spectrum_bool", "bool", ls)
        self._sc.checkSpectrumAttribute(
            field, "spectrum_float32", "float32", spec,
                                      error=1.e-5)
        self._sc.checkSpectrumAttribute(
            field, "final_spectrum_uint64", "uint64", ins)
        self._sc.checkSpectrumAttribute(
            field, "final_spectrum_bool", "bool", ls)
        # NOT SUPPORTED BY PNINX
# self._sc.checkSpectrumAttribute(field, "flag_spectrum_string", "string",
# logical)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_xmlImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <field units="" type="NX_INT" name="pco_int">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          11 12
          21 22
          31 32
        </field>

        <field units="" type="NX_INT8" name="pco_int8">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP" grows="2"/>
          11 12
          21 22
          31 32
        </field>
        <field units="" type="NX_INT16" name="pco_int16">
          <dimensions rank="2" />
          <strategy mode="STEP" compression="true" grows="3"/>
          11 12
          21 22
          31 32
        </field>
        <field units="" type="NX_INT32" name="pco_int32">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true"  grows="2" shuffle="false" />
          11 12
          21 22
          31 32
        </field>
        <field units="" type="NX_INT64" name="pco_int64">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"/>
          11 12
          21 22
          31 32
        </field>

        <field units="" type="NX_UINT" name="pco_uint">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          11 12
          21 22
          31 32
        </field>
        <field units="" type="NX_UINT8" name="pco_uint8">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP" grows="3"/>
          11 12
          21 22
          31 32
        </field>
        <field units="" type="NX_UINT16" name="pco_uint16">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true"/>
          11 12
          21 22
          31 32
        </field>
        <field units="" type="NX_UINT32" name="pco_uint32">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true"  grows="2" shuffle="false" />
          11 12
          21 22
          31 32
        </field>
        <field units="" type="NX_UINT64" name="pco_uint64">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"  grows="3"/>
          11 12
          21 22
          31 32
        </field>



        <field units="" type="NX_FLOAT" name="pco_float">
          <dimensions rank="2">
            <dim value="2" index="1"/>
            <dim value="3" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" rate="3"/>
          -3.43 -3.3e-1 53.1
          3.43e+02 3.13e-1 53
        </field>
        <field units="" type="NX_FLOAT32" name="pco_float32">
          <dimensions rank="2">
            <dim value="2" index="1"/>
            <dim value="3" index="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"/>
          -3.43 -3.3e-1 53.1
          3.43e+02 3.13e-1 53
        </field>
        <field units="" type="NX_FLOAT64" name="pco_float64">
          <dimensions rank="2" />
          <strategy mode="STEP" grows="3"/>
          -3.43 -3.3e-1 53.1
          3.43e+02 3.13e-1 53
        </field>
        <field units="" type="NX_NUMBER" name="pco_number">
          <dimensions rank="2">
            <dim value="2" index="1"/>
            <dim value="3" index="2"/>
          </dimensions>
          <strategy mode="STEP"  grows = "1" />
          -3.43 -3.3e-1 53.1
          3.43e+02 3.13e-1 53
        </field>



        <field units="" type="NX_DATE_TIME" name="time">
          <strategy mode="STEP" compression="true" rate="3"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          Let's us check it,
          and test it here.
          , . : ;
        </field>
        <field units="" type="ISO8601" name="isotime">
          <strategy mode="STEP" compression="true" grows="2" shuffle="true"/>
          <dimensions rank="2" />
          Let's us check it,
          and test it here.
          , . : ;
        </field>
        <field units="" type="NX_CHAR" name="string_time">
          <strategy mode="STEP" grows="2"/>
          <dimensions rank="2"/>
          Let's us check it,
          and test it here.
          , . : ;
        </field>

        <field units="" type="NX_BOOLEAN" name="flags">
          <strategy mode="STEP"/>
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
         True False 1 0
         FALSE TRUE false true
         0 1 1 0
        </field>

        <field units="" type="NX_BOOLEAN" name="flags_dim">
          <strategy mode="STEP"/>
          <dimensions rank="2" />
         True False 1 0
         FALSE TRUE false true
         0 1 1 0
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        image = [[11, 12], [21, 22], [31, 32]]
        fimage = [[-3.43, -3.3e-1, 53.1], [3.43e+02, 3.13e-1, 53]]
        simage = [["Let's", "us", "check", "it,"],
                  ["and", "test", "it", "here."],
                  [",", ".", ":", ";"]]
        bimage = [[True, False, True, False],
                  [False, True, False, True],
                  [False, True, True, False]]

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw, '{}')

        self.closeWriter(tdw)

        # check the created file

        f = open_file(fname, readonly=True)
        det = self._sc.checkFieldTree(f, fname, 19)
        self._sc.checkXMLImageField(det, "pco_int", "int64", "NX_INT", image)
        self._sc.checkXMLImageField(det, "pco_int8", "int8", "NX_INT8", image)
        self._sc.checkXMLImageField(
            det, "pco_int16", "int16", "NX_INT16", image)
        self._sc.checkXMLImageField(
            det, "pco_int32", "int32", "NX_INT32", image)
        self._sc.checkXMLImageField(
            det, "pco_int64", "int64", "NX_INT64", image)
        self._sc.checkXMLImageField(
            det, "pco_uint", "uint64", "NX_UINT", image)
        self._sc.checkXMLImageField(
            det, "pco_uint8", "uint8", "NX_UINT8", image)
        self._sc.checkXMLImageField(
            det, "pco_uint16", "uint16", "NX_UINT16", image)
        self._sc.checkXMLImageField(
            det, "pco_uint32", "uint32", "NX_UINT32", image)
        self._sc.checkXMLImageField(
            det, "pco_uint64", "uint64", "NX_UINT64", image)

        self._sc.checkXMLImageField(
            det, "pco_float", "float64", "NX_FLOAT", fimage,
                                    error=1.0e-14)
        self._sc.checkXMLImageField(
            det, "pco_float32", "float32", "NX_FLOAT32", fimage,
                                    error=1.0e-5)
        self._sc.checkXMLImageField(
            det, "pco_float64", "float64", "NX_FLOAT64", fimage,
                                    error=1.0e-14)
        self._sc.checkXMLImageField(
            det, "pco_number", "float64", "NX_NUMBER", fimage,
                                    error=1.0e-14)

        self._sc.checkXMLImageField(det, "flags", "bool", "NX_BOOLEAN", bimage)
        self._sc.checkXMLImageField(
            det, "time", "string", "NX_DATE_TIME", simage)
        self._sc.checkXMLImageField(
            det, "string_time", "string", "NX_CHAR", simage)
        self._sc.checkXMLImageField(
            det, "isotime", "string", "ISO8601", simage)
        self._sc.checkXMLImageField(
            det, "flags_dim", "bool", "NX_BOOLEAN", bimage)

        f.close()
        os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_xmlAttrImage(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        xml = """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">
        <attribute type="NX_FLOAT" name="image_float">
          <dimensions rank="2">
            <dim value="2" index="1"/>
            <dim value="3" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          -3.43 -3.3e-1 53.1
          3.43e+02 3.13e-1 53
        </attribute>

        <attribute type="NX_INT" name="image_int">
          <dimensions rank="2" />
          <strategy mode="FINAL"/>
          11 12
          21 22
          31 32
        </attribute>

        <attribute type="NX_INT32" name="image_int32">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          11 12
          21 22
          31 32
        </attribute>



        <attribute type="NX_BOOLEAN" name="image_bool">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
         True False 1 0
         FALSE TRUE false true
         0 1 1 0
        </attribute>

      </group>
      <field type="NX_FLOAT" name="counter">
        <attribute type="NX_FLOAT32" name="image_float32">
          <dimensions rank="2" />
          <strategy mode="STEP"/>
          -3.43 -3.3e-1 53.1
          3.43e+02 3.13e-1 53
        </attribute>

        <attribute type="NX_UINT32" name="image_uint32">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="2" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          11 12
          21 22
          31 32
        </attribute>

        <attribute type="NX_UINT64" name="image_uint64">
          <dimensions rank="2"/>
          <strategy mode="FINAL"/>
          11 12
          21 22
          31 32
        </attribute>


        <attribute type="NX_BOOLEAN" name="image_bool">
          <dimensions rank="2">
            <dim value="3" index="1"/>
            <dim value="4" index="2"/>
          </dimensions>
          <strategy mode="INIT"/>
         True False 1 0
         FALSE TRUE false true
         0 1 1 0
        </attribute>

        1.2
      </field>
    </group>
  </group>
</definition>
"""

#        <attribute type="NX_CHAR" name="flag_spectrum_string">
#          <dimensions rank="1">
#            <dim value="8" index="1"/>
#          </dimensions>
#          <strategy mode="STEP"/>
#        </attribute>

        image = [[11, 12], [21, 22], [31, 32]]
        fimage = [[-3.43, -3.3e-1, 53.1], [3.43e+02, 3.13e-1, 53]]
        bimage = [[True, False, True, False],
                  [False, True, False, True],
                  [False, True, True, False]]

        tdw = self.openWriter(fname, xml)
        for i in range(3):
            self.record(tdw, '{ }')

        self.closeWriter(tdw)

        # check the created file
        f = open_file(fname, readonly=True)
        det, field = self._sc.checkAttributeTree(f, fname, 4, 4)
        self._sc.checkImageAttribute(det, "image_float", "float64", fimage,
                                     error=1.e-14)
        self._sc.checkImageAttribute(det, "image_int", "int64", image)
        self._sc.checkImageAttribute(det, "image_bool", "bool", bimage)
        self._sc.checkImageAttribute(det, "image_int32", "int32", image)
        self._sc.checkImageAttribute(field, "image_float32", "float32", fimage,
                                     error=1.e-5)
        self._sc.checkImageAttribute(field, "image_uint32", "uint32", image)
        self._sc.checkImageAttribute(field, "image_uint64", "uint64", image)
        self._sc.checkImageAttribute(field, "image_bool", "bool", bimage)
        # STRING NOT SUPPORTED BY PNINX

        f.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
