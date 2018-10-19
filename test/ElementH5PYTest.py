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
# \file ElementTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct

from nxswriter.H5Elements import EFile
from nxswriter.Element import Element
from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class ElementH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name": "test", "units": "m"}

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # lastObject method test
    # \brief It tests executing _lastObject method
    def test_lastObject_hp5y(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        self._fname = '%s/%s%s.h5' % (
            os.getcwd(), self.__class__.__name__, fun)

        FileWriter.writer = H5PYWriter
        fname = self._fname
        nxFile = None
        eFile = None

        gname = "testGroup"
        gtype = "NXentry"
        fdname = "testField"
        fdtype = "int64"

        # file handle
        nxFile = FileWriter.create_file(fname, overwrite=True).root()
        # element file objects
        eFile = EFile([], None, nxFile)
        group = nxFile.create_group(gname, gtype)
        group.create_field(fdname, fdtype)

        el = Element(self._tfname, self._fattrs, eFile)
        el2 = Element(self._tfname, self._fattrs, el)
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el._tagAttrs, self._fattrs)
        self.assertEqual(el.doc, "")
        self.assertEqual(el._lastObject(), nxFile)
        self.assertEqual(el2._lastObject(), None)

        nxFile.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
