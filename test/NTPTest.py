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
## \file NTPTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import struct


#import pni.io.nx.h5 as nx


from ndts.Types import NTP
from ndts.Types import Converters


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class NTPTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "doc"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None        
        self._fattrs = {"short_name":"test","units":"m" }
        self._gname = "testDoc"
        self._gtype = "NXentry"


        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"



        ## map of Python:Tango types
        self._pTt = {"int":"DevLong64", "float":"DevDouble", "str":"DevString", "unicode":"DevString", 
                     "bool":"DevBoolean"}

        ## map of Numpy:Tango types
        self._npTt = {"int":"DevLong64", "int64":"DevLong64", "int32":"DevLong",
                      "int16":"DevShort", "int8":"DevUChar", "uint":"DevULong64", 
                      "uint64":"DevULong64", "uint32":"DevULong", "uint16":"DevUShort", 
                      "uint8":"DevUChar", "float":"DevDouble", "float64":"DevDouble", 
                      "float32":"DevFloat", "string":"DevString", "bool":"DevBoolean"}
        
        ## map of NEXUS : numpy types 
        self._nTnp = {"NX_FLOAT32":"float32", "NX_FLOAT64":"float64", "NX_FLOAT":"float64", 
                      "NX_NUMBER":"float64", "NX_INT":"int64", "NX_INT64":"int64", 
                      "NX_INT32":"int32", "NX_INT16":"int16", "NX_INT8":"int8", 
                      "NX_UINT64":"uint64", "NX_UINT32":"uint32", "NX_UINT16":"uint16", "NX_UINT8":"uint8", 
                      "NX_UINT":"uint64", "NX_POSINT":"uint64", 
                      "NX_DATE_TIME":"string", "ISO8601":"string", "NX_CHAR":"string", "NX_BOOLEAN":"bool"}

        ## map of type : converting function
        self._convert = {"float32":float, "float64":float, "float":float, "int64":long, "int32":int,  
                         "int16":long, "int8":int, "int":int, "uint64":long, "uint32":int, "uint16":long,
                         "uint8":int, "uint":int, "string":str, "bool":Converters.toBool}
        
        ## map of tag attribute types 
        self._aTn = {"signal":"NX_INT", "axis":"NX_INT", "primary":"NX_INT32", "offset":"NX_INT", 
                     "stride":"NX_INT", "file_time":"NX_DATE_TIME", 
                     "file_update_time":"NX_DATE_TIME", "restricts":"NX_INT", 
                     "ignoreExtraGroups":"NX_BOOLEAN", "ignoreExtraFields":"NX_BOOLEAN", 
                     "ignoreExtraAttributes":"NX_BOOLEAN", "minOccus":"NX_INT", "maxOccus":"NX_INT"
                     }

        ## map of vector tag attribute types 
        self._aTnv = {"vector":"NX_FLOAT"}
        
        ## map of rank : data format
        self._rTf = {0:"SCALAR", 1:"SPECTRUM", 2:"IMAGE"}




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


    ## toBool instance test
    # \brief It tests default settings
    def test_dict(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = NTP()
        self.assertTrue(isinstance(el, object))
        
        for it in self._pTt:
            self.assertEqual(el.pTt[it],self._pTt[it])
            self.assertEqual(NTP.pTt[it],self._pTt[it])


        for it in self._npTt:
            self.assertEqual(el.npTt[it],self._npTt[it])
            self.assertEqual(NTP.npTt[it],self._npTt[it])


        for it in self._nTnp:
            self.assertEqual(el.nTnp[it],self._nTnp[it])
            self.assertEqual(NTP.nTnp[it],self._nTnp[it])


        for it in self._convert:
            self.assertEqual(el.convert[it],self._convert[it])
            self.assertEqual(NTP.convert[it],self._convert[it])

        for it in self._aTn:
            self.assertEqual(el.aTn[it],self._aTn[it])
            self.assertEqual(NTP.aTn[it],self._aTn[it])


        for it in self._aTnv:
            self.assertEqual(el.aTnv[it],self._aTnv[it])
            self.assertEqual(NTP.aTnv[it],self._aTnv[it])


        for it in self._rTf:
            self.assertEqual(el.rTf[it],self._rTf[it])
            self.assertEqual(NTP.rTf[it],self._rTf[it])


    
if __name__ == '__main__':
    unittest.main()
