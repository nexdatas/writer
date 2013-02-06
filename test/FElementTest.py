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
import random
import numpy


import pni.io.nx.h5 as nx

from ndts.Element import Element
from ndts.H5Elements import FElement
from ndts.H5Elements import EFile
from ndts.ThreadPool import ThreadPool
from ndts.DataSources import DataSource
from ndts.H5Elements import XMLSettingSyntaxError
from ndts.Types import NTP

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
        return True


    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return "Test DataSource"



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
        el = FElement(self._tfname, self._fattrs, None)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.source, None)
        self.assertEqual(el.error, None)
        self.assertEqual(el.h5Object, None)

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
        self.assertEqual(el.source, None)
        self.assertEqual(el.error, None)
        self.assertEqual(el.h5Object, None)
        self.assertEqual(el2.h5Object, self._group)
        



    ## constructor test
    # \brief It tests default settings
    def test_store(self):
        print "Run: %s.test_store() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None, self._group )
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.store(), None)
        self.assertEqual(el.store("<tag/>"), None)
        


    ## run method test
    # \brief It tests run method
    def test_run(self):
        print "Run: %s.test_run() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None,  self._group )
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.run(), None)
        self.assertEqual(el.source, None)
        ds = TestDataSource()
        el.source = ds
        self.assertEqual(el.source, ds)
        self.assertTrue(hasattr(el.source, "getData"))
        self.assertTrue(not ds.dataTaken)
        self.assertEqual(el.run(), None)
        self.assertTrue(ds.dataTaken)


    ## run _findShape test
    # \brief It tests _findShape method
    def test_findShape_lengths_1d(self):
        print "Run: %s.test_findShape_lengths_1d() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None)


        self.myAssertRaise(ValueError, el._findShape, "")

        self.assertEqual(el._findShape("0"), [] )
        self.assertEqual(el._findShape("0", None, extraD=True), [0] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("0", None, extraD=True, grows = i), [0] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("0", None, extraD=False, grows = i), [] )


        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1")
        
        mlen = random.randint(1, 10000)        
        lens = {'1':str(mlen)}
        self.assertEqual(el._findShape("1",lengths = lens, extraD=False), [mlen] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("1",lengths = lens, extraD=False, grows = i), [mlen] )
        self.assertEqual(el._findShape("1",lengths = lens, extraD=True), [0, mlen] )
        for i in range(-2, 2):
            self.assertEqual(el._findShape("1",lengths = lens, extraD=True, grows = i), [0, mlen] )
        for i in range(2, 5):
            self.assertEqual(el._findShape("1",lengths = lens, extraD=True, grows = i), [mlen, 0] )

        lens = {'1':str(0)}

        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1", lengths = lens, extraD=False)
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1", lengths = lens, extraD=True)

        mlen = random.randint(-10000, 0)        
        lens = {'1':str(mlen)}

        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1", lengths = lens, extraD=False)
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1", lengths = lens, extraD=True)

        for i in range(-2, 5):
            self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1", lengths = lens, extraD=True, grows=i)

        mlen = random.randint(1, 1000)        
        lens = {'2':str(mlen)}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1", lengths = lens)

        mlen = random.randint(1, 1000)        
        lens = {'2':str(mlen)}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "1", lengths = lens,  extraD = True)



        


    ## run _findShape test
    # \brief It tests _findShape method
    def test_findShape_lengths_2d(self):
        print "Run: %s.test_findShape_lengths_2d() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None)

        
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2")

        
        mlen = [random.randint(1, 1000),random.randint(1, 1000) ]
        lens = {'1':str(mlen[0]),'2':str(mlen[1])}
        self.assertEqual(el._findShape("2",lengths = lens, extraD=False), mlen )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("2",lengths = lens, extraD=False, grows = i), mlen )
        self.assertEqual(el._findShape("2",lengths = lens, extraD=True), [0]+ mlen )
        for i in range(-2, 2):
            self.assertEqual(el._findShape("2",lengths = lens, extraD=True, grows = i), [0] + mlen )
        self.assertEqual(el._findShape("2",lengths = lens, extraD=True, grows = 2), [mlen[0], 0, mlen[1]] )
        for i in range(3, 5):
            self.assertEqual(el._findShape("2",lengths = lens, extraD=True, grows = i), mlen + [0] )


        lens = {'1':'0', '2':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = False)

        lens = {'2':'0', '1':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = False)

        lens = {'2':'0', '1':'0'}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = False)


        lens = {'1':'0', '2':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = True)

        lens = {'2':'0', '1':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = True)

        lens = {'1':'0', '2':'0'}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = True)

        nlen = [random.randint(-1000, 0), random.randint(-1000, 0)]
        lens = {'1':str(mlen[0]),'2':str(nlen[1])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = False)
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = True)

        for i in range(-2, 5):
            self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD=True, grows = i)
                


        mlen = random.randint(1, 1000)        
        lens = {'2':str(mlen), '3':str(mlen)}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens)

        mlen = random.randint(1, 1000)        
        lens = {'2':str(mlen)}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "2",lengths = lens, extraD = True)



    ## run _findShape test
    # \brief It tests _findShape method
    def test_findShape_lengths_3d(self):
        print "Run: %s.test_findShape_lengths_3d() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None)


        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3")

        
        mlen = [random.randint(1, 100),random.randint(1, 100), random.randint(1, 100) ]
        lens = {'1':str(mlen[0]),'2':str(mlen[1]),'3':str(mlen[2])}
        self.assertEqual(el._findShape("3",lengths = lens, extraD=False), mlen )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("3",lengths = lens, extraD=False, grows = i), mlen )
        self.assertEqual(el._findShape("3",lengths = lens, extraD=True), [0]+ mlen )
        for i in range(-2, 2):
            self.assertEqual(el._findShape("3",lengths = lens, extraD=True, grows = i), [0] + mlen )
        self.assertEqual(el._findShape("3",lengths = lens, extraD=True, grows = 2), 
                         [mlen[0], 0, mlen[1], mlen[2]] )
        self.assertEqual(el._findShape("3",lengths = lens, extraD=True, grows = 3), 
                         [mlen[0],  mlen[1], 0, mlen[2]] )
        for i in range(4, 5):
            self.assertEqual(el._findShape("3",lengths = lens, extraD=True, grows = i), mlen + [0] )

        lens = {'1':'0', '2':str(mlen[0]), '3':str(mlen[1])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=False)
        lens = {'2':'0', '1':str(mlen[0]), '3':str(mlen[1])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=False)
        lens = {'1':'0', '2':'0', '3':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=False)
        lens = {'2':'0', '3':'0', '1':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=False)
        lens = {'3':'0', '1':'0', '2':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=False)



        lens = {'1':'0', '2':str(mlen[0]), '3':str(mlen[1])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True)
        lens = {'2':'0', '1':str(mlen[0]), '3':str(mlen[1])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True)
        lens = {'1':'0', '2':'0', '3':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True)
        lens = {'2':'0', '3':'0', '1':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True)
        lens = {'3':'0', '1':'0', '2':str(mlen[0])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True)



        nlen = [random.randint(-100, 0), random.randint(-100, 0)]
        lens = {'1':str(mlen[0]),'2':str(nlen[1]),'3':str(mlen[1])}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=False)
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True)
        for i in range(-2, 5):
            self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True,grows = i)


        mlen = random.randint(1, 1000)        
        lens = {'2':str(mlen), '3':str(mlen), '4':str(mlen)}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens)

        mlen = random.randint(1, 1000)        
        lens = {'2':str(mlen)}
        self.myAssertRaise(XMLSettingSyntaxError, el._findShape, "3", lengths = lens, extraD=True)


    ## run _findShape test
    # \brief It tests _findShape method
    def test_findShape_ds_1d(self):
        print "Run: %s.test_findShape_ds_1d() " % self.__class__.__name__
        ds = TestDataSource()
        el = FElement(self._tfname, self._fattrs, None)
        el.source = ds
        
        self.assertEqual(el._findShape("0"), [] )

        self.assertEqual(el._findShape("0", None, extraD=True), [0] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("0", None, extraD=True, grows = i), [0] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("0", None, extraD=False, grows = i), [] )

        

        mlen = random.randint(1, 10000)        
        el.source.dims = [mlen]
        self.assertEqual(el._findShape("1", extraD=False), [mlen] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("1", extraD=False, grows = i), [mlen] )
        self.assertEqual(el._findShape("1", extraD=True), [0, mlen] )
        for i in range(-2, 2):
            self.assertEqual(el._findShape("1", extraD=True, grows = i), [0, mlen] )
        for i in range(2, 5):
            self.assertEqual(el._findShape("1", extraD=True, grows = i), [mlen, 0] )

        el.source.dims = [0]
        self.assertEqual(el._findShape("1"), [] )


        el.source.numpy = False


        mlen = random.randint(1, 10000)        
        el.source.dims = [mlen]
        self.assertEqual(el._findShape("1", extraD=False), [mlen] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("1", extraD=False, grows = i), [mlen] )
        self.assertEqual(el._findShape("1", extraD=True), [0, mlen] )
        for i in range(-2, 2):
            self.assertEqual(el._findShape("1", extraD=True, grows = i), [0, mlen] )
        for i in range(2, 5):
            self.assertEqual(el._findShape("1", extraD=True, grows = i), [mlen, 0] )

        el.source.dims = [0]
        self.assertEqual(el._findShape("1"), [] )



    ## run _findShape test
    # \brief It tests _findShape method
    def test_findShape_ds_2d(self):
        print "Run: %s.test_findShape_ds_2d() " % self.__class__.__name__
        ds = TestDataSource()
        el = FElement(self._tfname, self._fattrs, None)
        el.source = ds
        

        el.source.numpy = True

        mlen = [random.randint(1, 1000),random.randint(1, 1000) ]
        el.source.dims = mlen
        self.assertEqual(el._findShape("2", extraD=False), mlen )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("2", extraD=False, grows = i), mlen )
        self.assertEqual(el._findShape("2", extraD=True), [0]+ mlen )
        for i in range(-2, 2):
            self.assertEqual(el._findShape("2", extraD=True, grows = i), [0] + mlen )
        self.assertEqual(el._findShape("2", extraD=True, grows = 2), [mlen[0], 0, mlen[1]] )
        for i in range(3, 5):
            self.assertEqual(el._findShape("2", extraD=True, grows = i), mlen + [0] )

        el.source.numpy = False

        mlen = [random.randint(1, 1000),random.randint(1, 1000) ]
        el.source.dims = mlen
        self.assertEqual(el._findShape("2", extraD=False), mlen )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("2", extraD=False, grows = i), mlen )
        self.assertEqual(el._findShape("2", extraD=True), [0]+ mlen )
        for i in range(-2, 2):
            self.assertEqual(el._findShape("2", extraD=True, grows = i), [0] + mlen )
        self.assertEqual(el._findShape("2", extraD=True, grows = 2), [mlen[0], 0, mlen[1]] )
        for i in range(3, 5):
            self.assertEqual(el._findShape("2", extraD=True, grows = i), mlen + [0] )





    ## run _findShape test
    # \brief It tests _findShape method
    def test_findShape_xml(self):
        print "Run: %s.test_findShape_xml() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None)
        
        el.content = ["123"]
        self.assertEqual(el._findShape("0"), [] )
        self.assertEqual(el._findShape("0", None, extraD=True), [0] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("0", None, extraD=True, grows = i), [0] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("0", None, extraD=False, grows = i), [] )

        
            
        mlen = random.randint(1, 10000)        
        el.content = ["123 "* mlen ]
        self.assertEqual(el._findShape("1", extraD=False), [mlen] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("1", extraD=False, grows = i), [mlen] )
        self.assertEqual(el._findShape("1", extraD=True), [ mlen] )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("1", extraD=True, grows = i), [mlen] )


        mlen = [random.randint(1, 1000),random.randint(1, 1000) ]
        el.content = ["123 "* mlen[1] + "\n " ]*mlen[0]
        self.assertEqual(el._findShape("2", extraD=False), mlen )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("2", extraD=False, grows = i), mlen )
        self.assertEqual(el._findShape("2", extraD=True), mlen )
        for i in range(-2, 5):
            self.assertEqual(el._findShape("2", extraD=True, grows = i), mlen )





    ## run setMessage test
    # \brief It tests setMessage method
    def test_setMessage(self):
        print "Run: %s.test_setMessage() " % self.__class__.__name__
        message = "My Exception"
        text = "WARNING: Data for %s on %s not found"
        uob = "unnamed object"
        uds = "unknown datasource"
        ds = TestDataSource()
        el = FElement(self._tfname, self._fattrs, None)
        self.assertEqual(el.setMessage(),(text % (uob, uds), None))
        self.assertEqual(el.setMessage(message),(text % (uob, uds), message))
        el.source = ds
        self.assertEqual(el.setMessage(),(text % (uob, str(ds)), None))
        self.assertEqual(el.setMessage(message),(text % (uob, str(ds)), message))

        el2 = FElement(self._tfname, self._fattrs, el, self._group )
        self.assertEqual(el2.setMessage(),(text % (self._group.name, uds), None))
        self.assertEqual(el2.setMessage(message),(text % (self._group.name, uds), message))
        el2.source = ds
        self.assertEqual(el2.setMessage(),(text % (self._group.name, str(ds)), None))
        self.assertEqual(el2.setMessage(message),(text % (self._group.name, str(ds)), message))
        



if __name__ == '__main__':
    unittest.main()
