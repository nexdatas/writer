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
# \file EDimensionsTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct

from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter


from nxswriter.EField import EField
from nxswriter.Element import Element
from nxswriter.H5Elements import EFile
from nxswriter.H5Elements import EDimensions


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EDimensionsH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "dimensions"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None
        self._fattrs = {"name": "test", "units": "m"}
        self._fattrs2 = {"fname": "test", "units": "m"}
        self._fattrs3 = {"fname": "test", "units": "m", "rank": "2"}
        self._gname = "testDoc"
        self._gtype = "NXentry"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        print("\nsetting up...")

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
        el = EDimensions({}, None)
        self.assertTrue(isinstance(el, Element))
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.last, None)

    # store method test
    # \brief It tests executing store method
    def test_store(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        el = Element(self._tfname, self._fattrs2)
        el2 = EDimensions(self._fattrs2, el)
        self.assertEqual(el2.tagName, self._tfname)
        self.assertEqual(el2.content, [])
        self.assertEqual(el2._tagAttrs, self._fattrs2)
        self.assertEqual(el2.doc, "")
        self.assertEqual(el2.store(""), None)
        self.assertEqual(el2.last, el)
        self.assertEqual(el2.store("<tag/>"), None)

    # last method test
    # \brief It tests executing _lastObject method
    def test_last_h5py(self):
        print("Run: %s.test_last() " % self.__class__.__name__)

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        FileWriter.writer = H5PYWriter
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs3, el)
        el2 = EDimensions(self._fattrs3, fi)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs3)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "2")

        nxFile.close()
        os.remove(fname)

    # last method test
    # \brief It tests executing _lastObject method
    def test_last_norank_h5py(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        fname = "test.h5"
        nxFile = None
        eFile = None

        # gname = "testGroup"
        # gtype = "NXentry"
        # fdname = "testField"
        # fdtype = "int64"

        # file handle
        FileWriter.writer = H5PYWriter
        nxFile = FileWriter.create_file(
            fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)

        el = Element(self._tfname, self._fattrs2, eFile)
        fi = EField(self._fattrs2, el)
        el2 = EDimensions(self._fattrs2, fi)
        self.assertEqual(fi.tagName, "field")
        self.assertEqual(fi.content, [])
        self.assertEqual(fi._tagAttrs, self._fattrs2)
        self.assertEqual(fi.doc, "")
        self.assertEqual(fi._lastObject(), None)
        self.assertEqual(type(el2.last), EField)
        self.assertEqual(el2.last.rank, "0")

        nxFile.close()
        os.remove(fname)

    # _beforeLast method test
    # \brief It tests executing _beforeLast method
    def test_beforeLast(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Element(self._tfname, self._fattrs, None)
        el2 = Element(self._tfname, self._fattrs, el)
        el3 = EDimensions(self._fattrs, el2)
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el._tagAttrs, self._fattrs)
        self.assertEqual(el.doc, "")
        self.assertEqual(el2.last, el)
        self.assertEqual(el2._beforeLast(), None)
        self.assertEqual(el3._beforeLast(), el)
        self.assertEqual(el.doc, "")

    # _beforeLast method test
    # \brief It tests executing _beforeLast method
    def test_store_beforeLast(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        el = Element(self._tfname, self._fattrs, None)
        el2 = Element(self._tfname, self._fattrs, el)
        el3 = EDimensions(self._fattrs, el2)
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el._tagAttrs, self._fattrs)
        self.assertEqual(el.doc, "")
        self.assertEqual(el2.last, el)
        self.assertEqual(el2._beforeLast(), None)
        self.assertEqual(el3._beforeLast(), el)
        self.assertEqual(el3.store([None, "<tag/>", None]), None)
        self.assertEqual(el.doc, "")
        el3.last.doc = "SYM"
        self.assertEqual(el3.store(None), None)
        el2.doc = "SYM2"
        self.assertEqual(el3.store(None), None)


if __name__ == '__main__':
    unittest.main()
