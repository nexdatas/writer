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
## \file FieldArrayTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import binascii
import time

from ndts.FieldArray import FieldArray
from Checkers import Checker

## True if pniio installed
PNIIO = False
try:
    import pni.io.nx.h5 as nx
    PNIIO = True
except:
    import pni.nx.h5 as nx


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class FieldArrayTest(unittest.TestCase):

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

        self._sc = Checker(self)
        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256) 
         
        self.__rnd = random.Random(self.__seed)


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "SEED =", self.__seed 
        print "CHECKER SEED =", self._sc.seed 
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
        name = "myfield"
        dtype = "string"
        shape = (10,2)
        value  = [["ble" for c in  range(shape[1])] for d in range(shape[0])]

        el = FieldArray(nxFile, name, dtype,shape)
        self.assertEqual(el.name, name)
        self.assertEqual(el.dtype, dtype)
        self.assertEqual(el.shape, shape)
        self.assertEqual(el.chunk, None)
        el.write(value)

        nxFile.close()

        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        self.assertEqual(f.nchildren, 2)

        self._sc.checkSingleStringImageField(f, name, 'string', 'NX_CHAR', value, attrs = {} )

        for i in range(shape[1]):
            fl = f.open("%s_%s" %(name, i) )

        f.close()



        os.remove(fname)



    ## constructor test
    # \brief It tests default settings
    def test_read_write_0d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)


        attrs = {
            "string":["My string","NX_CHAR", "string"],
#            "string2":["My string","NX_CHAR", ""],
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

        name = "myfield"
        dtype = "string"
        shape = ()
        value = {}
        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],shape)
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, shape)
            self.assertEqual(el.chunk, None)
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        self.assertEqual(f.nchildren, len(attrs))
        for k in attrs:
            self._sc.checkSingleScalarField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], attrs[k][0], 
                                            error = attrs[k][3] if len(attrs[k])> 3 else 0, 
                                            attrs = {}
                                            )
            self._sc.checkSingleScalarField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], value[k],
                                            error = attrs[k][3] if len(attrs[k])> 3 else 0, 
                                            attrs = {}
                                            )
            
        f.close()




        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_read_write_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
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
            }

        name = "myfield"
        dtype = "string"
        shape = ()
        value = {}

        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 


            if attrs[k][2] == "string":
                mlen = [1,self.__rnd.randint(1, 3)]
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  ] 
            elif attrs[k][2] != "bool":
                mlen = [1,self.__rnd.randint(0, 3)]
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  ] 
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1))  ]
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false")  
                                     ]

            attrs[k][3] =  (mlen[0],)

        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],attrs[name][3])
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, attrs[name][3])
            self.assertEqual(el.chunk, None)
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        self.assertEqual(f.nchildren, len(attrs))
        for k in attrs:
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], attrs[k][0], 
                                            error = attrs[k][4] if len(attrs[k])> 4 else 0, 
                                            attrs = {}
                                            )
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], value[k],
                                            error = attrs[k][4] if len(attrs[k])> 4 else 0, 
                                            attrs = {}
                                            )
            
        f.close()




        os.remove(fname)





    ## constructor test
    # \brief It tests default settings
    def test_read_write_1d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
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
            }

        value = {}

        el = {} 
        quin = 0
        quot = 0
        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 


            if attrs[k][2] == "string":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(self.__rnd.randint(2, 10)) ] 
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(self.__rnd.randint(2, 10))] 
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1))  for c in range(self.__rnd.randint(2, 10))]
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false")  
                                      for c in range(self.__rnd.randint(2, 10)) ]
                    
            attrs[k][3] =  (len(attrs[k][0]),)


        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],attrs[name][3])
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, attrs[name][3])
            self.assertEqual(el.chunk, None)
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        self.assertEqual(f.nchildren, len(attrs))
        for k in attrs:
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], attrs[k][0], 
                                            error = attrs[k][4] if len(attrs[k])> 4 else 0, 
                                            attrs = {}
                                            )
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], value[k],
                                            error = attrs[k][4] if len(attrs[k])> 4 else 0, 
                                            attrs = {}
                                            )
            
        f.close()




        os.remove(fname)



    ## constructor test
    # \brief It tests default settings
    def test_read_write_2d_single(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
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
            }

        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 


            if attrs[k][2] == "string":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)   ] ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  ] ]
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1)) ]]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")  
                                      ]]
                    
            attrs[k][3] =  (1,1)





        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],attrs[name][3])
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, attrs[name][3])
            self.assertEqual(el.chunk, None)
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        for k in attrs:
            
            
            self._sc.checkSingleScalarField(f, k, 
                                            attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], attrs[k][0][0][0],
                                            attrs[k][4] if len(attrs[k])> 4 else 0, 
                                            attrs = {})
            self._sc.checkSingleScalarField(f, k, 
                                            attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], attrs[k][0][0][0],
                                            attrs[k][4] if len(attrs[k])> 4 else 0, 
                                            attrs = {})
            

        f.close()
        os.remove(fname)





    ## constructor test
    # \brief It tests default settings
    def test_read_write_2d_double(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
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
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-4],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            }



        value = {}

        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 


            if attrs[k][2] == "string":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(self.__rnd.randint(2, 10))  ] ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(self.__rnd.randint(2, 10)) ] ]
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1)) for c in range(self.__rnd.randint(2, 10)) ]]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")  
                                      for c in range(self.__rnd.randint(2, 10))  ]]
                    
            attrs[k][3] =  (1,len(attrs[k][0][0]))


        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],attrs[name][3])
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, attrs[name][3])
            self.assertEqual(el.chunk, None)
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][3][1]):
                
                self._sc.checkSingleScalarField(f, "%s_%s" % (k,i), 
                                                attrs[k][2] if attrs[k][2] else 'string', 
                                                attrs[k][1], attrs[k][0][0][i],
                                                attrs[k][4] if len(attrs[k])> 4 else 0, 
                                                attrs = {})

                self._sc.checkSingleScalarField(f, "%s_%s" % (k,i), 
                                                attrs[k][2] if attrs[k][2] else 'string', 
                                                attrs[k][1], value[k][0][i],
                                                attrs[k][4] if len(attrs[k])> 4 else 0, 
                                                attrs = {})
                
                    

        f.close()
        os.remove(fname)






    ## constructor test
    # \brief It tests default settings
    def test_read_write_2d_double_2(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
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
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-4],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            }



        value = {}
        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 


            if attrs[k][2] == "string":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)]  for c in range(self.__rnd.randint(2, 10))   ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)]  for c in range(self.__rnd.randint(2, 10))  ]
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))] for c in range(self.__rnd.randint(2, 10)) ]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")  ]
                                      for c in range(self.__rnd.randint(2, 10))  ]
                    
            attrs[k][3] =  (len(attrs[k][0]),1)


        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],attrs[name][3])
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, attrs[name][3])
            self.assertEqual(el.chunk, None)
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            self._sc.checkSingleSpectrumField(f, k,
                                              attrs[k][2] if attrs[k][2] else 'string', 
                                              attrs[k][1], sum(attrs[k][0], []),
                                              attrs[k][4] if len(attrs[k])> 4 else 0, 
                                              attrs = {})
            
            self._sc.checkSingleSpectrumField(f, k, 
                                              attrs[k][2] if attrs[k][2] else 'string', 
                                              attrs[k][1], value[k],
                                              attrs[k][4] if len(attrs[k])> 4 else 0, 
                                              attrs = {})
                
                    

        f.close()
        os.remove(fname)




    ## constructor test
    # \brief It tests default settings
    def test_read_write_2d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True)

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
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
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-4],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            }



        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 10)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(self.__rnd.randint(2, 10))  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 10))]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 10))] 
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 10))]
                    
            attrs[k][3] =  (len(attrs[k][0]),len(attrs[k][0][0]))





        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],attrs[name][3])
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, attrs[name][3])
            self.assertEqual(el.chunk, None)
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][3][1]):
                
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], zip(*attrs[k][0])[i],
                                                  attrs[k][4] if len(attrs[k])> 4 else 0, 
                                                  attrs = {})
                
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1],  zip(*value[k])[i],
                                                  attrs[k][4] if len(attrs[k])> 4 else 0, 
                                                  attrs = {})
                
                    

        f.close()
        os.remove(fname)



if __name__ == '__main__':
    unittest.main()
