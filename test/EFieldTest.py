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


import pni.io.nx.h5 as nx


from ndts.H5Elements import FElementWithAttr
from ndts.H5Elements import FElement
from ndts.H5Elements import EField
from ndts.Element import Element
from ndts.H5Elements import EFile
from ndts.H5Elements import EGroup
from ndts.Types import NTP, Converters

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



from  xml.sax import SAXParseException




## test fixture
class EFieldTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None        

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name":"test","units":"m" }
        self._gattrs = {"name":"test","type":"NXentry" }
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
        self._field = self._nxFile.create_field(self._fdname, self._fdtype)
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
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.source, None)
        self.assertEqual(el.strategy, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 5)
        self.assertEqual(el.shuffle, True)



    ## default store method
    # \brief It tests default settings
    def test_store_default(self):
        print "Run: %s.test_store() " % self.__class__.__name__
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = EField("field", self._fattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, None)
        self.assertEqual(el.source, None)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 5)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), None)
        



        


if __name__ == '__main__':
    unittest.main()
