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
from ndts.DataSources import DataSource

from Checkers import Checker 

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



from  xml.sax import SAXParseException



## test datasource
class TestDataSource(DataSource):
        ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        ## flag for running getData
        self.dataTaken = False
        ## list of dimensions
        self.dims = [] 
        ## if numpy  datasource
        self.numpy = True
        ## validity
        self.valid = True


    ## sets the parameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        pass


    ## access to data
    # \brief It is an abstract method providing data   
    def getData(self):
        self.dataTaken = True
        if len(self.dims) == 0:
            return {"format":NTP.rTf[0], "value":1, 
                    "tangoDType":"DevLong", "shape":[0,0]}
        elif numpy:
            return {"format":NTP.rTf[len(self.dims)], "value":numpy.ones(self.dims), 
                    "tangoDType":"DevLong", "shape":self.dims}
        elif len(self.dims) == 1:
            return {"format":NTP.rTf[1], "value":([1] * self.dims[0]), 
                    "tangoDType":"DevLong", "shape":[self.dims[0], 0]}
        elif len(self.dims) == 2:
            return {"format":NTP.rTf[2], "value":([[1] * self.dims[1]]*self.dims[0] ), 
                    "tangoDType":"DevLong", "shape":[self.dims[0], 0]}
        
        

    ## checks if the data is valid
    # \returns if the data is valid
    def isValid(self):
        return self.valid


    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return "Test DataSource"



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

        self._sc = Checker(self)

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
        self._nxFile = nx.create_file(self._fname, overwrite=True)
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
        self._nxFile.close()
        os.remove(self._fname)



    ## default store method
    # \brief It tests default settings
    def test_store_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
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
        
        self.myAssertRaise(ValueError, el.store)
        

        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)


    ## default store method
    # \brief It tests default settings
    def test_store_grows_1(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = EField("field", self._fattrs, eFile)
        ds = TestDataSource()
        el.source = ds
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, None)
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 5)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), (None, None))

        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)


    ## default store method
    # \brief It tests default settings
    def test_store_grows_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = EField("field", self._fattrs, eFile)
        ds = TestDataSource()
        el.source = ds
        el.strategy = 'STEP'
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 5)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('STEP', None))
        self.assertEqual(el.grows, 1)
        self._nxFile.close()
        os.remove(self._fname)
        


    ## default store method
    # \brief It tests default settings
    def test_store_grows_3(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = EField("field", self._fattrs, eFile)
        ds = TestDataSource()
        el.source = ds
        el.strategy = 'STEP'
        el.grows = 2
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, 2)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 5)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('STEP', None))
        self.assertEqual(el.grows, 2)
        self._nxFile.close()
        os.remove(self._fname)
        


    ## default store method
    # \brief It tests default settings
    def test_store_grows_4(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = EField("field", self._fattrs, eFile)
        ds = TestDataSource()
        el.source = ds
        el.strategy = 'INIT'
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'INIT')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 5)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), ('INIT', None))
        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)
        

    ## default store method
    # \brief It tests default settings
    def test_store_grows_5(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = EField("field", self._fattrs, eFile)
        ds = TestDataSource()
        ds.valid = False
        el.source = ds
        el.strategy = 'STEP'
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "field")
        self.assertEqual(el.content, [])
        self.assertEqual(el.rank, "0")
        self.assertEqual(el.lengths, {})
        self.assertEqual(el.strategy, 'STEP')
        self.assertEqual(el.source, ds)
        self.assertEqual(el.trigger, None)
        self.assertEqual(el.grows, None)
        self.assertEqual(el.compression, False)
        self.assertEqual(el.rate, 5)
        self.assertEqual(el.shuffle, True)
        self.assertEqual(el.store(), None)
        self.assertEqual(el.grows, None)
        self._nxFile.close()
        os.remove(self._fname)


    ## default store method
    # \brief It tests default settings
    def test_store_create_0d_step(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        attrs = {
            "string":["My string","NX_CHAR", "string"],
            "string2":["My string","NX_CHAR", ""],
            "datetime":["12:34:34","NX_DATE_TIME", "string"],
            "iso8601":["12:34:34","ISO8601", "string"],
            "int":[-132,"NX_INT", self._bint],
            "int8":[13,"NX_INT8", "int8"],
            "int16":[-223,"NX_INT16", "int16"],
            "int32":[13235,"NX_INT32", "int32"],
            "int64":[-12425,"NX_INT64", "int64"],
            "uint":[123,"NX_UINT", self._buint],
            "uint8":[65,"NX_UINT8", "uint8"],
            "uint16":[453,"NX_UINT16", "uint16"],
            "uint32":[12235,"NX_UINT32", "uint32"],
            "uint64":[14345,"NX_UINT64", "uint64"],
            "float":[-16.345,"NX_FLOAT", self._bfloat,1.e-14],
            "number":[-2.345e+2,"NX_NUMBER", self._bfloat,1.e-14],
            "float32":[-4.355e-1,"NX_FLOAT32", "float32",1.e-5],
            "float64":[-2.345,"NX_FLOAT64", "float64",1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool"],
            }



        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        for k in attrs: 
            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, 'STEP')
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), ("STEP",None))
            self.assertEqual(el[k].grows, 1)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.shape,(0,))
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.size,0)
            self.assertEqual(h5.nattrs, 2)
            self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
            self._sc.checkScalarAttribute(h5, "units", "string", "m")
            
        self._nxFile.close()
        os.remove(self._fname)



    ## default store method
    # \brief It tests default settings
    def test_store_create_0d_initfinal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        attrs = {
            "string":["My string","NX_CHAR", "string"],
            "string2":["My string","NX_CHAR", ""],
            "datetime":["12:34:34","NX_DATE_TIME", "string"],
            "iso8601":["12:34:34","ISO8601", "string"],
            "int":[-132,"NX_INT", self._bint],
            "int8":[13,"NX_INT8", "int8"],
            "int16":[-223,"NX_INT16", "int16"],
            "int32":[13235,"NX_INT32", "int32"],
            "int64":[-12425,"NX_INT64", "int64"],
            "uint":[123,"NX_UINT", self._buint],
            "uint8":[65,"NX_UINT8", "uint8"],
            "uint16":[453,"NX_UINT16", "uint16"],
            "uint32":[12235,"NX_UINT32", "uint32"],
            "uint64":[14345,"NX_UINT64", "uint64"],
            "float":[-16.345,"NX_FLOAT", self._bfloat,1.e-14],
            "number":[-2.345e+2,"NX_NUMBER", self._bfloat,1.e-14],
            "float32":[-4.355e-1,"NX_FLOAT32", "float32",1.e-5],
            "float64":[-2.345,"NX_FLOAT64", "float64",1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool"],
            }



        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        flip = False
        for k in attrs: 
            flip = not flip
            stt = 'INIT' if flip else 'FINAL'
            if attrs[k][1]:
                el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            else:    
                el[k] = EField("field", {"name":k, "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].source = ds

            el[k].strategy = stt
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt,None))
            self.assertEqual(el[k].grows, None)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.shape,(1,))
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.size,1)
            self.assertEqual(h5.nattrs, 2)
            self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
            self._sc.checkScalarAttribute(h5, "units", "string", "m")
            
            
        self._nxFile.close()
        os.remove(self._fname)


    ## default store method
    # \brief It tests default settings
    def test_store_create_0d_postrun(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        attrs = {
            "none":["My string","NX_CHAR", ""],
            "string":["My string","NX_CHAR", "string"],
            "datetime":["12:34:34","NX_DATE_TIME", "string"],
            "iso8601":["12:34:34","ISO8601", "string"],
            "int":[-132,"NX_INT", self._bint],
            "int8":[13,"NX_INT8", "int8"],
            "int16":[-223,"NX_INT16", "int16"],
            "int32":[13235,"NX_INT32", "int32"],
            "int64":[-12425,"NX_INT64", "int64"],
            "uint":[123,"NX_UINT", self._buint],
            "uint8":[65,"NX_UINT8", "uint8"],
            "uint16":[453,"NX_UINT16", "uint16"],
            "uint32":[12235,"NX_UINT32", "uint32"],
            "uint64":[14345,"NX_UINT64", "uint64"],
            "float":[-16.345,"NX_FLOAT", self._bfloat,1.e-14],
            "number":[-2.345e+2,"NX_NUMBER", self._bfloat,1.e-14],
            "float32":[-4.355e-1,"NX_FLOAT32", "float32",1.e-5],
            "float64":[-2.345,"NX_FLOAT64", "float64",1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool"],
            }



        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        for k in attrs: 
            stt = 'POSTRUN'
            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].postrun = k
            el[k].strategy = stt
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt,None))
            self.assertEqual(el[k].grows, None)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.shape,(1,))
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.size,1)
            self.assertEqual(h5.nattrs, 3)
            self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
            self._sc.checkScalarAttribute(h5, "units", "string", "m")
            self._sc.checkScalarAttribute(h5, "postrun", "string", k)

        

            
        self._nxFile.close()
        os.remove(self._fname)


    ## default store method
    # \brief It tests default settings
    def test_store_create_1d_step(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  


        attrs = {
            "string":["My string","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }

        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        quot = 0
        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(0, 3)]
#                attrs[k][0] =  [[ attrs[k][0]*random.randint(0, 3) for r in range(mlen[1]) ] for c in range(mlen[0])]
                attrs[k][0] =  [ attrs[k][0]*random.randint(0, 3) for r in range(mlen[0]) ] 
            else:    
                mlen = [random.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] =  [ bool(random.randint(0,1))  for c in range(mlen[0]) ]
                else:
                    attrs[k][0] =  [ ("true" if random.randint(0,1) else "false")  for c in range(mlen[0]) ]

            attrs[k][3] =  (mlen[0],)



            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].rank = "1"
            el[k].lengths = {"1":str(attrs[k][3][0])}
            el[k].source = ds
            el[k].grows = grow
            
            el[k].strategy = 'STEP'
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1":str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, 'STEP')
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), ("STEP",None))
            self.assertEqual(el[k].grows, grow if grow else 1)
            

        trip = 0
        for k in attrs: 
            trip = (trip + 1) %3
            grow = trip -1 if trip else  None
            h5 = el[k].h5Object
            if el[k].grows == 2:
                self.assertEqual(h5.shape, (attrs[k][3][0],0))
            else:
                self.assertEqual(h5.shape, (0,attrs[k][3][0]))
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(h5.size,0)
                self.assertEqual(h5.nattrs, 2)
                self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
            
        self._nxFile.close()
        os.remove(self._fname)


    ## default store method
    # \brief It tests default settings
    def test_store_create_1d_initfinal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  


        attrs = {
            "string":["My string","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }

        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        flip = False
        for k in attrs: 
            flip = not flip
            stt = 'INIT' if flip else 'FINAL'
            
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(0, 3)]
                attrs[k][0] =  [attrs[k][0]*random.randint(0,3)  for c in range(mlen[0])]
            else:    
                mlen = [random.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] =  [ bool(random.randint(0,1))  for c in range(mlen[0]) ]
                else:
                    attrs[k][0] =  [ ("true" if random.randint(0,1) else "false")  for c in range(mlen[0]) ]

            attrs[k][3] =  (mlen[0],)



            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].rank = "1"
            el[k].lengths = {"1":str(attrs[k][3][0])}
            el[k].source = ds
            el[k].strategy = stt
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1":str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt,None))
            self.assertEqual(el[k].grows, None)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.shape,(attrs[k][3][0],))
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(h5.size,attrs[k][3][0])
                self.assertEqual(h5.nattrs, 2)
                self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
            
        self._nxFile.close()
        os.remove(self._fname)



    ## default store method
    # \brief It tests default settings
    def test_store_create_1d_postrun(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  


        attrs = {
            "string":["My string","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }

        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        flip = False
        for k in attrs: 
            flip = not flip
            stt = 'POSTRUN'
            
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(0, 3)]
                attrs[k][0] =  [ attrs[k][0]*random.randint(0, 3) for c in range(mlen[0] )]
            else:    
                mlen = [random.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] =  [ bool(random.randint(0,1))  for c in range(mlen[0]) ]
                else:
                    attrs[k][0] =  [ ("true" if random.randint(0,1) else "false")  for c in range(mlen[0]) ]

            attrs[k][3] =  (mlen[0],)



            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].rank = "1"
            el[k].lengths = {"1":str(attrs[k][3][0])}
            el[k].source = ds
            el[k].strategy = stt
            el[k].postrun = k
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "1")
            self.assertEqual(el[k].lengths, {"1":str(attrs[k][3][0])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt,None))
            self.assertEqual(el[k].grows, None)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.shape,(attrs[k][3][0],))
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(h5.size,attrs[k][3][0])
                self.assertEqual(h5.nattrs, 3)
                self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
                self._sc.checkScalarAttribute(h5, "postrun", "string", k)
            
        self._nxFile.close()
        os.remove(self._fname)


    ## default store method
    # \brief It tests default settings
    def test_store_create_2d_step(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  


        attrs = {
            "string":["My string","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }


        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(1, 10), random.randint(0,3)]
                attrs[k][0] =  [[ attrs[k][0]*random.randint(0,3) for c in range(mlen[1]) ] for i in range(mlen[0])]
            else:    
                mlen = [random.randint(1, 10),random.randint(1, 10) ]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(random.randint(0,1))  for c in range(mlen[1]) ] for r in range(mlen[0])]
                else:
                    attrs[k][0] =  [[ ("True" if random.randint(0,1) else "False")  for c in range(mlen[1]) ] for r in range(mlen[0])]
                    
            attrs[k][3] =  (mlen[0],mlen[1])


        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        quin = 0
        for k in attrs: 
            quin = (quin + 1) %5
            grow = quin-1 if quin   else  None
            


            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].rank = "2"
            el[k].lengths = {"1":str(attrs[k][3][0]),"2":str(attrs[k][3][1])}
            el[k].source = ds
            el[k].grows = grow
            el[k].strategy = 'STEP'
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {"1":str(attrs[k][3][0]),"2":str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, 'STEP')
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, grow)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), ("STEP",None))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(el[k].grows, grow if grow else 1)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            if attrs[k][2] and attrs[k][2] != 'string':
                if el[k].grows == 3:
                    self.assertEqual(h5.shape,(attrs[k][3][0],attrs[k][3][1],0))
                elif el[k].grows == 2:
                    self.assertEqual(h5.shape,(attrs[k][3][0],0,attrs[k][3][1]))
                else:
                    self.assertEqual(h5.shape,(0,attrs[k][3][0],attrs[k][3][1]))
                self.assertEqual(h5.size,0)
                self.assertEqual(h5.nattrs, 2)
                self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
            else:
                self.assertEqual(h5.shape,(0,attrs[k][3][0],attrs[k][3][1]))

            
        self._nxFile.close()
        os.remove(self._fname)




    ## default store method
    # \brief It tests default settings
    def test_store_create_2d_initfinal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  


        attrs = {
            "string":["My string","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }


        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(1, 10), random.randint(0,3)]
                attrs[k][0] =  [[[ attrs[k][0]*random.randint(0,3) ] for r in range(mlen[1]) ] for c in range(mlen[0])]
            else:    
                mlen = [random.randint(1, 10),random.randint(1, 10) ]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(random.randint(0,1))  for c in range(mlen[1]) ] for r in range(mlen[0])]
                else:
                    attrs[k][0] =  [[ ("True" if random.randint(0,1) else "False")  for c in range(mlen[1]) ] for r in range(mlen[0])]
                    
            attrs[k][3] =  (mlen[0],mlen[1])


        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        quin = 0
        flip = False
        for k in attrs: 
            flip = not flip
            quin = (quin + 1) %5
            grow = quin-1 if quin   else  None
            stt = 'INIT' if flip else 'FINAL'
            


            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].rank = "2"
            el[k].lengths = {"1":str(attrs[k][3][0]),"2":str(attrs[k][3][1])}
            el[k].source = ds
            el[k].strategy = stt
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {"1":str(attrs[k][3][0]),"2":str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt,None))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(el[k].grows, None)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.shape,(attrs[k][3][0],attrs[k][3][1]))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(h5.size,attrs[k][3][0]*attrs[k][3][1])
                self.assertEqual(h5.nattrs, 2)
                self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")

            
        self._nxFile.close()
        os.remove(self._fname)






    ## default store method
    # \brief It tests default settings
    def test_store_create_2d_postrun(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  


        attrs = {
            "string":["My string","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }


        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(1, 10), random.randint(0,3)]
                attrs[k][0] =  [[ attrs[k][0]*random.randint(0,3) for r in range(mlen[1])] for c in range(mlen[0])]
            else:    
                mlen = [random.randint(1, 10),random.randint(1, 10) ]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(random.randint(0,1))  for c in range(mlen[1]) ] for r in range(mlen[0])]
                else:
                    attrs[k][0] =  [[ ("True" if random.randint(0,1) else "False")  for c in range(mlen[1]) ] for r in range(mlen[0])]
                    
            attrs[k][3] =  (mlen[0],mlen[1])


        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        quin = 0
        flip = False
        for k in attrs: 
            flip = not flip
            quin = (quin + 1) %5
            grow = quin-1 if quin   else  None
            stt = 'INIT' if flip else 'FINAL'
            


            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            ds = TestDataSource()
            ds.valid = True
            el[k].rank = "2"
            el[k].lengths = {"1":str(attrs[k][3][0]),"2":str(attrs[k][3][1])}
            el[k].source = ds
            el[k].postrun = k
            stt = 'POSTRUN'
            el[k].strategy = stt
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "2")
            self.assertEqual(el[k].lengths, {"1":str(attrs[k][3][0]),"2":str(attrs[k][3][1])})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].source, ds)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

            self.assertEqual(el[k].store(), (stt,None))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(el[k].grows, None)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.shape,(attrs[k][3][0],attrs[k][3][1]))
            if attrs[k][2] and attrs[k][2] != 'string':
                self.assertEqual(h5.size,attrs[k][3][0]*attrs[k][3][1])
                self.assertEqual(h5.nattrs, 3)
                self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
                self._sc.checkScalarAttribute(h5, "units", "string", "m")
                self._sc.checkScalarAttribute(h5, "postrun", "string", k)

            
        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_store_createAttributes_0d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        attrs = {
            "string":["My string","NX_CHAR", "string"],
            "datetime":["12:34:34","NX_DATE_TIME", "string"],
            "iso8601":["12:34:34","ISO8601", "string"],
            "int":[-123,"NX_INT", self._bint],
            "int8":[12,"NX_INT8", "int8"],
            "int16":[-123,"NX_INT16", "int16"],
            "int32":[12345,"NX_INT32", "int32"],
            "int64":[-12345,"NX_INT64", "int64"],
            "uint":[123,"NX_UINT", self._buint],
            "uint8":[12,"NX_UINT8", "uint8"],
            "uint16":[123,"NX_UINT16", "uint16"],
            "uint32":[12345,"NX_UINT32", "uint32"],
            "uint64":[12345,"NX_UINT64", "uint64"],
            "float":[-12.345,"NX_FLOAT", self._bfloat,1.e-14],
            "number":[-12.345e+2,"NX_NUMBER", self._bfloat,1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32",1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64",1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool"],
            "bool2":["FaLse","NX_BOOLEAN", "bool"],
            "bool3":["false","NX_BOOLEAN", "bool"],
            "bool4":["true","NX_BOOLEAN", "bool"]
            }

        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)

        el = {}
        for k in attrs.keys():
            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]))
            ds = TestDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store() 
            at = el[k].h5Attribute(k)
            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[k][0])),at.value)
            
            elif len(attrs[k]) > 3:
                self.assertTrue(abs(at.value - attrs[k][0]) <= attrs[k][3])
            else: 
                self.assertEqual(at.value, attrs[k][0])


        for k in attrs.keys():
            el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]), [])
            el[k]._createAttributes() 
            at = el[k].h5Object.attr(k)
