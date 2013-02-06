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
## \file FElementTestWithAttrTest.py
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


from ndts.H5Elements import FElementWithAttr
from ndts.H5Elements import FElement
from ndts.Element import Element
from ndts.H5Elements import EFile
from ndts.Types import NTP, Converters

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



from  xml.sax import SAXParseException




## test fixture
class FElementWithAttrTest(unittest.TestCase):

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
        el = FElementWithAttr(self._tfname, self._fattrs, None)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, self._tfname)
        self.assertEqual(el.content, [])
        self.assertEqual(el.doc, "")
        self.assertEqual(el.source, None)
        self.assertEqual(el.error, None)
        self.assertEqual(el.h5Object, None)
        self.assertEqual(el.tagAttributes, {})


    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        print "Run: %s.test_constructor() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None )
        el2 = FElementWithAttr(self._tfname, self._fattrs, el, self._group)
        self.assertTrue(isinstance(el2, Element))
        self.assertTrue(isinstance(el2, FElement))
        self.assertTrue(isinstance(el2, FElementWithAttr))
        self.assertEqual(el2.tagName, self._tfname)
        self.assertEqual(el2.content, [])
        self.assertEqual(el2.doc, "")
        self.assertEqual(el.source, None)
        self.assertEqual(el.error, None)
        self.assertEqual(el.h5Object, None)
        self.assertEqual(el2.h5Object, self._group)
        self.assertEqual(el2.tagAttributes, {})
        



    ## constructor test
    # \brief It tests default settings
    def test_createAttributes_0d(self):
        print "Run: %s.test_createAttributes_0d() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None )
        el2 = FElementWithAttr(self._tfname, self._fattrs, el, self._group)
        self.assertEqual(el2.tagAttributes, {})

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
            "bool2":["false","NX_BOOLEAN", "bool"],
            "bool2":["true","NX_BOOLEAN", "bool"]
            }

        for nm in attrs.keys():
            el2.tagAttributes[nm] = (attrs[nm][1], str(attrs[nm][0]))
            el2._createAttributes() 
            at = el2.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])),at.value)
            
            elif len(attrs[nm]) > 3:
                self.assertTrue(abs(at.value - attrs[nm][0]) <= attrs[nm][3])
            else: 
                self.assertEqual(at.value, attrs[nm][0])


        for nm in attrs.keys():
            el2.tagAttributes[nm] = (attrs[nm][1], str(attrs[nm][0]), [])
            el2._createAttributes() 
            at = el2.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])),at.value)
            
            elif len(attrs[nm]) > 3:
                self.assertTrue(abs(at.value - attrs[nm][0]) <= attrs[nm][3])
            else: 
                self.assertEqual(at.value, attrs[nm][0])

        for nm in attrs.keys():
            if attrs[nm][2] == 'string':
                "writing multi-dimensional string is not supported by pninx"
                continue
            el2.tagAttributes[nm] = (attrs[nm][1], str(attrs[nm][0]), [1])
            el2._createAttributes() 
            at = el2.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])),at.value)
            
            elif len(attrs[nm]) > 3:
                self.assertTrue(abs(at.value - attrs[nm][0]) <= attrs[nm][3])
            else: 
                
                if isinstance(at.value, numpy.ndarray): 
                    self.assertEqual(at.value, numpy.array(attrs[nm][0],dtype = attrs[nm][2]))
                else:
                    self.assertEqual([at.value], attrs[nm][0])


    ## constructor test
    # \brief It tests default settings
    def test_createAttributes_1d_single(self):
        print "Run: %s.test_createAttributes_1d_single() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None )
        el2 = FElementWithAttr(self._tfname, self._fattrs, el, self._group)
        self.assertEqual(el2.tagAttributes, {})

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



        for nm in attrs.keys():
            if attrs[nm][2] == 'string':
                "writing multi-dimensional string is not supported by pninx"
                continue
            el2.tagAttributes[nm] = (attrs[nm][1], str(attrs[nm][0]),attrs[nm][3] )
            el2._createAttributes() 
            at = el2.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                self.assertEqual(Converters.toBool(str(attrs[nm][0])),at.value)
            
            elif len(attrs[nm]) > 4:
                self.assertTrue(abs(at.value - attrs[nm][0]) <= attrs[nm][4])
            else: 
                
                if isinstance(at.value, numpy.ndarray): 
                    self.assertEqual(at.value, numpy.array(attrs[nm][0],dtype = attrs[nm][2]))
                else:
                    self.assertEqual([at.value], attrs[nm][0])






    ## constructor test
    # \brief It tests default settings
    def test_createAttributes_1d(self):
        print "Run: %s.test_createAttributes_1d() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None )
        el2 = FElementWithAttr(self._tfname, self._fattrs, el, self._group)
        self.assertEqual(el2.tagAttributes, {})

        

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

        for nm in attrs.keys():
            if attrs[nm][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(0, 3)]
                attrs[nm][0] =  [ attrs[nm][0]*mlen[1] ]*mlen[0] 
            else:    
                mlen = [random.randint(1, 10)]
                if nm == 'bool':
                    attrs[nm][0] =  [ bool(random.randint(0,1))  for c in range(mlen[0]) ]
                else:
                    attrs[nm][0] =  [ ("true" if random.randint(0,1) else "false")  for c in range(mlen[0]) ]

            attrs[nm][3] =  (mlen[0],)


        for nm in attrs.keys():
            el2.tagAttributes[nm] = (attrs[nm][1], "".join([str(it)+ " "  for it in attrs[nm][0]]),attrs[nm][3] )
            el2._createAttributes() 
            at = el2.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                for i in range(len(attrs[nm][0])):
                    self.assertEqual(Converters.toBool(str(attrs[nm][0][i])),at.value[i])
                pass
            elif len(attrs[nm]) > 4:
                for i in range(len(attrs[nm][0])):
                    self.assertTrue(abs(at.value[i] - attrs[nm][0][i]) <= attrs[nm][4])
            else: 
                
                for i in range(len(attrs[nm][0])):
                    self.assertEqual(at.value[i], attrs[nm][0][i])





    ## constructor test
    # \brief It tests default settings
    def test_createAttributes_2d(self):
        print "Run: %s.test_createAttributes_1d() " % self.__class__.__name__
        el = FElement(self._tfname, self._fattrs, None )
        el2 = FElementWithAttr(self._tfname, self._fattrs, el, self._group)
        self.assertEqual(el2.tagAttributes, {})

        

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

        for nm in attrs.keys():
            if attrs[nm][2] != "bool":
                mlen = [random.randint(1, 10),random.randint(1, 10), random.randint(0,3)]
                attrs[nm][0] =  [[ attrs[nm][0]*mlen[2] ]*mlen[1] ]*mlen[0]
            else:    
                mlen = [random.randint(1, 10),random.randint(1, 10) ]
                if nm == 'bool':
                    attrs[nm][0] =  [[ bool(random.randint(0,1))  for c in range(mlen[1]) ]]*mlen[0]
                else:
                    attrs[nm][0] =  [[ ("True" if random.randint(0,1) else "False")  for c in range(mlen[1]) ]]*mlen[0]
                    
            attrs[nm][3] =  (mlen[0],mlen[1])

            
        for nm in attrs.keys():
            el2.tagAttributes[nm] = (attrs[nm][1], 
                                     "".join(["".join([str(it)+ " "  for it in sub]
                                                      ) + "\n" for sub in attrs[nm][0]]),
                                     attrs[nm][3] 
                                     )
            el2._createAttributes() 
            at = el2.h5Attribute(nm)
            self.assertEqual(at.dtype, attrs[nm][2])
            if attrs[nm][2] == "bool":
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertEqual(Converters.toBool(str(attrs[nm][0][i][j])), at.value[i,j])
                pass
            elif len(attrs[nm]) > 4:
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertTrue(abs(at.value[i][j] - attrs[nm][0][i][j]) <= attrs[nm][4])
            else: 
                for i in range(len(attrs[nm][0])):
                    for j in range(len(attrs[nm][0][i])):
                        self.assertEqual(at.value[i][j], attrs[nm][0][i][j])




        


if __name__ == '__main__':
    unittest.main()
