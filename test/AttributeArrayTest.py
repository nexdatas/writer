#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

from nxswriter.FieldArray import AttributeArray

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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()
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
            self.assertEqual(len(parent[i].attributes), 1)
            at = parent[i].attributes[aname]
            print type(at)
            self.assertTrue(isinstance(at,nx._nxh5.nxattribute))
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()


        attrs = {
            "string":["My string","NX_CHAR", "string"],
            "datetime":["12:34:34","NX_DATE_TIME", "string"],
            "iso8601":["12:34:34","ISO8601", "string"],
            "int":[-132,"NX_INT", "int64"],
            "int8":[13,"NX_INT8", "int8"],
            "int16":[-223,"NX_INT16", "int16"],
            "int32":[13235,"NX_INT32", "int32"],
            "int64":[-12425,"NX_INT64", "int64"],
            "uint":[123,"NX_UINT", "uint64"],
            "uint8":[65,"NX_UINT8", "uint8"],
            "uint16":[453,"NX_UINT16", "uint16"],
            "uint32":[12235,"NX_UINT32", "uint32"],
            "uint64":[14345,"NX_UINT64", "uint64"],
            "float":[-16.345,"NX_FLOAT", "float64",1.e-14],
            "number":[-2.345e+2,"NX_NUMBER", "float64",1.e-14],
            "float32":[-4.355e-1,"NX_FLOAT32", "float32",1.e-5],
            "float64":[-2.345,"NX_FLOAT64", "float64",1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool"],
            }



        parent = []
        for i in range(10):
            parent.append(nxFile.create_field("data_%s" % i,"string"))
        

        cnt = 0    
        for a in attrs:
            cnt += 1

            el = AttributeArray(parent, a, attrs[a][2])
            el.value = attrs[a][0]

            self.assertEqual(el.name, a)
            self.assertEqual(el.dtype, attrs[a][2])
            if len(attrs[a]) <= 3:
                self.assertEqual(el.value, attrs[a][0])
            else:
                self.assertTrue(abs(el.value-attrs[a][0])<attrs[a][3])
            
            
            for i in range(10):
                self.assertEqual(len(parent[i].attributes), cnt)
                at = parent[i].attributes[a]
                self.assertTrue(isinstance(at,nx._nxh5.nxattribute))
                self.assertTrue(at.valid)
                self.assertTrue(hasattr(at.shape,"__iter__"))
                self.assertEqual(len(at.shape),0)
                self.assertEqual(at.dtype,attrs[a][2])
                self.assertEqual(at.name,a)
                if len(attrs[a]) <= 3:
                    self.assertEqual(at.value, attrs[a][0])
                else:
                    self.assertTrue(abs(at.value-attrs[a][0])<attrs[a][3])
                
        nxFile.close()
        os.remove(fname)


if __name__ == '__main__':
    unittest.main()
