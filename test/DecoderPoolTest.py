#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file DecoderPoolTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import json
import numpy
from xml.dom import minidom

import nxswriter

from nxswriter.DecoderPool import DecoderPool, UTF8decoder, UINT32decoder, VDEOdecoder


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

## Wrong Decoder
class W0DS(object):
    pass

## Wrong Decoder
class W1DS(object):
    ## constructor
    def __init__(self):
        ##name attribute
        self.name = None
        ## dtype attribute
        self.dtype = None
        ## format attribute
        self.format = None



## Wrong Decoder
class W2DS(object):
    ## constructor
    def __init__(self):
        ##name attribute
        self.name = None
        ## dtype attribute
        self.dtype = None
        ## format attribute
        self.format = None

    ## load method
    def load(self):
        pass


## Wrong Decoder
class W3DS(object):
    ## constructor
    def __init__(self):
        ##name attribute
        self.name = None
        ## dtype attribute
        self.dtype = None
        ## format attribute
        self.format = None

    ## load method
    def load(self):
        pass

    ## shape method
    def shape(self):
        pass




## Wrong Decoder
class W4DS(object):
    ## constructor
    def __init__(self):
        ##name attribute
        self.name = None
        ## dtype attribute
        self.dtype = None
        ## format attribute
        self.format = None

    ## load method
    def load(self):
        pass

    ## shape method
    def shape(self):
        pass

    ## decode method
    def decode(self):
        pass


## test fixture
class DecoderPoolTest(unittest.TestCase):

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

    ## constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = DecoderPool()
        self.assertTrue(isinstance(el, object))

        el = DecoderPool(json.loads("{}"))
        self.assertTrue(isinstance(el, object))

        jsn = json.loads('{"decoders":{"UTF":"DecoderPool.Decode"}}')
        self.myAssertRaise(AttributeError,DecoderPool,jsn)


        jsn = json.loads('{"decoders":{"UTF":"DDecoderPool.UTF8decoder"}}')
        self.myAssertRaise(ImportError,DecoderPool,jsn)


        el = DecoderPool(json.loads('{"decoders":{"UTF":"DecoderPool.UTF8decoder"}}'))




    ## hasDecoder test
    # \brief It tests default settings
    def test_hasDecoder(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = DecoderPool()
        self.assertTrue(el.hasDecoder("UTF8"))
        self.assertTrue(el.hasDecoder("UINT32"))
        self.assertTrue(el.hasDecoder("LIMA_VIDEO_IMAGE"))
        self.assertTrue(not el.hasDecoder("DBB"))
        self.assertTrue(not el.hasDecoder("CL"))

        el = DecoderPool(json.loads('{"decoders":{"UTF":"DecoderPool.UTF8decoder"}}'))
        self.assertTrue(el.hasDecoder("UTF8"))
        self.assertTrue(el.hasDecoder("UINT32"))
        self.assertTrue(el.hasDecoder("LIMA_VIDEO_IMAGE"))
        self.assertTrue(not el.hasDecoder("DBB"))
        self.assertTrue(el.hasDecoder("UTF"))


    ## get method test
    # \brief It tests default settings
    def test_get(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = DecoderPool()
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"),None)
        self.assertEqual(el.get("CL"),None)
        

        el = DecoderPool(json.loads('{"decoders":{"UTF":"DecoderPool.UTF8decoder"}}'))
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"),None)
        ds = el.get("UTF")
        self.assertTrue(isinstance(ds, UTF8decoder))






    ## append method test
    # \brief It tests default settings
    def test_append(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = DecoderPool()
        el.append(nxswriter.DecoderPool.UTF8decoder,"UTF")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"),None)
        ds = el.get("UTF")
        self.assertTrue(isinstance(ds, UTF8decoder))



        el = DecoderPool()
        el.append(W0DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"),None)


        el = DecoderPool()
        el.append(W1DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"),None)



        el = DecoderPool()
        el.append(W2DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"),None)



        el = DecoderPool()
        el.append(W3DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("W0"),None)


        el = DecoderPool()
        el.append(W4DS, "W0")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        dc = el.get("W0")
        self.assertTrue(isinstance(dc, W4DS))


    ## append put test
    # \brief It tests default settings
    def test_pop(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)



        el = DecoderPool()
        el.pop("CL")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        el.pop("UINT32")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        self.assertEqual(el.get("UINT32"),None)
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"),None)
        self.assertEqual(el.get("CL"),None)


        el = DecoderPool()
        el.append(W4DS, "W0")
        ds = el.get("W0")
        self.assertTrue(isinstance(ds, W4DS))
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        ds = el.get("UINT32")
        self.assertTrue(isinstance(ds, UINT32decoder))
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        el.pop("W0")
        el.pop("UINT32")
        ds = el.get("UTF8")
        self.assertTrue(isinstance(ds, UTF8decoder))
        self.assertEqual(el.get("UINT32"),None)
        ds = el.get("LIMA_VIDEO_IMAGE")
        self.assertTrue(isinstance(ds, VDEOdecoder))
        self.assertEqual(el.get("DDB"),None)
        self.assertEqual(el.get("W0"),None)


if __name__ == '__main__':
    unittest.main()
