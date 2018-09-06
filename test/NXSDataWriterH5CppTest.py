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
# \file NXSDataWriterTest.py
# unittests for NXSDataWriter
#
import unittest
import os
import sys
import json
import numpy

import PyTango
try:
    from ProxyHelper import ProxyHelper
except:
    from .ProxyHelper import ProxyHelper

import struct

import nxswriter.H5CppWriter as H5CppWriter


try:
    import ServerSetUp
except:
    from . import ServerSetUp

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class NXSDataWriterH5CppTest(unittest.TestCase):
    # server counter
    serverCounter = 0

    # constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        NXSDataWriterH5CppTest.serverCounter += 1
        sins = self.__class__.__name__ + \
            "%s" % NXSDataWriterH5CppTest.serverCounter
        self._sv = ServerSetUp.ServerSetUp("testp09/testtdw/" + sins, sins)

        self.__status = {
            PyTango.DevState.OFF: "Not Initialized",
            PyTango.DevState.ON: "Ready",
            PyTango.DevState.OPEN: "File Open",
            PyTango.DevState.EXTRACT: "Entry Open",
            PyTango.DevState.RUNNING: "Writing ...",
            PyTango.DevState.FAULT: "Error",
        }

        self._scanXmlb = """
<definition>
  <group type="NXentry" name="entry%s">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="%s://entry%s/instrument/detector/counter1" name="cnt1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""

        self._scanXml = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="%s://entry1/instrument/detector/mca" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="/NXentry/NXinstrument/NXdetector/counter1" name="counter1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""

        self._scanXml1 = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="/entry1/instrument/detector/counter1" name="cnt1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""
        self._scanXml3 = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute>
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_INT64" name="image">
          <dimensions rank="2">
            <dim value="100" index="1"/>
            <dim value="200" index="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="image"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/image" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="%s://entry1/instrument/detector/counter1" name="cnt1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""

        self._counter = [0.1, 0.2]
        self._mca1 = [e * 0.1 for e in range(2048)]
        self._mca2 = [(float(e) / (100. + e)) for e in range(2048)]
        self._image1 = [[(i + j) for i in range(100)] for j in range(200)]
        self._image2 = [[(i - j) for i in range(100)] for j in range(200)]
        self._image1a = [[(i + j) for i in range(200)] for j in range(100)]
        self._image2a = [[(i - j) for i in range(200)] for j in range(100)]

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up of Tango Server
    def setUp(self):
        self._sv.setUp()

    # test closer
    # \brief Common tear down oif Tango Server
    def tearDown(self):
        self._sv.tearDown()

    def setProp(self, rc, name, value):
        db = PyTango.Database()
        name = "" + name[0].upper() + name[1:]
        db.put_device_property(
            self._sv.new_device_info_writer.name,
            {name: value})
        rc.Init()

    # Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error = False
            method(*args, **kwargs)
        except Exception:
            error = True
        self.assertEqual(error, True)

    # openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        try:
            fname = '%s/test.h5' % os.getcwd()
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            dp.OpenFile()
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.XMLSettings, "")
            self.assertEqual(dp.JSONRecord, "{}")
            dp.CloseFile()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file
            f = H5CppWriter.open_file(fname, readonly=True)
#            self.assertEqual(f.name, fname)
            f = f.root()
#            self.assertEqual(f.path, fname)

#            print("\nFile attributes:")
            cnt = 0
            for at in f.attributes:
                cnt += 1
#                print(at.name),"=",at[...]
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(6, len(f.attributes))
#            print ""

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFileDir(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        directory = '#nexdatas_test_directory#'
        dirCreated = False
        dirExists = False

        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                dirCreated = True
                dirExists = True
            except:
                pass
        else:
            dirExists = True

        if dirExists:
            fname = '%s/%s/%s%s.h5' % (
                os.getcwd(), directory, self.__class__.__name__, fun)
        else:
            fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)

        if dirCreated:
            fname = '%s/%s/%s%s.h5' % (
                os.getcwd(), directory, self.__class__.__name__, fun)
        else:
            fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)

        try:
            fname = '%s/test.h5' % os.getcwd()
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            dp.OpenFile()
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.XMLSettings, "")
            self.assertEqual(dp.JSONRecord, "{}")
            dp.CloseFile()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file
            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            #            self.assertEqual(f.name, fname)
#            self.assertEqual(f.path, fname)

#            print("\nFile attributes:")
            cnt = 0
            for at in f.attributes:
                cnt += 1
#                print(at.name),"=",at[...]
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(6, len(f.attributes))
#            print ""

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

            if dirCreated:
                os.removedirs(directory)

    # openEntry test
    # \brief It tests validation of opening and closing entry in H5 files.
    def test_openEntry(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/test2.h5' % os.getcwd()
        xml = '<definition> <group type="NXentry" name="entry"/></definition>'
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = xml
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenEntry()
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)

            dp.CloseEntry()
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            dp.CloseFile()
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.state(), PyTango.DevState.ON)

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            #            self.assertEqual(f.path, fname)

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 2)

            cnt = 0
            for ch in f:
                self.assertTrue(ch.is_valid)
                cnt += 1
                if ch.name == "entry":
                    self.assertEqual(ch.name, "entry")
                    self.assertEqual(len(ch.attributes), 1)
                    for at in ch.attributes:
                        self.assertTrue(at.is_valid)
                        self.assertTrue(hasattr(at.shape, "__iter__"))
                        self.assertEqual(len(at.shape), 1)
                        self.assertEqual(at.shape, (1,))
                        self.assertEqual(at.dtype, "string")
                    #                    self.assertEqual(at.dtype,"string")
                        self.assertEqual(at.name, "NX_class")
                        self.assertEqual(at[...], "NXentry")
                else:
                    self.assertEqual(ch.name, "nexus_logs")
                    ch2 = ch.open("configuration")
                    for c in ch2:
                        if c.name == "nexus__entry__1_xml":
                            self.assertEqual(
                                c.read(),
                                '<definition> '
                                '<group type="NXentry" name="entry"/>'
                                '</definition>')
                            print(c.read())
                        else:
                            self.assertEqual(c.name, "python_version")
                            self.assertEqual(c.read(), sys.version)

                    self.assertEqual(len(ch.attributes), 1)
                    for at in ch.attributes:
                        self.assertTrue(at.is_valid)
                        self.assertTrue(hasattr(at.shape, "__iter__"))
                        self.assertEqual(len(at.shape), 1)
                        self.assertEqual(at.shape, (1,))
                        self.assertEqual(at.dtype, "string")
                    #                    self.assertEqual(at.dtype,"string")
                        self.assertEqual(at.name, "NX_class")
                        self.assertEqual(at[...], "NXcollection")

            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # openEntryWithSAXParseException test
    # \brief It tests validation of opening and closing entry
    # with SAXParseException
    def test_openEntryWithSAXParseException(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/test2.h5' % os.getcwd()
        wrongXml = """Ala ma kota."""
        xml = """<definition/>"""
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            try:
                error = None
                dp.XMLSettings = wrongXml
            except PyTango.DevFailed:
                error = True
            except Exception:
                error = False
            self.assertEqual(error, True)
            self.assertTrue(error is not None)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

#            dp.CloseFile()
#            dp.OpenFile()

            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = xml
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenEntry()
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
#            self.assertEqual(f.path, fname)

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1

            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_twoentries(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/scantest2.h5' % os.getcwd()
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXmlb % ("001", fname, "001")
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{"data": {"exp_c01":' + str(self._counter[0]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca1) + '  } }')
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXmlb % ("002", fname, "002")
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{"data": {"exp_c01":' + str(self._counter[0]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca1) + '  } }')
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            from nxswriter import FileWriter
            FileWriter.writer = H5CppWriter
            f = FileWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 3)

            ent = ["001", "002"]
            for et in ent:

                en = f.open("entry%s" % et)
                self.assertTrue(en.is_valid)
                self.assertEqual(en.name, "entry%s" % et)
                self.assertEqual(len(en.attributes), 1)
                self.assertEqual(en.size, 2)

                at = en.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXentry")

    # ins = f.open("entry1/instrument:NXinstrument")    #bad exception
    #            ins = f.open("entry1/instrument")
                ins = en.open("instrument")
                self.assertTrue(ins.is_valid)
                self.assertEqual(ins.name, "instrument")
                self.assertEqual(len(ins.attributes), 2)
                self.assertEqual(ins.size, 1)

                at = ins.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXinstrument")

                at = ins.attributes["short_name"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "short_name")
                self.assertEqual(at[...], "scan instrument")

                det = ins.open("detector")
                self.assertTrue(det.is_valid)
                self.assertEqual(det.name, "detector")
                self.assertEqual(len(det.attributes), 1)
                self.assertEqual(det.size, 2)

                at = det.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXdetector")

    # cnt = det.open("counter")              # bad exception
                cnt = det.open("counter1")
                self.assertTrue(cnt.is_valid)
                self.assertEqual(cnt.name, "counter1")
                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(cnt.shape), 1)
                self.assertEqual(cnt.shape, (2,))
                self.assertEqual(cnt.dtype, "float64")
                self.assertEqual(cnt.size, 2)
                value = cnt.read()
    #            value = cnt[:]
                for i in range(len(value)):
                    self.assertEqual(self._counter[i], value[i])

                self.assertEqual(len(cnt.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = cnt.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = cnt.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "m")

                at = cnt.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")

                mca = det.open("mca")
                self.assertTrue(mca.is_valid)
                self.assertEqual(mca.name, "mca")

                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(mca.shape), 2)
                self.assertEqual(mca.shape, (2, 2048))
                self.assertEqual(mca.dtype, "float64")
                self.assertEqual(mca.size, 4096)
                value = mca.read()
                for i in range(len(value[0])):
                    self.assertEqual(self._mca1[i], value[0][i])
                for i in range(len(value[0])):
                    self.assertEqual(self._mca2[i], value[1][i])

                self.assertEqual(len(mca.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = mca.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = mca.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "")

                at = mca.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")

                dt = en.open("data")
                self.assertTrue(dt.is_valid)
                self.assertEqual(dt.name, "data")
                self.assertEqual(len(dt.attributes), 1)
                self.assertEqual(dt.size, 2)

                at = dt.attributes["NX_class"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "NX_class")
                self.assertEqual(at[...], "NXdata")

                cnt = dt.open("cnt1")
                self.assertTrue(cnt.is_valid)
                #            ???
                # self.assertEqual(cnt.name,"cnt1")
                #            self.assertEqual(cnt.name,"counter1")

                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(cnt.shape), 1)
                self.assertEqual(cnt.shape, (2,))
                self.assertEqual(cnt.dtype, "float64")
                self.assertEqual(cnt.size, 2)
    #             print(cnt.read())
                value = cnt[:]
                for i in range(len(value)):
                    self.assertEqual(self._counter[i], value[i])

                self.assertEqual(len(cnt.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = cnt.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = cnt.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "m")

                at = cnt.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")

                mca = dt.open("data")
                self.assertTrue(mca.is_valid)
                self.assertEqual(mca.name, "data")

                self.assertTrue(hasattr(cnt.shape, "__iter__"))
                self.assertEqual(len(mca.shape), 2)
                self.assertEqual(mca.shape, (2, 2048))
                self.assertEqual(mca.dtype, "float64")
                self.assertEqual(mca.size, 4096)
                value = mca.read()
                for i in range(len(value[0])):
                    self.assertEqual(self._mca1[i], value[0][i])
                for i in range(len(value[0])):
                    self.assertEqual(self._mca2[i], value[1][i])

                self.assertEqual(len(mca.attributes), 4)

                at = cnt.attributes["nexdatas_strategy"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "nexdatas_strategy")
                self.assertEqual(at[...], "STEP")

                at = mca.attributes["type"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "type")
                self.assertEqual(at[...], "NX_FLOAT")

                at = mca.attributes["units"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")
                self.assertEqual(at.name, "units")
                self.assertEqual(at[...], "")

                at = mca.attributes["nexdatas_source"]
                self.assertTrue(at.is_valid)
                self.assertTrue(hasattr(at.shape, "__iter__"))
                self.assertEqual(len(at.shape), 1)
                self.assertEqual(at.shape, (1,))
                self.assertEqual(at.dtype, "string")

            f.close()
        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/scantest2.h5' % os.getcwd()
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{"data": {"exp_c01":' + str(self._counter[0]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca1) + '  } }')
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
#            self.assertEqual(f.path, fname)
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            # ???????
            # ! PNI self.assertEqual(mca.name, "mca")
            # ????
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_skipacq(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/scantest2.h5' % os.getcwd()
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{"data": {"exp_c01":' + str(self._counter[0]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca1) + '  } }')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.FileName = fname
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            self.myAssertRaise(Exception, dp.openEntry)
            self.assertEqual(dp.state(), PyTango.DevState.FAULT)
            dp.OpenFile()
            dp.skipacquisition = True
            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.FileName = fname
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            dp.skipacquisition = True
            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.skipacquisition = True
            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.skipacquisition, False)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            # self.assertEqual(f.path, fname)
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            # ???????
            # ! PNI self.assertEqual(mca.name, "mca")
            # ????
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_source")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_canfail(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/scantest2.h5' % os.getcwd()
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml % fname
            dp.Canfail = True
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            dp.OpenEntry()
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{}')
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{}')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()

            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    value[i], numpy.finfo(getattr(numpy, 'float64')).max)

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "(u'Data for /entry1:NXentry/instrument:NXinstrument"
                "/detector:NXdetector/counter1 not found. DATASOURCE: CLIENT"
                " record exp_c01', 'Data without value')\n(u'Data for "
                "/entry1:NXentry/instrument:NXinstrument/detector:NXdetector"
                "/counter1 not found. DATASOURCE: CLIENT record exp_c01',"
                " 'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(numpy.finfo(getattr(numpy, 'float64')).max,
                                 value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(numpy.finfo(getattr(numpy, 'float64')).max,
                                 value[1][i])

            self.assertEqual(len(mca.attributes), 6)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "(u'Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/mca not found. DATASOURCE: CLIENT "
                "record p09/mca/exp.02', 'Data without value')\n(u'Data for "
                "/entry1:NXentry/instrument:NXinstrument/detector:NXdetector"
                "/mca not found. DATASOURCE: CLIENT record p09/mca/exp.02', "
                "'Data without value')")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            #            cnt = dt.open("cnt1")
            cnt = dt.open("counter1")
            self.assertTrue(cnt.is_valid)
            #            ???
            #            self.assertEqual(cnt.name,"cnt1")
            self.assertEqual(cnt.name, "counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(numpy.finfo(getattr(numpy, 'float64')).max,
                                 value[i])

            self.assertEqual(len(cnt.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = cnt.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "(u'Data for /entry1:NXentry/instrument:NXinstrument/"
                "detector:NXdetector/counter1 not found. DATASOURCE: CLIENT "
                "record exp_c01', 'Data without value')\n(u'Data for "
                "/entry1:NXentry/instrument:NXinstrument/detector:NXdetector"
                "/counter1 not found. DATASOURCE: CLIENT record exp_c01', "
                "'Data without value')")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")
            # self.assertEqual(mca.name,"mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(
                    numpy.finfo(getattr(numpy, 'float64')).max,
                    value[1][i])

            self.assertEqual(len(mca.attributes), 6)

            at = mca.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_canfail"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail")
            self.assertEqual(at[...], "FAILED")

            at = mca.attributes["nexdatas_canfail_error"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_canfail_error")
            self.assertEqual(
                at[...],
                "(u'Data for /entry1:NXentry/instrument:NXinstrument/detector"
                ":NXdetector/mca not found. DATASOURCE: CLIENT record "
                "p09/mca/exp.02', 'Data without value')\n(u'Data for "
                "/entry1:NXentry/instrument:NXinstrument/detector:NXdetector"
                "/mca not found. DATASOURCE: CLIENT record p09/mca/exp.02', "
                "'Data without value')")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()
        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_canfail_false(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/scantest2.h5' % os.getcwd()
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Canfail = False

            dp.XMLSettings = self._scanXml % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)

            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.canfail, False)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            self.myAssertRaise(Exception, dp.Record, '{}')
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.canfail, False)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.FAULT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            self.myAssertRaise(Exception, dp.Record, '{}')

            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.canfail, False)
            self.assertEqual(dp.state(), PyTango.DevState.FAULT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.state(), PyTango.DevState.FAULT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.canfail, True)
            self.assertEqual(dp.stepsperfile, 0)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.FAULT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()

            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
#            self.assertEqual(cnt.shape, (1,))
            self.assertEqual(cnt.dtype, "float64")
            # self.assertEqual(cnt.size, 1)
            cnt.read()
            # value = cnt[:]
            # for i in range(len(value)):
            #    self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            # self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
            # self.assertEqual(mca.size, 4096)
            mca.read()
            # for i in range(len(value[0])):
            #     self.assertEqual(self._mca1[i], value[0][i])
            # for i in range(len(value[0])):
            #     self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            #  cnt = dt.open("cnt1")
            cnt = dt.open("counter1")
            self.assertTrue(cnt.is_valid)
            # ???
            #  self.assertEqual(cnt.name,"cnt1")
            self.assertEqual(cnt.name, "counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            # self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            # self.assertEqual(cnt.size, 2)
            #  print(cnt.read())
            cnt[:]
            # for i in range(len(value)):
            #     self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")
#            self.assertEqual(mca.name,"mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            # self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
            # self.assertEqual(mca.size, 4096)
            mca.read()
            # for i in range(len(value[0])):
            #     self.assertEqual(self._mca1[i], value[0][i])
            # for i in range(len(value[0])):
            #     self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()
        finally:
            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecordGrow2(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = '%s/scantest2.h5' % os.getcwd()
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenEntry()
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[0], self._counter[1]]
            mcag = [self._mca1, self._mca2]
            rec = {"data": {"exp_c01": cntg, "p09/mca/exp.02": mcag}}
            dp.Record(json.dumps(rec))

            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[1], self._counter[0]]
            mcag = [self._mca2, self._mca1]
            rec = {"data": {"exp_c01": cntg, "p09/mca/exp.02": mcag}}
            dp.Record(json.dumps(rec))

            dp.CloseEntry()
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

            # ins = f.open("entry1/instrument:NXinstrument")  # bad exception
            # ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (4, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 8192)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[3][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[2][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("counter1")
            self.assertTrue(cnt.is_valid)
            #            ???
            #            self.assertEqual(cnt.name,"cnt1")
            self.assertEqual(cnt.name, "counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (4, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 8192)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[3][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[2][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord_split(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        tfname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)
        fname = None
        try:
            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = tfname

            dp.stepsPerFile = 2
            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml1
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenEntry()
            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 1)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{"data": {"exp_c01":' + str(self._counter[0]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca1) + '  } }')
            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 1)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')

            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 2)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')
            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 2)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')

            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 3)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.Record('{"data": {"exp_c01":' + str(self._counter[1]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca2) + '  } }')
            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 3)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])
            dp.Record('{"data": {"exp_c01":' + str(self._counter[0]) +
                      ', "p09/mca/exp.02":' +
                      str(self._mca1) + '  } }')

            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 4)
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseEntry()
            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 1)
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.stepsperfile, 2)
            self.assertEqual(dp.currentfileid, 0)
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            fname = '%s/%s%s_00001.h5' % (
                os.getcwd(), self.__class__.__name__, fun)
            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            #   self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()
            # check the created file

            fname = '%s/%s%s_00002.h5' % (
                os.getcwd(), self.__class__.__name__, fun)
            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()
            # check the created file

            fname = '%s/%s%s_00003.h5' % (
                os.getcwd(), self.__class__.__name__, fun)
            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "mca")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[1 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2, 2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for i in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[0][i])
            for i in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[1][i])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:
            for i in range(1, 4):
                fname = '%s/%s%s_%05d.h5' % (
                    os.getcwd(), self.__class__.__name__, fun, i)
                if os.path.isfile(fname):
                    os.remove(fname)
            if os.path.isfile(tfname):
                os.remove(tfname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecordGrow3(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "scantestgrow.h5"
        try:

            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            # self.setProp(dp, "DefaultCanFail", False)
            dp.FileName = fname
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml3 % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenEntry()
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[0], self._counter[1]]
            imageg = [self._image1a, self._image2a]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}
            dp.Record(json.dumps(rec))

            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[1], self._counter[0]]
            imageg = [self._image2a, self._image1a]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}

            dp.Record(json.dumps(rec))

            dp.CloseEntry()
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("image")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "image")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 100, 200))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 80000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[3][i][j])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 100, 200))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 80000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[3][i][j])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecordGrow3_false(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "scantestgrow.h5"
        try:

            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            self.setProp(dp, "DefaultCanFail", False)
            dp.FileName = fname
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml3 % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenEntry()
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[0], self._counter[1]]
            imageg = [self._image1a, self._image2a]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}
            dp.Record(json.dumps(rec))

            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[1], self._counter[0]]
            imageg = [self._image2a, self._image1a]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}

            dp.Record(json.dumps(rec))

            dp.CloseEntry()
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("image")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "image")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 100, 200))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 80000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[3][i][j])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 100, 200))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 80000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image2a[i][j], value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(self._image1a[i][j], value[3][i][j])

            self.assertEqual(len(mca.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)

    # scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecordGrow4(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "scantestgrow.h5"
        try:

            dp = PyTango.DeviceProxy(self._sv.device)
            self.assertTrue(ProxyHelper.wait(dp, 10000))
            #        print 'attributes', dp.attribute_list_query()
            dp.FileName = fname
            self.setProp(dp, "writer", "h5cpp")
            dp.FileName = fname
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenFile()

            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.XMLSettings = self._scanXml3 % fname
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)

            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.OpenEntry()
            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[0], self._counter[1]]
            imageg = [self._image1, self._image2]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}
            dp.Record(json.dumps(rec))

            self.assertEqual(dp.state(), PyTango.DevState.EXTRACT)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            cntg = [self._counter[1], self._counter[0]]
            imageg = [self._image2, self._image1]
            rec = {"data": {"exp_c01": cntg, "image": imageg}}

            dp.Record(json.dumps(rec))

            dp.CloseEntry()
            self.assertEqual(dp.state(), PyTango.DevState.OPEN)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            dp.CloseFile()
            self.assertEqual(dp.state(), PyTango.DevState.ON)
            self.assertEqual(dp.status(), self.__status[dp.state()])

            # check the created file

            f = H5CppWriter.open_file(fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)

            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name, "entry1")
            self.assertEqual(len(en.attributes), 1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXentry")

# ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(len(ins.attributes), 2)
            self.assertEqual(ins.size, 1)

            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXinstrument")

            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "short_name")
            self.assertEqual(at[...], "scan instrument")

            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name, "detector")
            self.assertEqual(len(det.attributes), 1)
            self.assertEqual(det.size, 2)

            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdetector")

# cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
            value = cnt.read()
#            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = det.open("image")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "image")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 200, 200))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 160000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(0, value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(9223372036854775807, value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(0, value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(9223372036854775807, value[3][i][j])

            self.assertEqual(len(mca.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name, "data")
            self.assertEqual(len(dt.attributes), 1)
            self.assertEqual(dt.size, 2)

            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "NX_class")
            self.assertEqual(at[...], "NXdata")

            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            self.assertEqual(cnt.name, "cnt1")
            # self.assertEqual(cnt.name,"counter1")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (4,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 4)
#             print(cnt.read())
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(
                    self._counter[i if i < 2 else 3 - i], value[i])

            self.assertEqual(len(cnt.attributes), 4)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_FLOAT")

            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name, "data")

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 3)
            self.assertEqual(mca.shape, (4, 200, 200))
            self.assertEqual(mca.dtype, "int64")
            self.assertEqual(mca.size, 160000)
            value = mca.read()
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(0, value[0][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(9223372036854775807, value[1][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(0, value[2][i][j])
            for i in range(len(value[0])):
                for j in range(len(value[0][0])):
                    self.assertEqual(9223372036854775807, value[3][i][j])

            self.assertEqual(len(mca.attributes), 6)

            at = cnt.attributes["nexdatas_strategy"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "nexdatas_strategy")
            self.assertEqual(at[...], "STEP")

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "type")
            self.assertEqual(at[...], "NX_INT64")

            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")
            self.assertEqual(at.name, "units")
            self.assertEqual(at[...], "")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape, "__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype, "string")

            f.close()

        finally:

            if os.path.isfile(fname):
                os.remove(fname)


if __name__ == '__main__':
    unittest.main()
