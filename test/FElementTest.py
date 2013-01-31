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
## \file FElementTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import pni.nx.h5 as nx
from ndts.Element import Element
from ndts.H5Elements import FElement
from ndts.H5Elements import EFile
from ndts.ThreadPool import ThreadPool


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



from  xml.sax import SAXParseException



## test fixture
class FElementTest(unittest.TestCase):

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

    ## constructor test
    # \brief It tests default settings
    def test_min_constructor(self):
        print "Run: %s.test_constructor() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, self._group)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")

    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        print "Run: %s.test_constructor() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None )
        el2 = FElement(self._tfname, self._fattrs, el, self._group)
        self.assertTrue(isinstance(el2, Element))
        self.assertTrue(isinstance(el2, FElement))
        self.assertEqual(el2.tagName, self._tfname)
        self.assertEqual(el2.content, [])
        self.assertEqual(el2.doc, "")


    ## constructor test
    # \brief It tests default settings
    def test_store(self):
        print "Run: %s.test_store() " % self.__class__.__name__
        el = Element(self._tfname, self._fattrs, self._group )
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.store(), None)
        self.assertEqual(el.store("<tag/>"), None)
        


if __name__ == '__main__':
    unittest.main()
