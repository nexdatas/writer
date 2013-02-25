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
## \file DataHolderTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import numpy


from ndts.DataHolder import DataHolder
from ndts.DecoderPool import DecoderPool

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class DataHolderTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)


        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self.__data = {"format":"SCALAR", 
                       "value":"123", "tangoDType":"DevShort", 
                       "shape":[1,0],
                       "encoding": None, "decoders": None}
        


    ## test starter
    # \brief Common set up
    def setUp(self):
        ## file handle
        print "\nsetting up..."        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

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
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        el = DataHolder(**self.__data) 
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.format, self.__data["format"])
        self.assertEqual(el.value, self.__data["value"])
        self.assertEqual(el.tangoDType, self.__data["tangoDType"])
        self.assertEqual(el.shape, self.__data["shape"])
        self.assertEqual(el.encoding, self.__data["encoding"])
        self.assertEqual(el.decoders, self.__data["decoders"])


    ## setup test
    # \brief It tests default settings
    def test_constructor_scalar(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        arr = {
            "ScalarBoolean":[ "bool", "DevBoolean", True],
            "ScalarUChar":[ "uint8", "DevUChar", 23],
            "ScalarShort":[ "int16", "DevShort", -123],
            "ScalarUShort":[ "uint16", "DevUShort", 1234],
            "ScalarLong":[ self._bint, "DevLong", -124],
            "ScalarULong":[self._buint , "DevULong", 234],
            "ScalarLong64":[ "int64", "DevLong64", 234],
            "ScalarULong64":[ "uint64", "DevULong64", 23],
            "ScalarFloat":[ "float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble":[ "float64", "DevDouble", -2.456673e+02,1e-14],
            "ScalarString":[ "string", "DevString", "MyTrue"],
#            "State":[ "string", "DevState", PyTango._PyTango.DevState.ON],
            }





        for a in arr:

            data = {"format":"SCALAR", 
                    "value":arr[a][2], 
                    "tangoDType":arr[a][1], 
                    "shape":[1,0],
                    "encoding": None, 
                    "decoders": None}
            el = DataHolder(**data)
 
            self.assertTrue(isinstance(el, object))
            self.assertEqual(el.format, data["format"])
            self.assertEqual(el.value, data["value"])
            self.assertEqual(el.tangoDType, data["tangoDType"])
            self.assertEqual(el.shape, data["shape"])
            self.assertEqual(el.encoding, data["encoding"])
            self.assertEqual(el.decoders, data["decoders"])


 

    ## setup test
    # \brief It tests default settings
    def test_constructor_encode(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        dp = DecoderPool()

        arr = {
           "ScalarEncoded":[ "string", "DevEncoded", ("UTF8","Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b"),
                             [1,0], "SCALAR","Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b", "DevString"],
           "SpectrumEncoded":[ "string", "DevEncoded", 
                               ('UINT32', '\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00') ,
                               [4,0], "SPECTRUM",numpy.array([1234, 5678,   45,  345], dtype=numpy.uint32),"DevULong"]
           }





        for a in arr:
            
            data = {"format":"SCALAR", 
                    "value":arr[a][2], 
                    "tangoDType":arr[a][1], 
                    "shape":[1,0], 
                    "encoding": arr[a][2][0], 
                    "decoders": dp}
            el = DataHolder(**data)
 
            self.assertTrue(isinstance(el, object))
            self.assertEqual(el.format, arr[a][4])
            self.assertEqual(el.tangoDType, arr[a][6])
            self.assertEqual(el.shape, arr[a][3])
            self.assertEqual(el.encoding, data["encoding"])
            self.assertEqual(el.decoders, data["decoders"])

            if el.shape == [1,0]:
                self.assertEqual(el.value, arr[a][5])
            elif len(el.shape)==2 and el.shape[1] == 0:
                self.assertEqual(len(el.value), len(arr[a][5]))
                self.assertEqual(len(el.value), el.shape[0])
                for i in range(el.shape[0]):
                    self.assertEqual(el.value[i], arr[a][5][i])
                    
                    

 


if __name__ == '__main__':
    unittest.main()
