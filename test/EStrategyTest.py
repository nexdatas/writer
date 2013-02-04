#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file EStrategyTest.py
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


import pni.nx.h5 as nx


from ndts.H5Elements import EStrategy
from ndts.H5Elements import FElement
from ndts.H5Elements import EField
from ndts.Element import Element
from ndts.H5Elements import EFile
from ndts.Types import NTP, Converters

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



from  xml.sax import SAXParseException




## test fixture
class EStrategyTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None        

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name":"test","units":"m" }
        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"


        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    ## test starter
    # \brief Common set up
    def setUp(self):
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._group = self._nxFile.create_group(self._gname, self._gtype)
        self._field = self._group.create_field(self._fdname, self._fdtype)
        print "\nsetting up..."        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."
        self._nxFile.close()
        os.remove(self._fname)

    ## Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except exception, e:
            error = True
        self.assertEqual(error, True)


    ## default constructor test
    # \brief It tests default settings
    def test_default_constructor(self):
        print "Run: %s.test_default_constructor() " % self.__class__.__name__
        el = EField("field", self._fattrs, None)
        st = EStrategy("strategy", self._fattrs, el)
        self.assertTrue(isinstance(st, Element))
        self.assertTrue(isinstance(st, EStrategy))
        self.assertEqual(st.tagName, "strategy")
        self.assertEqual(st.content, [])
        self.assertEqual(st.doc, "")
        self.assertEqual(st._last.strategy, None)
        self.assertEqual(el.strategy, None)
        self.assertEqual(st._last.trigger, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(st._last.grows, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(st._last.compression, False)
        self.assertEqual(el.compression, False)
        self.assertEqual(st._last.rate, 5)
        self.assertEqual(el.rate, 5)
        self.assertEqual(st._last.shuffle, True)
        self.assertEqual(el.shuffle, True)



    ## first constructor test
    # \brief It tests default settings
    def test_constructor_1(self):
        print "Run: %s.test_constructor() " % self.__class__.__name__
        attrs = {}
        attrs["mode"] = "STEP"
        attrs["trigger"] = "def_trigger"
        attrs["grows"] = "2"
        attrs["compression"] = "true"
        attrs["rate"] = "4"
        attrs["shuffle"] = "false"
        el = EField("field", self._fattrs, None)
        st = EStrategy("strategy", attrs, el)
        self.assertTrue(isinstance(st, Element))
        self.assertTrue(isinstance(st, EStrategy))
        self.assertEqual(st.tagName, "strategy")
        self.assertEqual(st.content, [])
        self.assertEqual(st.doc, "")
        self.assertEqual(st._last.strategy, attrs["mode"])
        self.assertEqual(el.strategy, attrs["mode"])
        self.assertEqual(st._last.trigger, attrs["trigger"])
        self.assertEqual(el.trigger, attrs["trigger"])
        self.assertEqual(st._last.grows, int(attrs["grows"]))
        self.assertEqual(el.grows, int(attrs["grows"]))
        self.assertEqual(st._last.compression, Converters.toBool(attrs["compression"]))
        self.assertEqual(el.compression,  Converters.toBool(attrs["compression"]))
        self.assertEqual(st._last.rate, int(attrs["rate"]))
        self.assertEqual(el.rate, int(attrs["rate"]))
        self.assertEqual(st._last.shuffle, Converters.toBool(attrs["shuffle"]))
        self.assertEqual(el.shuffle, Converters.toBool(attrs["shuffle"]))
        



        


if __name__ == '__main__':
    unittest.main()
