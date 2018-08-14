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
# \file ErrorsTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys


from nxswriter.Errors import (
    CorruptedFieldArrayError, XMLSettingSyntaxError,
    DataSourceError, PackageError, DataSourceSetupError,
    XMLSyntaxError, UnsupportedTagError, ThreadError)


# test fixture
class ErrorsTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

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

    # CorruptedFieldArrayError test
    # \brief It tests default settings
    def test_CorruptedFieldArrayError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = CorruptedFieldArrayError()
        self.assertTrue(isinstance(err, Exception))

    # XMLSettingSyntaxError test
    # \brief It tests default settings
    def test_XMLSettingSyntaxError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = XMLSettingSyntaxError()
        self.assertTrue(isinstance(err, Exception))

    # DataSourceError test
    # \brief It tests default settings
    def test_DataSourceError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = DataSourceError()
        self.assertTrue(isinstance(err, Exception))

    # PackageError test
    # \brief It tests default settings
    def test_PackageError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = PackageError()
        self.assertTrue(isinstance(err, Exception))

    # DataSourceSetupError test
    # \brief It tests default settings
    def test_DataSourceSetupError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = DataSourceSetupError()
        self.assertTrue(isinstance(err, Exception))

    # XMLSyntaxError test
    # \brief It tests default settings
    def test_XMLSyntaxError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = XMLSyntaxError()
        self.assertTrue(isinstance(err, Exception))

    # XMLSyntaxError test
    # \brief It tests default settings
    def test_UnsupportedTagError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = UnsupportedTagError()
        self.assertTrue(isinstance(err, Exception))

    # XMLSyntaxError test
    # \brief It tests default settings
    def test_ThreadError(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        err = ThreadError()
        self.assertTrue(isinstance(err, Exception))


if __name__ == '__main__':
    unittest.main()
