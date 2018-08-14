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
# \file ELinkTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import random
import numpy

from TestDataSource import TestDataSource


from nxswriter.FElement import FElement
from nxswriter.ELink import ELink
from nxswriter.EField import EField
from nxswriter.EGroup import EGroup
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
from nxswriter.Types import NTP, Converters
from nxswriter.Errors import XMLSettingSyntaxError
from nxswriter.FetchNameHandler import TNObject

from Checkers import Checker

import nxswriter.FileWriter as FileWriter
import nxswriter.H5PYWriter as H5PYWriter


# from  xml.sax import SAXParseException

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class ELinkH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._fname2 = "test2.h5"
        self._nxFile = None
        self._eFile = None

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name": "testField", "units": "m"}
        self._fattrs2 = {"name": "testField", "type": "NX_INT", "units": "m"}
        self._gattrs = {"name": "testGroup", "type": "NXentry"}
        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._sc = Checker(self)

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        FileWriter.writer = H5PYWriter
        print("\nsetting up...")
        print("CHECKER SEED = %s" % self._sc.seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

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

    # default constructor test
    # \brief It tests default settings
    def test_default_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        li = ELink({}, eFile)
        self.assertTrue(isinstance(li, Element))
        self.assertTrue(isinstance(li, FElement))
        self.assertEqual(li.tagName, "link")
        self.assertEqual(li.content, [])

        self.assertEqual(li.h5Object, None)
#        self.assertEqual(type(el.h5Object), None)
#        self.assertEqual(el.h5Object.name, self._gattrs["name"])
#        self.assertEqual(el.h5Object.nattrs, 1)
#        self.assertEqual(el.h5Object.attr("NX_class")[...], self._gattrs["type"])
#        self.assertEqual(el.h5Object.attr("NX_class").dtype, "string")
#        self.assertEqual(el.h5Object.attr("NX_class").shape, ())

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        atts1 = {"name": "link1", "target": "/NXentry/testField",
                 "path": "ELinkH5PYTesttest_createLink_default.h5://testGroup/testField"}
        atts2 = {"name": "link2", "target": "/entry:NXentry/testField",
                 "path": "ELinkH5PYTesttest_createLink_default.h5://entry/testField"}
        atts3 = {"name": "link3", "target": "entry3/testField",
                 "path": "ELinkH5PYTesttest_createLink_default.h5://entry3/testField"}
        atts4 = {"name": "link4", "target": "/testField",
                 "path": "ELinkH5PYTesttest_createLink_default.h5://testField"}
        atts5 = {"name": "link5", "target": "/testGroup",
                 "path": "ELinkH5PYTesttest_createLink_default.h5://testGroup"}
        atts6 = {"name": "link5", "target": "/testField"}
        atts7 = {"name": "link7",
                 "path": "ELinkH5PYTesttest_createLink_default.h5://testField"}
        ct7 = "testField"
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li2 = ELink(atts2, eFile)
        li3 = ELink(atts3, eFile)
        li4 = ELink(atts4, eFile)
        li5 = ELink(atts5, eFile)
        li6 = ELink(atts6, eFile)
        li7 = ELink(atts7, eFile)
        li7.content.append(ct7)

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.myAssertRaise(XMLSettingSyntaxError, li1.createLink, TNObject())
        li1.createLink(gT1)
        self.assertTrue(isinstance(li1.h5Object, H5PYWriter.H5PYLink))
        self.assertEqual(li1.h5Object.name, atts1["name"])
        self.assertTrue(li1.h5Object._h5object.path, atts1["target"])

        # self.assertEqual(li1.h5Object._h5object, None)
        li2.createLink(TNObject())
        self.myAssertRaise(XMLSettingSyntaxError, li3.createLink, TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li7.createLink(TNObject())
        self.myAssertRaise(XMLSettingSyntaxError, li5.createLink, TNObject())
        self.myAssertRaise(XMLSettingSyntaxError, li6.createLink, TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertTrue(isinstance(li1.h5Object, H5PYWriter.H5PYLink))
        self.assertEqual(li1.h5Object.name, atts1["name"])
#        self.assertEqual(li1.h5Object._h5object.name, atts1["name"])
        print("KL %s %s" % (str(li1.h5Object.target_path), atts1["path"]))
        self.assertTrue(str(li1.h5Object.target_path).endswith(atts1["path"]))
        self.assertTrue(isinstance(li2.h5Object, H5PYWriter.H5PYLink))
        self.assertEqual(li2.h5Object.name, atts2["name"])
        self.assertTrue(str(li2.h5Object.target_path).endswith(atts2["path"]))
        self.assertTrue(isinstance(li3.h5Object, H5PYWriter.H5PYLink))
        self.assertEqual(li3.h5Object.name, atts3["name"])
        self.assertTrue(str(li3.h5Object.target_path).endswith(atts3["path"]))
        self.assertTrue(isinstance(li4.h5Object, H5PYWriter.H5PYLink))
        self.assertEqual(li4.h5Object.name, atts4["name"])
        self.assertTrue(str(li4.h5Object.target_path).endswith(atts4["path"]))
        self.assertTrue(isinstance(li5.h5Object, H5PYWriter.H5PYLink))
        self.assertEqual(li5.h5Object.name, atts5["name"])
        self.assertTrue(str(li5.h5Object.target_path).endswith(atts5["path"]))
#        self.assertEqual(li1.h5Object._h5object, None)
#        self.assertEqual(li2.h5Object._h5object, None)
#        self.assertEqual(li3.h5Object._h5object, None)
#        self.assertEqual(li4.h5Object._h5object, None)
#        self.assertEqual(li5.h5Object._h5object, None)
        self.assertEqual(li6.h5Object, None)
        self.assertTrue(isinstance(li7.h5Object, H5PYWriter.H5PYLink))
        self.assertEqual(li7.h5Object.name, atts7["name"])
        self.assertTrue(str(li7.h5Object.target_path).endswith(atts7["path"]))

        l1 = self._nxFile.open("link1")
        self.assertEqual(l1.read(), fi2.h5Object.read())
        self.assertEqual(l1.dtype, fi2.h5Object.dtype)
        self.assertEqual(l1.shape, fi2.h5Object.shape)
        self.assertEqual(len(l1.attributes), len(fi2.h5Object.attributes))
        self.assertEqual(l1.attributes["units"][
                         ...], fi2.h5Object.attributes["units"][...])
        self.assertEqual(
            l1.attributes["units"].dtype, fi2.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l1.attributes["units"].shape, fi2.h5Object.attributes["units"].shape)

        l2 = self._nxFile.open("link2")
        self.assertEqual(l2.read(), fi3.h5Object.read())
        self.assertEqual(l2.dtype, fi3.h5Object.dtype)
        self.assertEqual(l2.shape, fi3.h5Object.shape)
        self.assertEqual(len(l2.attributes), len(fi3.h5Object.attributes))
        self.assertEqual(l2.attributes["units"][
                         ...], fi3.h5Object.attributes["units"][...])
        self.assertEqual(
            l2.attributes["units"].dtype, fi3.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l2.attributes["units"].shape, fi3.h5Object.attributes["units"].shape)

        l3 = self._nxFile.open("link3")
        self.assertEqual(l3.read(), fi4.h5Object.read())
        self.assertEqual(l3.dtype, fi4.h5Object.dtype)
        self.assertEqual(l3.shape, fi4.h5Object.shape)
        self.assertEqual(len(l3.attributes), len(fi4.h5Object.attributes))
        self.assertEqual(l3.attributes["units"][
                         ...], fi4.h5Object.attributes["units"][...])
        self.assertEqual(
            l3.attributes["units"].dtype, fi4.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l3.attributes["units"].shape, fi4.h5Object.attributes["units"].shape)

        l4 = self._nxFile.open("link4")
        self.assertEqual(l4.read(), fi.h5Object.read())
        self.assertEqual(l4.dtype, fi.h5Object.dtype)
        self.assertEqual(l4.shape, fi.h5Object.shape)
        self.assertEqual(len(l4.attributes), len(fi.h5Object.attributes))
        self.assertEqual(l4.attributes["units"][
                         ...], fi.h5Object.attributes["units"][...])
        self.assertEqual(
            l4.attributes["units"].dtype, fi.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l4.attributes["units"].shape, fi.h5Object.attributes["units"].shape)

        l5 = self._nxFile.open("link5")
        self.assertEqual(l5.attributes["NX_class"][
                         ...], gr.h5Object.attributes["NX_class"][...])
        self.assertEqual(
            l5.attributes["NX_class"].dtype, gr.h5Object.attributes["NX_class"].dtype)
        self.assertEqual(
            l5.attributes["NX_class"].shape, gr.h5Object.attributes["NX_class"].shape)
#        self.assertEqual(l5.name, gr.h5Object.name )

        l7 = self._nxFile.open("link7")
        self.assertEqual(l7.read(), fi.h5Object.read())
        self.assertEqual(l7.dtype, fi.h5Object.dtype)
        self.assertEqual(l7.shape, fi.h5Object.shape)
        self.assertEqual(len(l7.attributes), len(fi.h5Object.attributes))
        self.assertEqual(l7.attributes["units"][
                         ...], fi.h5Object.attributes["units"][...])
        self.assertEqual(
            l7.attributes["units"].dtype, fi.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l7.attributes["units"].shape, fi.h5Object.attributes["units"].shape)

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_nods(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        atts1 = {"name": "link1"}
        atts2 = {"name": "link2"}
        atts3 = {"name": "link3"}
        atts4 = {"name": "link4"}
        atts5 = {"name": "link5"}
        atts6 = {"name": "link5"}
        tatts1 = {"name": "link1", "target": "/NXentry/testField"}
        tatts2 = {"name": "link2", "target": "/entry:NXentry/testField"}
        tatts3 = {"name": "link3", "target": "entry3/testField"}
        tatts4 = {"name": "link4", "target": "/testField"}
        tatts5 = {"name": "link5", "target": "/testGroup"}
        tatts6 = {"name": "link5", "target": "/testField"}
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li2 = ELink(atts2, eFile)
        li3 = ELink(atts3, eFile)
        li4 = ELink(atts4, eFile)
        li5 = ELink(atts5, eFile)
        li6 = ELink(atts6, eFile)

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        li1.createLink(TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        li3.createLink(TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li5.createLink(TNObject())
        li6.createLink(TNObject())
        li6.createLink(TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.store()
        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.run()
        self.myAssertRaise(Exception, self._nxFile.open, "link1")

        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.store()
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.run()
        self.myAssertRaise(Exception, self._nxFile.open, "link2")

        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.store()
        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.run()
        self.myAssertRaise(Exception, self._nxFile.open, "link3")

        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.store()
        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.run()
        self.myAssertRaise(Exception, self._nxFile.open, "link4")

        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.store()
        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.run()
        self.myAssertRaise(Exception, self._nxFile.open, "link5")

        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.store()
        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.run()
        self.myAssertRaise(Exception, self._nxFile.open, "link6")

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_ds(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        atts1 = {"name": "link1"}
        atts2 = {"name": "link2"}
        atts3 = {"name": "link3"}
        atts4 = {"name": "link4"}
        atts5 = {"name": "link5"}
        atts6 = {"name": "link5"}
        tatts1 = {"target1": "/NXentry/testField",
                  "target2": "/entry:NXentry/testField",
                  "target3": "entry3/testField",
                  "target4": "/testField",
                  "target5": "/testGroup",
                  "target6": "/testField"}
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        ds1 = TestDataSource()
        ds1.value = {"rank": 0, "value": tatts1["target1"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds2 = TestDataSource()
        ds2.value = {"rank": 0, "value": tatts1["target2"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds3 = TestDataSource()
        ds3.value = {"rank": 0, "value": tatts1["target3"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds4 = TestDataSource()
        ds4.value = {"rank": 0, "value": tatts1["target4"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds5 = TestDataSource()
        ds5.value = {"rank": 0, "value": tatts1["target5"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds6 = TestDataSource()
        ds6.value = {"rank": 0, "value": tatts1["target6"],
                     "tangoDType": "DevString", "shape": [0, 0]}

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li1.source = ds1
        li2 = ELink(atts2, eFile)
        li2.source = ds2
        li3 = ELink(atts3, eFile)
        li3.source = ds3
        li4 = ELink(atts4, eFile)
        li4.source = ds4
        li5 = ELink(atts5, eFile)
        li5.source = ds5
        li6 = ELink(atts6, eFile)
        li6.source = ds6

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        li1.createLink(TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        li3.createLink(TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li5.createLink(TNObject())
        li6.createLink(TNObject())
        li6.createLink(TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        self.assertEqual(li1.store(), (None, None))
        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.run()

        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        self.assertEqual(li2.store(), (None, None))
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.run()

        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        self.assertEqual(li3.store(), (None, None))
        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.run()

        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        self.assertEqual(li4.store(), (None, None))
        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.run()

        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        self.assertEqual(li5.store(), (None, None))
        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.run()

        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        self.assertEqual(li6.store(), (None, None))
        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.run()

        l1 = self._nxFile.open("link1")
        self.assertEqual(l1.read(), fi2.h5Object.read())
        self.assertEqual(l1.dtype, fi2.h5Object.dtype)
        self.assertEqual(l1.shape, fi2.h5Object.shape)
        self.assertEqual(len(l1.attributes), len(fi2.h5Object.attributes))
        self.assertEqual(l1.attributes["units"][
                         ...], fi2.h5Object.attributes["units"][...])
        self.assertEqual(
            l1.attributes["units"].dtype, fi2.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l1.attributes["units"].shape, fi2.h5Object.attributes["units"].shape)

        l2 = self._nxFile.open("link2")
        self.assertEqual(l2.read(), fi3.h5Object.read())
        self.assertEqual(l2.dtype, fi3.h5Object.dtype)
        self.assertEqual(l2.shape, fi3.h5Object.shape)
        self.assertEqual(len(l2.attributes), len(fi3.h5Object.attributes))
        self.assertEqual(l2.attributes["units"][
                         ...], fi3.h5Object.attributes["units"][...])
        self.assertEqual(
            l2.attributes["units"].dtype, fi3.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l2.attributes["units"].shape, fi3.h5Object.attributes["units"].shape)

        l3 = self._nxFile.open("link3")
        self.assertEqual(l3.read(), fi4.h5Object.read())
        self.assertEqual(l3.dtype, fi4.h5Object.dtype)
        self.assertEqual(l3.shape, fi4.h5Object.shape)
        self.assertEqual(len(l3.attributes), len(fi4.h5Object.attributes))
        self.assertEqual(l3.attributes["units"][
                         ...], fi4.h5Object.attributes["units"][...])
        self.assertEqual(
            l3.attributes["units"].dtype, fi4.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l3.attributes["units"].shape, fi4.h5Object.attributes["units"].shape)

        l4 = self._nxFile.open("link4")
        self.assertEqual(l4.read(), fi.h5Object.read())
        self.assertEqual(l4.dtype, fi.h5Object.dtype)
        self.assertEqual(l4.shape, fi.h5Object.shape)
        self.assertEqual(len(l4.attributes), len(fi.h5Object.attributes))
        self.assertEqual(l4.attributes["units"][
                         ...], fi.h5Object.attributes["units"][...])
        self.assertEqual(
            l4.attributes["units"].dtype, fi.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l4.attributes["units"].shape, fi.h5Object.attributes["units"].shape)

        l5 = self._nxFile.open("link5")
        self.assertEqual(l5.attributes["NX_class"][
                         ...], gr.h5Object.attributes["NX_class"][...])
        self.assertEqual(
            l5.attributes["NX_class"].dtype, gr.h5Object.attributes["NX_class"].dtype)
        self.assertEqual(
            l5.attributes["NX_class"].shape, gr.h5Object.attributes["NX_class"].shape)
#        self.assertEqual(l5.name, gr.h5Object.name )

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_strategy(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        atts1 = {"name": "link1"}
        atts2 = {"name": "link2"}
        atts3 = {"name": "link3"}
        atts4 = {"name": "link4"}
        atts5 = {"name": "link5"}
        atts6 = {"name": "link5"}
        tatts1 = {"target1": "/NXentry/testField",
                  "target2": "/entry:NXentry/testField",
                  "target3": "entry3/testField",
                  "target4": "/testField",
                  "target5": "/testGroup",
                  "target6": "/testField"}
        stg = {"strategy1": "INIT",
               "strategy2": "STEP",
               "strategy3": "FINAL",
               "strategy4": "INIT",
               "strategy5": "STEP",
               "strategy6": "FINAL"}
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        ds1 = TestDataSource()
        ds1.value = {"rank": 0, "value": tatts1["target1"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds2 = TestDataSource()
        ds2.value = {"rank": 0, "value": tatts1["target2"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds3 = TestDataSource()
        ds3.value = {"rank": 0, "value": tatts1["target3"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds4 = TestDataSource()
        ds4.value = {"rank": 0, "value": tatts1["target4"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds5 = TestDataSource()
        ds5.value = {"rank": 0, "value": tatts1["target5"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds6 = TestDataSource()
        ds6.value = {"rank": 0, "value": tatts1["target6"],
                     "tangoDType": "DevString", "shape": [0, 0]}

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li1.source = ds1
        li1.strategy = stg["strategy1"]
        li2 = ELink(atts2, eFile)
        li2.source = ds2
        li2.strategy = stg["strategy2"]
        li3 = ELink(atts3, eFile)
        li3.source = ds3
        li3.strategy = stg["strategy3"]
        li4 = ELink(atts4, eFile)
        li4.source = ds4
        li4.strategy = stg["strategy4"]
        li4.trigger = "myTrigger"
        li5 = ELink(atts5, eFile)
        li5.source = ds5
        li5.strategy = stg["strategy5"]
        li5.trigger = "myTrigger"
        li6 = ELink(atts6, eFile)
        li6.strategy = stg["strategy6"]
        li6.source = ds6

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        li1.createLink(TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        li3.createLink(TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li5.createLink(TNObject())
        li6.createLink(TNObject())
        li6.createLink(TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        self.assertEqual(li1.store(), (stg["strategy1"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.run()
        self.assertTrue(li1.error is None)
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        self.assertEqual(li2.store(), (stg["strategy2"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.run()
        self.assertTrue(li2.error is None)

        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        self.assertEqual(li3.store(), (stg["strategy3"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.run()
        self.assertTrue(li3.error is None)

        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        self.assertEqual(li4.store(), (stg["strategy4"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.run()
        self.assertTrue(li4.error is None)

        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        self.assertEqual(li5.store(), (stg["strategy5"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.run()
        self.assertTrue(li5.error is None)

        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        self.assertEqual(li6.store(), (stg["strategy6"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.run()
        self.assertTrue(li6.error is not None)

        l1 = self._nxFile.open("link1")
        self.assertEqual(l1.read(), fi2.h5Object.read())
        self.assertEqual(l1.dtype, fi2.h5Object.dtype)
        self.assertEqual(l1.shape, fi2.h5Object.shape)
        self.assertEqual(len(l1.attributes), len(fi2.h5Object.attributes))
        self.assertEqual(l1.attributes["units"][
                         ...], fi2.h5Object.attributes["units"][...])
        self.assertEqual(
            l1.attributes["units"].dtype, fi2.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l1.attributes["units"].shape, fi2.h5Object.attributes["units"].shape)

        l2 = self._nxFile.open("link2")
        self.assertEqual(l2.read(), fi3.h5Object.read())
        self.assertEqual(l2.dtype, fi3.h5Object.dtype)
        self.assertEqual(l2.shape, fi3.h5Object.shape)
        self.assertEqual(len(l2.attributes), len(fi3.h5Object.attributes))
        self.assertEqual(l2.attributes["units"][
                         ...], fi3.h5Object.attributes["units"][...])
        self.assertEqual(
            l2.attributes["units"].dtype, fi3.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l2.attributes["units"].shape, fi3.h5Object.attributes["units"].shape)

        l3 = self._nxFile.open("link3")
        self.assertEqual(l3.read(), fi4.h5Object.read())
        self.assertEqual(l3.dtype, fi4.h5Object.dtype)
        self.assertEqual(l3.shape, fi4.h5Object.shape)
        self.assertEqual(len(l3.attributes), len(fi4.h5Object.attributes))
        self.assertEqual(l3.attributes["units"][
                         ...], fi4.h5Object.attributes["units"][...])
        self.assertEqual(
            l3.attributes["units"].dtype, fi4.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l3.attributes["units"].shape, fi4.h5Object.attributes["units"].shape)

        l4 = self._nxFile.open("link4")
        self.assertEqual(l4.read(), fi.h5Object.read())
        self.assertEqual(l4.dtype, fi.h5Object.dtype)
        self.assertEqual(l4.shape, fi.h5Object.shape)
        self.assertEqual(len(l4.attributes), len(fi.h5Object.attributes))
        self.assertEqual(l4.attributes["units"][
                         ...], fi.h5Object.attributes["units"][...])
        self.assertEqual(
            l4.attributes["units"].dtype, fi.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l4.attributes["units"].shape, fi.h5Object.attributes["units"].shape)

        l5 = self._nxFile.open("link5")
        self.assertEqual(l5.attributes["NX_class"][
                         ...], gr.h5Object.attributes["NX_class"][...])
        self.assertEqual(
            l5.attributes["NX_class"].dtype, gr.h5Object.attributes["NX_class"].dtype)
        self.assertEqual(
            l5.attributes["NX_class"].shape, gr.h5Object.attributes["NX_class"].shape)
 #       self.assertEqual(l5.name, gr.h5Object.name )

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_strategy_external(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        atts1 = {"name": "link1"}
        atts2 = {"name": "link2"}
        atts3 = {"name": "link3"}
        atts4 = {"name": "link4"}
        atts5 = {"name": "link5"}
        atts6 = {"name": "link5"}
        tatts1 = {"target1": "%s://testGroup/testField" % self._fname,
                  "target2": "%s://entry/testField" % self._fname,
                  "target3": "%s://entry3/testField" % self._fname,
                  "target4": "%s://testField" % self._fname,
                  "target5": "%s:///testGroup" % self._fname,
                  "target6": "%s://testField" % self._fname}
        stg = {"strategy1": "INIT",
               "strategy2": "STEP",
               "strategy3": "FINAL",
               "strategy4": "INIT",
               "strategy5": "STEP",
               "strategy6": "FINAL"}
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        ds1 = TestDataSource()
        ds1.value = {"rank": 0, "value": tatts1["target1"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds2 = TestDataSource()
        ds2.value = {"rank": 0, "value": tatts1["target2"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds3 = TestDataSource()
        ds3.value = {"rank": 0, "value": tatts1["target3"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds4 = TestDataSource()
        ds4.value = {"rank": 0, "value": tatts1["target4"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds5 = TestDataSource()
        ds5.value = {"rank": 0, "value": tatts1["target5"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds6 = TestDataSource()
        ds6.value = {"rank": 0, "value": tatts1["target6"],
                     "tangoDType": "DevString", "shape": [0, 0]}

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li1.source = ds1
        li1.strategy = stg["strategy1"]
        li2 = ELink(atts2, eFile)
        li2.source = ds2
        li2.strategy = stg["strategy2"]
        li3 = ELink(atts3, eFile)
        li3.source = ds3
        li3.strategy = stg["strategy3"]
        li4 = ELink(atts4, eFile)
        li4.source = ds4
        li4.strategy = stg["strategy4"]
        li4.trigger = "myTrigger"
        li5 = ELink(atts5, eFile)
        li5.source = ds5
        li5.strategy = stg["strategy5"]
        li5.trigger = "myTrigger"
        li6 = ELink(atts6, eFile)
        li6.strategy = stg["strategy6"]
        li6.source = ds6

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        li1.createLink(TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        li3.createLink(TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li5.createLink(TNObject())
        li6.createLink(TNObject())
        li6.createLink(TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        self.assertEqual(li1.store(), (stg["strategy1"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.run()
        self.assertEqual(li1.error, None)
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        self.assertEqual(li2.store(), (stg["strategy2"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.run()
        self.assertEqual(li2.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        self.assertEqual(li3.store(), (stg["strategy3"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.run()
        self.assertEqual(li3.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        self.assertEqual(li4.store(), (stg["strategy4"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.run()
        self.assertEqual(li4.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        self.assertEqual(li5.store(), (stg["strategy5"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.run()
        self.assertEqual(li5.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        self.assertEqual(li6.store(), (stg["strategy6"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.run()
        self.assertTrue(li6.error is not None)

        l1 = self._nxFile.open("link1")
        self.assertEqual(l1.read(), fi2.h5Object.read())
        self.assertEqual(l1.dtype, fi2.h5Object.dtype)
        self.assertEqual(l1.shape, fi2.h5Object.shape)
        self.assertEqual(len(l1.attributes), len(fi2.h5Object.attributes))
        self.assertEqual(
            l1.attributes["units"][...],
            fi2.h5Object.attributes["units"][...])
        self.assertEqual(l1.attributes["units"].dtype,
                         fi2.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l1.attributes["units"].shape, fi2.h5Object.attributes["units"].shape)

        l2 = self._nxFile.open("link2")
        self.assertEqual(l2.read(), fi3.h5Object.read())
        self.assertEqual(l2.dtype, fi3.h5Object.dtype)
        self.assertEqual(l2.shape, fi3.h5Object.shape)
        self.assertEqual(len(l2.attributes), len(fi3.h5Object.attributes))
        self.assertEqual(l2.attributes["units"][
                         ...], fi3.h5Object.attributes["units"][...])
        self.assertEqual(
            l2.attributes["units"].dtype, fi3.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l2.attributes["units"].shape, fi3.h5Object.attributes["units"].shape)

        l3 = self._nxFile.open("link3")
        self.assertEqual(l3.read(), fi4.h5Object.read())
        self.assertEqual(l3.dtype, fi4.h5Object.dtype)
        self.assertEqual(l3.shape, fi4.h5Object.shape)
        self.assertEqual(len(l3.attributes), len(fi4.h5Object.attributes))
        self.assertEqual(l3.attributes["units"][
                         ...], fi4.h5Object.attributes["units"][...])
        self.assertEqual(
            l3.attributes["units"].dtype, fi4.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l3.attributes["units"].shape, fi4.h5Object.attributes["units"].shape)

        l4 = self._nxFile.open("link4")
        self.assertEqual(l4.read(), fi.h5Object.read())
        self.assertEqual(l4.dtype, fi.h5Object.dtype)
        self.assertEqual(l4.shape, fi.h5Object.shape)
        self.assertEqual(len(l4.attributes), len(fi.h5Object.attributes))
        self.assertEqual(l4.attributes["units"][
                         ...], fi.h5Object.attributes["units"][...])
        self.assertEqual(
            l4.attributes["units"].dtype, fi.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l4.attributes["units"].shape, fi.h5Object.attributes["units"].shape)

        l5 = self._nxFile.open("link5")
        self.assertEqual(l5.attributes["NX_class"][
                         ...], gr.h5Object.attributes["NX_class"][...])
        self.assertEqual(
            l5.attributes["NX_class"].dtype, gr.h5Object.attributes["NX_class"].dtype)
        self.assertEqual(
            l5.attributes["NX_class"].shape, gr.h5Object.attributes["NX_class"].shape)
        #! bug in for  PNI
        #! self.assertEqual(l5.name, gr.h5Object.name )
        self.assertEqual(l5.name, atts5["name"])

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_strategy_external_failed(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        atts1 = {"name": "link1"}
        atts2 = {"name": "link2"}
        atts3 = {"name": "link3"}
        atts4 = {"name": "link4"}
        atts5 = {"name": "link5"}
        atts6 = {"name": "link5"}
        tatts1 = {"target1": "%s://NXentry/testField" % self._fname,
                  "target2": "%s://NXentry/testField" % self._fname,
                  "target3": "%s://NXentry3/testField" % self._fname,
                  "target4": "%s://NXtestField" % self._fname,
                  "target5": "%s:///NXtestGroup" % self._fname,
                  "target6": "%s://NXtestField" % self._fname}
        stg = {"strategy1": "INIT",
               "strategy2": "STEP",
               "strategy3": "FINAL",
               "strategy4": "INIT",
               "strategy5": "STEP",
               "strategy6": "FINAL"}
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        ds1 = TestDataSource()
        ds1.value = {"rank": 0, "value": tatts1["target1"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds2 = TestDataSource()
        ds2.value = {"rank": 0, "value": tatts1["target2"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds3 = TestDataSource()
        ds3.value = {"rank": 0, "value": tatts1["target3"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds4 = TestDataSource()
        ds4.value = {"rank": 0, "value": tatts1["target4"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds5 = TestDataSource()
        ds5.value = {"rank": 0, "value": tatts1["target5"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds6 = TestDataSource()
        ds6.value = {"rank": 0, "value": tatts1["target6"],
                     "tangoDType": "DevString", "shape": [0, 0]}

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li1.source = ds1
        li1.strategy = stg["strategy1"]
        li2 = ELink(atts2, eFile)
        li2.source = ds2
        li2.strategy = stg["strategy2"]
        li3 = ELink(atts3, eFile)
        li3.source = ds3
        li3.strategy = stg["strategy3"]
        li4 = ELink(atts4, eFile)
        li4.source = ds4
        li4.strategy = stg["strategy4"]
        li4.trigger = "myTrigger"
        li5 = ELink(atts5, eFile)
        li5.source = ds5
        li5.strategy = stg["strategy5"]
        li5.trigger = "myTrigger"
        li6 = ELink(atts6, eFile)
        li6.strategy = stg["strategy6"]
        li6.source = ds6

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        li1.createLink(TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        li3.createLink(TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li5.createLink(TNObject())
        li6.createLink(TNObject())
        li6.createLink(TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        self.assertEqual(li1.store(), (stg["strategy1"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.run()
        self.assertEqual(li1.error, None)
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        self.assertEqual(li2.store(), (stg["strategy2"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.run()
        self.assertEqual(li2.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        self.assertEqual(li3.store(), (stg["strategy3"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.run()
        self.assertEqual(li3.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        self.assertEqual(li4.store(), (stg["strategy4"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.run()
        self.assertEqual(li4.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        self.assertEqual(li5.store(), (stg["strategy5"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.run()
        self.assertEqual(li5.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        self.assertEqual(li6.store(), (stg["strategy6"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.run()
        self.assertTrue(li6.error is not None)

        self.assertTrue(not self._nxFile.open("link1").is_valid)
        self.assertTrue(not self._nxFile.open("link2").is_valid)
        self.assertTrue(not self._nxFile.open("link3").is_valid)
        self.assertTrue(not self._nxFile.open("link4").is_valid)
        self.assertTrue(not self._nxFile.open("link5").is_valid)
        self.myAssertRaise(Exception, self._nxFile.open, "link6")

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_strategy_external_rel(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._nxFile = FileWriter.create_file(
            self._fname, overwrite=True).root()
        eFile = EFile({}, None, self._nxFile)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        sfnm = self._fname.split('/')

        fnm = sfnm[-1]
        fnm2 = fnm
        fnm3 = fnm
        if len(sfnm) > 1:
            fnm2 = '../' + '/'.join(sfnm[-2:])
        if len(sfnm) > 2:
            fnm3 = '../../' + '/'.join(sfnm[-3:])

        atts1 = {"name": "link1"}
        atts2 = {"name": "link2"}
        atts3 = {"name": "link3"}
        atts4 = {"name": "link4"}
        atts5 = {"name": "link5"}
        atts6 = {"name": "link5"}
        tatts1 = {"target1": "%s://testGroup/testField" % fnm,
                  "target2": "%s://entry/testField" % fnm2,
                  "target3": "%s://entry3/testField" % fnm3,
                  "target4": "%s://testField" % fnm,
                  "target5": "%s:///testGroup" % fnm2,
                  "target6": "%s://testField" % fnm}
        stg = {"strategy1": "INIT",
               "strategy2": "STEP",
               "strategy3": "FINAL",
               "strategy4": "INIT",
               "strategy5": "STEP",
               "strategy6": "FINAL"}
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        ds1 = TestDataSource()
        ds1.value = {"rank": 0, "value": tatts1["target1"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds2 = TestDataSource()
        ds2.value = {"rank": 0, "value": tatts1["target2"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds3 = TestDataSource()
        ds3.value = {"rank": 0, "value": tatts1["target3"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds4 = TestDataSource()
        ds4.value = {"rank": 0, "value": tatts1["target4"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds5 = TestDataSource()
        ds5.value = {"rank": 0, "value": tatts1["target5"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds6 = TestDataSource()
        ds6.value = {"rank": 0, "value": tatts1["target6"],
                     "tangoDType": "DevString", "shape": [0, 0]}

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li1.source = ds1
        li1.strategy = stg["strategy1"]
        li2 = ELink(atts2, eFile)
        li2.source = ds2
        li2.strategy = stg["strategy2"]
        li3 = ELink(atts3, eFile)
        li3.source = ds3
        li3.strategy = stg["strategy3"]
        li4 = ELink(atts4, eFile)
        li4.source = ds4
        li4.strategy = stg["strategy4"]
        li4.trigger = "myTrigger"
        li5 = ELink(atts5, eFile)
        li5.source = ds5
        li5.strategy = stg["strategy5"]
        li5.trigger = "myTrigger"
        li6 = ELink(atts6, eFile)
        li6.strategy = stg["strategy6"]
        li6.source = ds6

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        li1.createLink(TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        li3.createLink(TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li5.createLink(TNObject())
        li6.createLink(TNObject())
        li6.createLink(TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        self.assertEqual(li1.store(), (stg["strategy1"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.run()
        self.assertEqual(li1.error, None)
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        self.assertEqual(li2.store(), (stg["strategy2"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.run()
        self.assertEqual(li2.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        self.assertEqual(li3.store(), (stg["strategy3"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.run()
        self.assertEqual(li3.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        self.assertEqual(li4.store(), (stg["strategy4"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.run()
        self.assertEqual(li4.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        self.assertEqual(li5.store(), (stg["strategy5"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.run()
        self.assertEqual(li5.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        self.assertEqual(li6.store(), (stg["strategy6"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.run()
        self.assertTrue(li6.error is not None)

        l1 = self._nxFile.open("link1")
        self.assertEqual(l1.read(), fi2.h5Object.read())
        self.assertEqual(l1.dtype, fi2.h5Object.dtype)
        self.assertEqual(l1.shape, fi2.h5Object.shape)
        self.assertEqual(len(l1.attributes), len(fi2.h5Object.attributes))
        self.assertEqual(l1.attributes["units"][
                         ...], fi2.h5Object.attributes["units"][...])
        self.assertEqual(
            l1.attributes["units"].dtype, fi2.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l1.attributes["units"].shape, fi2.h5Object.attributes["units"].shape)

        l2 = self._nxFile.open("link2")
        self.assertEqual(l2.read(), fi3.h5Object.read())
        self.assertEqual(l2.dtype, fi3.h5Object.dtype)
        self.assertEqual(l2.shape, fi3.h5Object.shape)
        self.assertEqual(len(l2.attributes), len(fi3.h5Object.attributes))
        self.assertEqual(l2.attributes["units"][
                         ...], fi3.h5Object.attributes["units"][...])
        self.assertEqual(
            l2.attributes["units"].dtype, fi3.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l2.attributes["units"].shape, fi3.h5Object.attributes["units"].shape)

        l3 = self._nxFile.open("link3")
        self.assertEqual(l3.read(), fi4.h5Object.read())
        self.assertEqual(l3.dtype, fi4.h5Object.dtype)
        self.assertEqual(l3.shape, fi4.h5Object.shape)
        self.assertEqual(len(l3.attributes), len(fi4.h5Object.attributes))
        self.assertEqual(l3.attributes["units"][
                         ...], fi4.h5Object.attributes["units"][...])
        self.assertEqual(
            l3.attributes["units"].dtype, fi4.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l3.attributes["units"].shape, fi4.h5Object.attributes["units"].shape)

        l4 = self._nxFile.open("link4")
        self.assertEqual(l4.read(), fi.h5Object.read())
        self.assertEqual(l4.dtype, fi.h5Object.dtype)
        self.assertEqual(l4.shape, fi.h5Object.shape)
        self.assertEqual(len(l4.attributes), len(fi.h5Object.attributes))
        self.assertEqual(l4.attributes["units"][
                         ...], fi.h5Object.attributes["units"][...])
        self.assertEqual(
            l4.attributes["units"].dtype, fi.h5Object.attributes["units"].dtype)
        self.assertEqual(
            l4.attributes["units"].shape, fi.h5Object.attributes["units"].shape)

        l5 = self._nxFile.open("link5")
        self.assertEqual(l5.attributes["NX_class"][
                         ...], gr.h5Object.attributes["NX_class"][...])
        self.assertEqual(
            l5.attributes["NX_class"].dtype, gr.h5Object.attributes["NX_class"].dtype)
        self.assertEqual(
            l5.attributes["NX_class"].shape, gr.h5Object.attributes["NX_class"].shape)
        #! bug in PNI
        #! self.assertEqual(l5.name, gr.h5Object.name )
        self.assertEqual(l5.name, atts5["name"])

        self._nxFile.close()
        os.remove(self._fname)

    # default constructor test
    # \brief It tests default settings
    def test_createLink_strategy_external_twofiles(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._fname2 = '%s/%s%s_2.h5' % (
            os.getcwd(), self.__class__.__name__, fun)
        self._File = FileWriter.create_file(self._fname, overwrite=True)
        self._nxFile = self._File.root()
        self._File2 = FileWriter.create_file(self._fname2, overwrite=True)
        self._nxFile2 = self._File2.root()
        eFile = EFile({}, None, self._nxFile)
        eFile2 = EFile({}, None, self._nxFile2)
        fi = EField(self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup(self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type": "NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type": "NXentry", "name": "entry3"}, eFile)
        gr3.store()

        sfnm = self._fname.split('/')

        fnm = sfnm[-1]
        fnm2 = fnm
        fnm3 = fnm
        if len(sfnm) > 1:
            fnm2 = '../' + '/'.join(sfnm[-2:])
        if len(sfnm) > 2:
            fnm3 = '../../' + '/'.join(sfnm[-3:])

        atts1 = {"name": "link1"}
        atts2 = {"name": "link2"}
        atts3 = {"name": "link3"}
        atts4 = {"name": "link4"}
        atts5 = {"name": "link5"}
        atts6 = {"name": "link5"}
        tatts1 = {"target1": "%s://testGroup/testField" % fnm,
                  "target2": "%s://entry/testField" % fnm2,
                  "target3": "%s://entry3/testField" % fnm3,
                  "target4": "%s://testField" % fnm,
                  "target5": "%s:///testGroup" % fnm2,
                  "target6": "%s://testField" % fnm}
        stg = {"strategy1": "INIT",
               "strategy2": "STEP",
               "strategy3": "FINAL",
               "strategy4": "INIT",
               "strategy5": "STEP",
               "strategy6": "FINAL"}
        gT1 = TNObject()
        ch = TNObject("testGroup", "NXentry", gT1)
        gT2 = TNObject()
        ch = TNObject("entry3", "NXentry", gT2)

        ds1 = TestDataSource()
        ds1.value = {"rank": 0, "value": tatts1["target1"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds2 = TestDataSource()
        ds2.value = {"rank": 0, "value": tatts1["target2"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds3 = TestDataSource()
        ds3.value = {"rank": 0, "value": tatts1["target3"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds4 = TestDataSource()
        ds4.value = {"rank": 0, "value": tatts1["target4"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds5 = TestDataSource()
        ds5.value = {"rank": 0, "value": tatts1["target5"],
                     "tangoDType": "DevString", "shape": [0, 0]}
        ds6 = TestDataSource()
        ds6.value = {"rank": 0, "value": tatts1["target6"],
                     "tangoDType": "DevString", "shape": [0, 0]}

        li0 = ELink({}, eFile2)
        li1 = ELink(atts1, eFile2)
        li1.source = ds1
        li1.strategy = stg["strategy1"]
        li2 = ELink(atts2, eFile2)
        li2.source = ds2
        li2.strategy = stg["strategy2"]
        li3 = ELink(atts3, eFile2)
        li3.source = ds3
        li3.strategy = stg["strategy3"]
        li4 = ELink(atts4, eFile2)
        li4.source = ds4
        li4.strategy = stg["strategy4"]
        li4.trigger = "myTrigger"
        li5 = ELink(atts5, eFile2)
        li5.source = ds5
        li5.strategy = stg["strategy5"]
        li5.trigger = "myTrigger"
        li6 = ELink(atts6, eFile2)
        li6.strategy = stg["strategy6"]
        li6.source = ds6

        fi2 = EField(self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField(self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()

        fi4 = EField(self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        li1.createLink(TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        li3.createLink(TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        li5.createLink(TNObject())
        li6.createLink(TNObject())
        li6.createLink(TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        self.assertEqual(li1.store(), (stg["strategy1"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link1")
        li1.run()
        self.assertEqual(li1.error, None)
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        self.assertEqual(li2.store(), (stg["strategy2"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link2")
        li2.run()
        self.assertEqual(li2.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        self.assertEqual(li3.store(), (stg["strategy3"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link3")
        li3.run()
        self.assertEqual(li3.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        self.assertEqual(li4.store(), (stg["strategy4"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link4")
        li4.run()
        self.assertEqual(li4.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        self.assertEqual(li5.store(), (stg["strategy5"], 'myTrigger'))
        self.myAssertRaise(Exception, self._nxFile.open, "link5")
        li5.run()
        self.assertEqual(li5.error, None)

        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        self.assertEqual(li6.store(), (stg["strategy6"], None))
        self.myAssertRaise(Exception, self._nxFile.open, "link6")
        li6.run()
        self.assertTrue(li6.error is not None)
        print(fi2.h5Object.shape)

        self._File.close()
        self._File.reopen(readonly=True)
        print(fi2.h5Object)

        self._File.close()

        l1 = self._nxFile2.open("link1")
        l2 = self._nxFile2.open("link2")
        l3 = self._nxFile2.open("link3")
        l4 = self._nxFile2.open("link4")
        l5 = self._nxFile2.open("link5")
        res = {}
        res["l1"] = [l1.read(), l1.dtype, l1.shape, len(l1.attributes),
                     l1.attributes["units"][...], l1.attributes["units"].dtype,
                     l1.attributes["units"].shape]
        res["l2"] = [l2.read(), l2.dtype, l2.shape, len(l2.attributes),
                     l2.attributes["units"][...], l2.attributes["units"].dtype,
                     l2.attributes["units"].shape]
        res["l3"] = [l3.read(), l3.dtype, l3.shape, len(l3.attributes),
                     l3.attributes["units"][...], l3.attributes["units"].dtype,
                     l3.attributes["units"].shape]
        res["l4"] = [l4.read(), l4.dtype, l4.shape, len(l4.attributes),
                     l4.attributes["units"][...], l4.attributes["units"].dtype,
                     l4.attributes["units"].shape]
        res["l5"] = [
            l5.attributes["NX_class"][...], l5.attributes["NX_class"].dtype,
            l5.attributes["NX_class"].shape, l5.name]

        self._File2.close()
        self._nxFile2 = None
        l1 = l2 = l3 = l4 = l5 = None

        self._File.reopen(readonly=True)

        print(fi2.h5Object.shape)
        self.assertEqual(res["l1"][0], fi2.h5Object.read())
        self.assertEqual(res["l1"][1], fi2.h5Object.dtype)
        self.assertEqual(res["l1"][2], fi2.h5Object.shape)
        self.assertEqual(res["l1"][3], len(fi2.h5Object.attributes))
        self.assertEqual(res["l1"][4], fi2.h5Object.attributes["units"][...])
        self.assertEqual(res["l1"][5], fi2.h5Object.attributes["units"].dtype)
        self.assertEqual(res["l1"][6], fi2.h5Object.attributes["units"].shape)

        self.assertEqual(res["l2"][0], fi3.h5Object.read())
        self.assertEqual(res["l2"][1], fi3.h5Object.dtype)
        self.assertEqual(res["l2"][2], fi3.h5Object.shape)
        self.assertEqual(res["l2"][3], len(fi3.h5Object.attributes))
        self.assertEqual(res["l2"][4], fi3.h5Object.attributes["units"][...])
        self.assertEqual(res["l2"][5], fi3.h5Object.attributes["units"].dtype)
        self.assertEqual(res["l2"][6], fi3.h5Object.attributes["units"].shape)

        self.assertEqual(res["l3"][0], fi4.h5Object.read())
        self.assertEqual(res["l3"][1], fi4.h5Object.dtype)
        self.assertEqual(res["l3"][2], fi4.h5Object.shape)
        self.assertEqual(res["l3"][3], len(fi4.h5Object.attributes))
        self.assertEqual(res["l3"][4], fi4.h5Object.attributes["units"][...])
        self.assertEqual(res["l3"][5], fi4.h5Object.attributes["units"].dtype)
        self.assertEqual(res["l3"][6], fi4.h5Object.attributes["units"].shape)

        self.assertEqual(res["l4"][0], fi.h5Object.read())
        self.assertEqual(res["l4"][1], fi.h5Object.dtype)
        self.assertEqual(res["l4"][2], fi.h5Object.shape)
        self.assertEqual(res["l4"][3], len(fi.h5Object.attributes))
        self.assertEqual(res["l4"][4], fi.h5Object.attributes["units"][...])
        self.assertEqual(res["l4"][5], fi.h5Object.attributes["units"].dtype)
        self.assertEqual(res["l4"][6], fi.h5Object.attributes["units"].shape)

        self.assertEqual(
            res["l5"][0], gr.h5Object.attributes["NX_class"][...])
        self.assertEqual(
            res["l5"][1], gr.h5Object.attributes["NX_class"].dtype)
        self.assertEqual(
            res["l5"][2], gr.h5Object.attributes["NX_class"].shape)
        self.assertEqual(res["l5"][3], gr.h5Object.name)

        self._nxFile.close()
        os.remove(self._fname)
        os.remove(self._fname2)


if __name__ == '__main__':
    unittest.main()