#            at = el[k].h5Attribute(k)
            self._sc.checkScalarAttribute(el[k].h5Object, k, attrs[k][2], attrs[k][0], 
                                          attrs[k][3] if len(attrs[k])>3 else 0)

        for k in attrs.keys():
            if attrs[k][2] == 'string':
                "writing multi-dimensional string is not supported by pninx"
                continue
            el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]), [1])
            el[k]._createAttributes() 
#            at = el[k].h5Attribute(k)
            at = el[k].h5Object.attr(k)
            self._sc.checkSpectrumAttribute(el[k].h5Object, k, attrs[k][2], [attrs[k][0]], 
                                            attrs[k][3] if len(attrs[k])>3 else 0)

        self._nxFile.close()
 
#        os.remove(self._fname)
 
    ## constructor test
    # \brief It tests default settings
    def test_store_createAttributes_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  


        attrs = {
#            "string":["My string","NX_CHAR", "string" , (1,)],
#            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
#            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }

        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)

        el = {}
        for k in attrs.keys():
            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], str(attrs[k][0]),attrs[k][3] )

            ds = TestDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store() 
            at = el[k].h5Object.attr(k)
            self._sc.checkSpectrumAttribute(el[k].h5Object, k, attrs[k][2], [attrs[k][0]] , 
                                            attrs[k][3] if len(attrs[k])>3 else 0)







    ## constructor test
    # \brief It tests default settings
    def test_store_createAttributes_1d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        

        attrs = {
#            "string":["My string","NX_CHAR", "string" , (1,)],
#            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
#            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }


        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(0, 3)]
                attrs[k][0] =  [ attrs[k][0]*random.randint(0, 3)  for r in range(mlen[0])]
            else:    
                mlen = [random.randint(1, 10)]
                if k == 'bool':
                    attrs[k][0] =  [ bool(random.randint(0,1))  for c in range(mlen[0]) ]
                else:
                    attrs[k][0] =  [ ("true" if random.randint(0,1) else "false")  for c in range(mlen[0]) ]

            attrs[k][3] =  (mlen[0],)


        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)

        el = {}
        for k in attrs.keys():
            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], "".join([str(it)+ " "  for it in attrs[k][0]]),attrs[k][3] )

            ds = TestDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store() 

            at = el[k].h5Object.attr(k)

            self._sc.checkSpectrumAttribute(el[k].h5Object, k, attrs[k][2], attrs[k][0] , 
                                            attrs[k][3] if len(attrs[k])>3 else 0)





    ## constructor test
    # \brief It tests default settings
    def test_store_createAttributes_2d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        

        attrs = {
#            "string":["My string","NX_CHAR", "string" , (1,)],
#            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
#            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", self._bint, (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", self._buint, (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", self._bfloat, (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  self._bfloat,(1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            "bool2":["FaLse","NX_BOOLEAN", "bool", (1,)], 
            "bool3":["false","NX_BOOLEAN", "bool", (1,)],
            "bool4":["true","NX_BOOLEAN", "bool", (1,)]
            }

        for k in attrs.keys():
            if attrs[k][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(1, 10), random.randint(0,3)]
                attrs[k][0] =  [[ attrs[k][0]*random.randint(0,3) for r in range(mlen[1]) ] for c in range(mlen[0])]
            else:    
                mlen = [random.randint(1, 10),random.randint(1, 10) ]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(random.randint(0,1))  for c in range(mlen[1]) ] for r in range(mlen[0])]
                else:
                    attrs[k][0] =  [[ ("True" if random.randint(0,1) else "False")  for c in range(mlen[1]) ]for r in range(mlen[0])]
                    
            attrs[k][3] =  (mlen[0],mlen[1])

            
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)

        el = {}
        for k in attrs.keys():
            el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)

            self.assertEqual(el[k].tagAttributes, {})
            el[k].tagAttributes[k] = (attrs[k][1], 
                                     "".join(["".join([str(it)+ " "  for it in sub]
                                                      ) + "\n" for sub in attrs[k][0]]),
                                     attrs[k][3] 
                                     )

            ds = TestDataSource()
            ds.valid = True
            el[k].source = ds
            el[k].strategy = 'STEP'

            el[k].store() 


            at = el[k].h5Object.attr(k)
            self._sc.checkImageAttribute(el[k].h5Object, k, attrs[k][2], attrs[k][0] , 
                                            attrs[k][4] if len(attrs[k])>4 else 0)

            self.assertEqual(at.dtype, attrs[k][2])
            if attrs[k][2] == "bool":
                for i in range(len(attrs[k][0])):
                    for j in range(len(attrs[k][0][i])):
                        self.assertEqual(Converters.toBool(str(attrs[k][0][i][j])), at.value[i,j])
                pass
            elif len(attrs[k]) > 4:
                for i in range(len(attrs[k][0])):
                    for j in range(len(attrs[k][0][i])):
                        self.assertTrue(abs(at.value[i][j] - attrs[k][0][i][j]) <= attrs[k][4])
            else: 
                for i in range(len(attrs[k][0])):
                    for j in range(len(attrs[k][0][i])):
                        self.assertEqual(at.value[i][j], attrs[k][0][i][j])





    ## default store method
    # \brief It tests default settings
    def test_store_value_0d_initfinal(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  

        attrs = {
            "string":["My string","NX_CHAR", "string"],
            "string2":["My string","NX_CHAR", ""],
            "datetime":["12:34:34","NX_DATE_TIME", "string"],
            "iso8601":["12:34:34","ISO8601", "string"],
            "int":[-132,"NX_INT", self._bint],
            "int8":[13,"NX_INT8", "int8"],
            "int16":[-223,"NX_INT16", "int16"],
            "int32":[13235,"NX_INT32", "int32"],
            "int64":[-12425,"NX_INT64", "int64"],
            "uint":[123,"NX_UINT", self._buint],
            "uint8":[65,"NX_UINT8", "uint8"],
            "uint16":[453,"NX_UINT16", "uint16"],
            "uint32":[12235,"NX_UINT32", "uint32"],
            "uint64":[14345,"NX_UINT64", "uint64"],
            "float":[-16.345,"NX_FLOAT", self._bfloat,1.e-14],
            "number":[-2.345e+2,"NX_NUMBER", self._bfloat,1.e-14],
            "float32":[-4.355e-1,"NX_FLOAT32", "float32",1.e-5],
            "float64":[-2.345,"NX_FLOAT64", "float64",1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool"],
            }



        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile("NXfile", [], None, self._nxFile)
        el = {} 
        flip = False
        for k in attrs: 
            flip = not flip
            stt = 'INIT' if flip else 'FINAL'
            if attrs[k][1]:
                el[k] = EField("field", {"name":k, "type":attrs[k][1], "units":"m"}, eFile)
            else:    
                el[k] = EField("field", {"name":k, "units":"m"}, eFile)

            el[k].strategy = stt
        
            self.assertTrue(isinstance(el[k], Element))
            self.assertTrue(isinstance(el[k], FElement))
            self.assertTrue(isinstance(el[k], FElementWithAttr))
            self.assertEqual(el[k].tagName, "field")
            self.assertEqual(el[k].content, [])
            self.assertEqual(el[k].rank, "0")
            self.assertEqual(el[k].lengths, {})
            self.assertEqual(el[k].strategy, stt)
            self.assertEqual(el[k].trigger, None)
            self.assertEqual(el[k].grows, None)
            self.assertEqual(el[k].compression, False)
            self.assertEqual(el[k].rate, 5)
            self.assertEqual(el[k].shuffle, True)

#            self.assertEqual(el[k].store(), None)
            self.myAssertRaise(ValueError, el[k].store)
            self.assertEqual(el[k].grows, None)
            

        for k in attrs: 
            h5 = el[k].h5Object
            self.assertEqual(h5.shape,(1,))
            self.assertEqual(h5.dtype,attrs[k][2] if attrs[k][2] else 'string')
            self.assertEqual(h5.size,1)
            self.assertEqual(h5.nattrs, 2)
            self._sc.checkScalarAttribute(h5, "type", "string", attrs[k][1])
            self._sc.checkScalarAttribute(h5, "units", "string", "m")
            
            
        self._nxFile.close()
        os.remove(self._fname)


        

if __name__ == '__main__':
    unittest.main()
