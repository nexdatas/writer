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
## \file AttributeArrayTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct

from ndts.FieldArray import AttributeArray

try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class AttributeArrayTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)


        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name":"test","units":"m" }


        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)
        parent = []
        for i in range(10):
            parent.append(nxFile.create_field("data_%s" % i,"string"))
        
        aname = 'myattr'
        dtype = 'string'
        avalue = "mystring"

        el = AttributeArray(parent, aname, dtype)
        self.assertEqual(el.name, aname)
        self.assertEqual(el.dtype, dtype)
        el.value = avalue
        self.assertEqual(el.value, avalue)

        for i in range(10):
            self.assertEqual(parent[i].nattrs, 1)
            at = parent[i].attr(aname)
            self.assertTrue(isinstance(at,nx.nxh5.NXAttribute))
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,dtype)
            self.assertEqual(at.name,aname)
            self.assertEqual(at.value,avalue)

        nxFile.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_0d_data(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)
        parent = []
        for i in range(10):
            parent.append(nxFile.create_field("data_%s" % i,"string"))
        
        aname = 'myattr2'
        dtype = 'int64'
        avalue = 1233

        el = AttributeArray(parent, aname, dtype)
        self.assertEqual(el.name, aname)
        self.assertEqual(el.dtype, dtype)
        el.value = avalue
        self.assertEqual(el.value, avalue)

        for i in range(10):
            self.assertEqual(parent[i].nattrs, 1)
            at = parent[i].attr(aname)
            self.assertTrue(isinstance(at,nx.nxh5.NXAttribute))
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,dtype)
            self.assertEqual(at.name,aname)
            self.assertEqual(at.value,avalue)

        nxFile.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
