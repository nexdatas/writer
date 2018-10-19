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
#    but WITHOUT ANY WARRANTY; without even the implied waranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with nexdatas.  If not, see <http://www.gnu.org/licenses/>.
# \package test nexdatas
# \file EStrategyTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import struct


from nxswriter.EStrategy import EStrategy
from nxswriter.EField import EField
from nxswriter.Element import Element
from nxswriter.Types import Converters
from nxstools import filewriter as FileWriter
from nxstools import h5pywriter as H5PYWriter


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class EStrategyH5PYTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name": "test", "units": "m"}
        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        FileWriter.writer = H5PYWriter
        self._nxFile = FileWriter.create_file(self._fname, overwrite=True)
        self._nxroot = self._nxFile.root()
        # element file objects
        self._group = self._nxroot.create_group(self._gname, self._gtype)
        self._field = self._group.create_field(self._fdname, self._fdtype)
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")
        self._nxFile.close()
        os.remove(self._fname)

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
        print("Run: %s.test_default_constructor() " % self.__class__.__name__)
        el = EField(self._fattrs, None)
        st = EStrategy(self._fattrs, el)
        self.assertTrue(isinstance(st, Element))
        self.assertTrue(isinstance(st, EStrategy))
        self.assertEqual(st.tagName, "strategy")
        self.assertEqual(st.content, [])
        self.assertEqual(st.doc, "")
        self.assertEqual(st.last.strategy, None)
        self.assertEqual(el.strategy, None)
        self.assertEqual(st.last.trigger, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(st.last.grows, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(st.last.compression, False)
        self.assertEqual(el.compression, False)
        self.assertEqual(st.last.rate, 5)
        self.assertEqual(el.rate, 5)
        self.assertEqual(st.last.shuffle, True)
        self.assertEqual(el.shuffle, True)

    # first constructor test
    # \brief It tests default settings
    def test_constructor_1(self):
        print("Run: %s.test_constructor() " % self.__class__.__name__)
        attrs = {}
        attrs["mode"] = "STEP"
        attrs["trigger"] = "def_trigger"
        attrs["grows"] = "2"
        attrs["compression"] = "true"
        attrs["rate"] = "4"
        attrs["shuffle"] = "false"
        el = EField(self._fattrs, None)
        st = EStrategy(attrs, el)
        self.assertTrue(isinstance(st, Element))
        self.assertTrue(isinstance(st, EStrategy))
        self.assertEqual(st.tagName, "strategy")
        self.assertEqual(st.content, [])
        self.assertEqual(st.doc, "")
        self.assertEqual(st.last.strategy, attrs["mode"])
        self.assertEqual(el.strategy, attrs["mode"])
        self.assertEqual(st.last.trigger, attrs["trigger"])
        self.assertEqual(el.trigger, attrs["trigger"])
        self.assertEqual(st.last.grows, int(attrs["grows"]))
        self.assertEqual(el.grows, int(attrs["grows"]))
        self.assertEqual(
            st.last.compression, Converters.toBool(attrs["compression"]))
        self.assertEqual(
            el.compression, Converters.toBool(attrs["compression"]))
        self.assertEqual(st.last.rate, int(attrs["rate"]))
        self.assertEqual(el.rate, int(attrs["rate"]))
        self.assertEqual(st.last.shuffle, Converters.toBool(attrs["shuffle"]))
        self.assertEqual(el.shuffle, Converters.toBool(attrs["shuffle"]))

    # first constructor test
    # \brief It tests default settings
    def test_constructor_2(self):
        print("Run: %s.test_constructor() " % self.__class__.__name__)
        attrs = {}
        attrs["mode"] = "INIT"
        attrs["trigger"] = "def_trigger1"
        attrs["grows"] = "0"
        attrs["compression"] = "false"
        attrs["rate"] = "2"
        attrs["shuffle"] = "false"
        el = EField(self._fattrs, None)
        st = EStrategy(attrs, el)
        self.assertTrue(isinstance(st, Element))
        self.assertTrue(isinstance(st, EStrategy))
        self.assertEqual(st.tagName, "strategy")
        self.assertEqual(st.content, [])
        self.assertEqual(st.doc, "")
        self.assertEqual(st.last.strategy, attrs["mode"])
        self.assertEqual(el.strategy, attrs["mode"])
        self.assertEqual(st.last.trigger, attrs["trigger"])
        self.assertEqual(el.trigger, attrs["trigger"])
        self.assertEqual(
            st.last.grows,
            int(attrs["grows"]) if int(attrs["grows"]) > 0 else 1)
        self.assertEqual(
            el.grows, int(attrs["grows"]) if int(attrs["grows"]) > 0 else 1)
        self.assertEqual(
            st.last.compression, Converters.toBool(attrs["compression"]))
        self.assertEqual(
            el.compression, Converters.toBool(attrs["compression"]))
        self.assertEqual(st.last.rate, 5)
        self.assertEqual(el.rate, 5)
        self.assertEqual(st.last.shuffle, True)
        self.assertEqual(el.shuffle, True)

    # first constructor test
    # \brief It tests default settings
    def test_constructor_3(self):
        print("Run: %s.test_constructor() " % self.__class__.__name__)
        attrs = {}
        attrs["mode"] = "STEP"
        attrs["trigger"] = "def_trigger"
        attrs["grows"] = "3"
        attrs["compression"] = "true"
        attrs["rate"] = "10"
        attrs["shuffle"] = "true"
        el = EField(self._fattrs, None)
        st = EStrategy(attrs, el)
        self.assertTrue(isinstance(st, Element))
        self.assertTrue(isinstance(st, EStrategy))
        self.assertEqual(st.tagName, "strategy")
        self.assertEqual(st.content, [])
        self.assertEqual(st.doc, "")
        self.assertEqual(st.last.strategy, attrs["mode"])
        self.assertEqual(el.strategy, attrs["mode"])
        self.assertEqual(st.last.trigger, attrs["trigger"])
        self.assertEqual(el.trigger, attrs["trigger"])
        self.assertEqual(st.last.grows, int(attrs["grows"]))
        self.assertEqual(el.grows, int(attrs["grows"]))
        self.assertEqual(
            st.last.compression, Converters.toBool(attrs["compression"]))
        self.assertEqual(
            el.compression, Converters.toBool(attrs["compression"]))
        self.assertEqual(
            st.last.rate, int(attrs["rate"]) if int(attrs["rate"]) < 10 else 9)
        self.assertEqual(
            el.rate, int(attrs["rate"]) if int(attrs["rate"]) < 10 else 9)
        self.assertEqual(st.last.shuffle, Converters.toBool(attrs["shuffle"]))
        self.assertEqual(el.shuffle, Converters.toBool(attrs["shuffle"]))

    # store method test
    # \brief It tests executing store method
    def test_store(self):
        print("Run: %s.test_store() " % self.__class__.__name__)

        # attrs = {"mode": "STEP"}
        el = EField(self._fattrs, None)
        st = EStrategy({"mode": "STEP"}, el)
        self.assertEqual(st.content, [])
        self.assertEqual(st.doc, "")
        self.assertEqual(st.store(), None)
        self.assertEqual(st.last, el)

        self.assertEqual(st.store("<tag/>"), None)
        self.assertEqual(st.last.postrun, "")

        content = ["Test postrun"]
        st.content = content
        self.assertEqual(st.content, st.content)
        self.assertEqual(st.store("<tag/>"), None)
        self.assertEqual(st.last.postrun, st.content[0])

        st.content = ["Test", " postrun"]
        self.assertEqual(st.content, st.content)
        self.assertEqual(st.store("<tag/>"), None)
        self.assertEqual(st.last.postrun, content[0])


if __name__ == '__main__':
    unittest.main()
