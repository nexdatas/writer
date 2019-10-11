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
# \file ConvertersTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys
import struct


from nxswriter.Types import Converters


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class ConvertersTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "doc"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None
        self._fattrs = {"short_name": "test", "units": "m"}
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

    # toBool instance test
    # \brief It tests default settings
    def test_toBool_instance(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        bools = {
            True: True, False: False,
            "True": True, "False": False,
            "true": True, "false": False,
            "TRUE": True, "FALSE": False,
            "tRUE": True, "fALSE": False,
            "TrUE": True, "FaLSE": False,
            "TrUE": True, "FAlSE": False,
            "TRuE": True, "FALsE": False,
            "TRUe": True, "FALSe": False,
            "trUE": True, "faLSE": False,
            "tRuE": True, "fAlSE": False,
            "tRUe": True, "fALsE": False,
            "tRUe": True, "fALSe": False,
            "TruE": True, "FalSE": False,
            "TrUe": True, "FaLsE": False,
            "TrUe": True, "FaLSe": False,
            "TRue": True, "FAlsE": False,
            "TRue": True, "FAlSe": False,
            "TRue": True, "FAlse": False,
            "truE": True, "falSE": False,
            "trUe": True, "faLsE": False,
            "tRue": True, "fAlsE": False,
            "True": True, "FalsE": False,
            "BleBle": True, "FaLSe": False,
            "bleble": True, "FAlSe": False,
            "xxxxxx": True, "FalSe": False,
            "bldsff": True, "fALse": False,
            "blerew": True, "FaLse": False,
            "bwerle": True, "FAlse": False,
            "alebwe": True, "fAlse": False,
            "glewer": True, "faLse": False,
            "fgeble": True, "falSe": False,
            "fall": True, "falsE": False,
        }

        el = Converters()
        self.assertTrue(isinstance(el, object))
        self.assertTrue(hasattr(el, "toBool"))

        for b in bools:
            self.assertEqual(el.toBool(b), bools[b])

    # toBool class test
    # \brief It tests default settings
    def test_toBool_class(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        bools = {
            True: True, False: False,
            "True": True, "False": False,
            "true": True, "false": False,
            "TRUE": True, "FALSE": False,
            "tRUE": True, "fALSE": False,
            "TrUE": True, "FaLSE": False,
            "TrUE": True, "FAlSE": False,
            "TRuE": True, "FALsE": False,
            "TRUe": True, "FALSe": False,
            "trUE": True, "faLSE": False,
            "tRuE": True, "fAlSE": False,
            "tRUe": True, "fALsE": False,
            "tRUe": True, "fALSe": False,
            "TruE": True, "FalSE": False,
            "TrUe": True, "FaLsE": False,
            "TrUe": True, "FaLSe": False,
            "TRue": True, "FAlsE": False,
            "TRue": True, "FAlSe": False,
            "TRue": True, "FAlse": False,
            "truE": True, "falSE": False,
            "trUe": True, "faLsE": False,
            "tRue": True, "fAlsE": False,
            "True": True, "FalsE": False,
            "BleBle": True, "FaLSe": False,
            "bleble": True, "FAlSe": False,
            "xxxxxx": True, "FalSe": False,
            "bldsff": True, "fALse": False,
            "blerew": True, "FaLse": False,
            "bwerle": True, "FAlse": False,
            "alebwe": True, "fAlse": False,
            "glewer": True, "faLse": False,
            "fgeble": True, "falSe": False,
            "fall": True, "falsE": False,
        }

        for b in bools:
            self.assertEqual(Converters.toBool(b), bools[b])


if __name__ == '__main__':
    unittest.main()
