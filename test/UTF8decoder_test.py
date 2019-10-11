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
# \file UTF8decoderTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys
import struct

from nxswriter.DecoderPool import UTF8decoder


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class UTF8decoderTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        self.__name = 'UTF8'

        self.__data = ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")
        self.__dtype = "string"

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        dc = UTF8decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

    # load method test
    # \brief It tests default settings
    def test_load(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        # data = {}
        dc = UTF8decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.load(self.__data), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)

    # shape method test
    # \brief It tests default settings
    def test_shape(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        # data = {}
        dc = UTF8decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), [1, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.load(self.__data), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)
        self.assertEqual(dc.shape(), [1, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)

    # decode method test
    # \brief It tests default settings
    def test_decode(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        # data = {}
        dc = UTF8decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), [1, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.decode(), None)

        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)
        self.assertEqual(dc.shape(), [1, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)

        self.assertEqual(dc.load(self.__data), None)
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)
        self.assertEqual(dc.shape(), [1, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)

        self.assertEqual(dc.decode(), self.__data[1])

        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)
        self.assertEqual(dc.shape(), [1, 0])
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, self.__data[0])
        self.assertEqual(dc.dtype, self.__dtype)


if __name__ == '__main__':
    unittest.main()
