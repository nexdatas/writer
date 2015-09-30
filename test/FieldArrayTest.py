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
import numpy

from nxswriter.FieldArray import FieldArray
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


    ## Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertURaise(self, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except :
            error = True
        self.assertEqual(error, True)


    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()


        attrs = {
            "string":["My string","NX_CHAR", "string"],
#            "string2":["My string","NX_CHAR", ""],
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
            value[name] = el.read()
            el.close()
#            self.myAssertRaise(nx.NXGroupError, el.write,attrs[name][0])
            self.myAssertURaise(el.write,attrs[name][0])
            
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64",(1,),1.e-14],
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
            el.close()
#            el.write(attrs[name][0])
#            self.myAssertRaise(nx.NXGroupError, el.write,attrs[name][0])
            self.myAssertURaise(el.write,attrs[name][0])
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64",(1,),1.e-14],
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
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(self.__rnd.randint(2, 6)) ] 
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(self.__rnd.randint(2, 6))] 
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1))  for c in range(self.__rnd.randint(2, 6))]
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false")  
                                      for c in range(self.__rnd.randint(2, 6)) ]
                    
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64",(1,),1.e-14],
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
            el.close()
#            self.myAssertRaise(nx.NXGroupError, el.write,attrs[name][0])
            self.myAssertURaise(el.write,attrs[name][0])
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64",(1,),1.e-14],
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
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(self.__rnd.randint(2, 6))  ] ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(self.__rnd.randint(2, 6)) ] ]
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1)) for c in range(self.__rnd.randint(2, 6)) ]]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")  
                                      for c in range(self.__rnd.randint(2, 6))  ]]
                    
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64",(1,),1.e-14],
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
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)]  for c in range(self.__rnd.randint(2, 6))   ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)]  for c in range(self.__rnd.randint(2, 6))  ]
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))] for c in range(self.__rnd.randint(2, 6)) ]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")  ]
                                      for c in range(self.__rnd.randint(2, 6))  ]
                    
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
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64",(1,),1.e-14],
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

            mlen = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(self.__rnd.randint(2, 6))  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 6))]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 6))] 
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 6))]
                    
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






    ## constructor test
    # \brief It tests default settings
    def test_read_write_3d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64",(1,),1.e-14],
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

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(mlen2)  ] for c3 in range(self.__rnd.randint(2, 6))  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(mlen2)] for c3 in range(self.__rnd.randint(2, 6))  ]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(mlen2)]  for c3 in range(self.__rnd.randint(2, 6))  ]
                else:
                    attrs[k][0] =  [[[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(mlen2)] for c3 in range(self.__rnd.randint(2, 6))  ]
                    
            attrs[k][3] =  (len(attrs[k][0]),len(attrs[k][0][0]),len(attrs[k][0][0][0]))





        
        for name in attrs:
            el = FieldArray(nxFile, name, attrs[name][2],attrs[name][3])
            self.assertEqual(el.name, name)
            self.assertEqual(el.dtype, attrs[name][2])
            self.assertEqual(el.shape, attrs[name][3])
            self.assertEqual(el.chunk, None)
#            print name ,attrs[name][0]
            el.write(attrs[name][0])
#            print name ,attrs[name][0], "read", el.read()
            value[name] = el.read()
            el.close()
#            self.myAssertRaise(nx.NXGroupError, el.write,attrs[name][0])
            self.myAssertURaise(el.write,attrs[name][0])
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][3][1]):
                for j in range(attrs[k][3][2]):
                    res = map(lambda *image: map(lambda *row: list(row), *image), *attrs[k][0])
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res[i][j],
                                                      attrs[k][4] if len(attrs[k])> 4 else 0, 
                                                      attrs = {})
                    res = map(lambda *image: map(lambda *row: list(row), *image), *value[k])
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res[i][j],
                                                      attrs[k][4] if len(attrs[k])> 4 else 0, 
                                                      attrs = {})
                
                    

        f.close()
        os.remove(fname)





    ## constructor test
    # \brief It tests default settings
    def test_get_set_1d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
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
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(self.__rnd.randint(2, 6)) ] 
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(self.__rnd.randint(2, 6))] 
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1))  for c in range(self.__rnd.randint(2, 6))]
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false")  
                                      for c in range(self.__rnd.randint(2, 6)) ]
                    
            attrs[k][3] =  (len(attrs[k][0]),)
            nr = self.__rnd.randint(1, 6)
            attrs[k][4] =  (len(attrs[k][0])+nr,)
            attrs[k][5] =  (self.__rnd.randint(0, nr),)


        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            el.write([attrs[k][0][0]]*attrs[k][4][0])
            el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]] = attrs[k][0]
            value[k] = el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        self.assertEqual(f.nchildren, len(attrs))
        
        for k in attrs:
            res = [attrs[k][0][0]]*attrs[k][4][0] 
            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]] = attrs[k][0]
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], res, 
                                            error = attrs[k][6] if len(attrs[k])> 6 else 0, 
                                            attrs = {}
                                            )
            res = [attrs[k][0][0]]*attrs[k][4][0] 
            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]] = value[k]
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], res,
                                            error = attrs[k][6] if len(attrs[k])> 6 else 0, 
                                            attrs = {}
                                            )
            
        f.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_get_set_1d_single(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
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
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  ] 
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3) ] 
            else:    
                mlen = [1]
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1)) ]
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false")  
                                       ]
                    
            attrs[k][3] =  (len(attrs[k][0]),)
            nr = self.__rnd.randint(1, 6)
            attrs[k][4] =  (len(attrs[k][0])+nr,)
            attrs[k][5] =  (self.__rnd.randint(0, nr),)


        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            el.write([attrs[k][0][0]]*attrs[k][4][0])
            el[attrs[k][5][0]] = attrs[k][0]
            value[k] = el[attrs[k][5][0]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        self.assertEqual(f.nchildren, len(attrs))
        
        for k in attrs:
            res = [attrs[k][0][0]]*attrs[k][4][0] 
            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]] = attrs[k][0]
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], res, 
                                            error = attrs[k][6] if len(attrs[k])> 6 else 0, 
                                           attrs = {}
                                            )
            res = [attrs[k][0][0]]*attrs[k][4][0] 
            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]] = value[k]
            self._sc.checkSingleSpectrumField(f, k, attrs[k][2] if attrs[k][2] else 'string', 
                                            attrs[k][1], res,
                                            error = attrs[k][6] if len(attrs[k])> 6 else 0, 
                                            attrs = {}
                                            )
            
        f.close()




        os.remove(fname)





    ## constructor test
    # \brief It tests default settings
    def test_get_set_2d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()


        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }



        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(self.__rnd.randint(2, 6))  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 6))]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 6))] 
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(self.__rnd.randint(2, 6))]
                    
            attrs[k][3] =  (len(attrs[k][0]),len(attrs[k][0][0]))
            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6))
            attrs[k][4] =  (len(attrs[k][0])+nr[0],len(attrs[k][0][0])+nr[1])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]))




        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            el.write([[attrs[k][0][0][0]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
               attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][1]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
                           attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][1]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                res = [attrs[k][0][0][0]]*attrs[k][4][0]
                if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][1]:
                    res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]= zip(*attrs[k][0])[i-attrs[k][5][1]] 
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                res = [attrs[k][0][0][0]]*attrs[k][4][0]
                if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][1]:
                    res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]= zip(*value[k])[i-attrs[k][5][1]] 
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                
                    

        f.close()
        os.remove(fname)



    ## constructor test
    # \brief It tests default settings
    def test_get_set_2d_first(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()


        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }



        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c2 in range(self.__rnd.randint(2, 6))  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c2 in range(self.__rnd.randint(2, 6))]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1)) for c2 in range(self.__rnd.randint(2, 6))] 
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false") for c2 in range(self.__rnd.randint(2, 6))]
                    
            attrs[k][3] =  (len(attrs[k][0]),)
            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6))
            attrs[k][4] =  (len(attrs[k][0])+nr[0], 1+nr[1])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]))




        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            el.write([[attrs[k][0][0]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
               attrs[k][5][1]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
                           attrs[k][5][1]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                res = [attrs[k][0][0]]*attrs[k][4][0]
                if i == attrs[k][5][1]:
                    res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]= attrs[k][0]
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                if i == attrs[k][5][1]:
                    res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]= value[k]
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                
                    

        f.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_get_set_2d_second(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()


        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }



        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c2 in range(self.__rnd.randint(2, 6))  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c2 in range(self.__rnd.randint(2, 6))]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1)) for c2 in range(self.__rnd.randint(2, 6))] 
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false") for c2 in range(self.__rnd.randint(2, 6))]
                    
            attrs[k][3] =  (len(attrs[k][0]),)
            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6))
            attrs[k][4] =  (1+nr[0], len(attrs[k][0])+nr[1])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]))




        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            el.write([[attrs[k][0][0]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0], attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][0]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0], attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][0]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                res = [attrs[k][0][0]]*attrs[k][4][0]
                if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][0]:
                    res[attrs[k][5][0]] = attrs[k][0][i-attrs[k][5][1]] 
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                res = [attrs[k][0][0]]*attrs[k][4][0]
                if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][0]:
                    res[attrs[k][5][0]] = value[k][0][i-attrs[k][5][1]] 
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                
                
                    

        f.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_get_set_2d_scalar(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()


        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }



        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

                    
            attrs[k][3] =  ()
            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6))
            attrs[k][4] =  (1+nr[0], 1+nr[1])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]))




        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            el.write([[attrs[k][0]*0]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0], attrs[k][5][1]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0], attrs[k][5][1]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                res = [attrs[k][0]*0]*attrs[k][4][0]
                if i == attrs[k][5][1]:
                    res[attrs[k][5][0]] = attrs[k][0]
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                res = [attrs[k][0]*0]*attrs[k][4][0]
                if i == attrs[k][5][1]:
                    res[attrs[k][5][0]] = value[k][0][0]
                self._sc.checkSingleSpectrumField(f, "%s_%s" % (k,i), 
                                                  attrs[k][2] if attrs[k][2] else 'string', 
                                                  attrs[k][1], res,
                                                  attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                  attrs = {})
                
                
                
                    

        f.close()
        os.remove(fname)



    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(mlen2)  ] for c3 in range(self.__rnd.randint(2, 6))  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(mlen2)] for c3 in range(self.__rnd.randint(2, 6))  ]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(mlen2)]  for c3 in range(self.__rnd.randint(2, 6))  ]
                else:
                    attrs[k][0] =  [[[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(mlen2)] for c3 in range(self.__rnd.randint(2, 6))  ]
                    
            attrs[k][3] =  (len(attrs[k][0]),len(attrs[k][0][0]),len(attrs[k][0][0][0]))

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1, 6))
            attrs[k][4] =  (len(attrs[k][0])+nr[0],len(attrs[k][0][0])+nr[1],len(attrs[k][0][0][0])+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))




        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0][0][0][0]]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
               attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][1],
               attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][2]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
               attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][1],
               attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][2]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0][0][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][1]:
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][2]:
                            res2 = map(lambda *image: map(lambda *row: list(row), *image), *attrs[k][0])
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = res2[i-attrs[k][5][1]][j-attrs[k][5][2]] 


                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                    res = [attrs[k][0][0][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][1]:
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][2]:
                            res2 = map(lambda *image: map(lambda *row: list(row), *image), *value[k])
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = res2[i-attrs[k][5][1]][j-attrs[k][5][2]] 
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                
                    

        f.close()
        os.remove(fname)




    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d_double_first(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(mlen2)  ] 
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(mlen2)] 
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(mlen2)]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(mlen2)] 
                    
            attrs[k][3] =  (len(attrs[k][0]),len(attrs[k][0][0]))

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1,6))
            attrs[k][4] =  (len(attrs[k][0])+nr[0],len(attrs[k][0][0])+nr[1],1+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))



        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0][0][0]]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
               attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][1],
               attrs[k][5][2]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
               attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][1],
               attrs[k][5][2]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][1]:
                        if j == attrs[k][5][2]:
                            res = [attrs[k][0][0][0]]*attrs[k][4][0]
                            res2 = map(lambda *row: list(row), *attrs[k][0])
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = res2[i-attrs[k][5][1]]


                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                    res = [attrs[k][0][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][1]:
                        if j == attrs[k][5][2]:
                            res = [attrs[k][0][0][0]]*attrs[k][4][0]
                            res2 = map(lambda *row: list(row), *value[k])
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = res2[i-attrs[k][5][1]]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                
                    

        f.close()
        os.remove(fname)





    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d_double_second(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(mlen2)  ] 
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(mlen2)] 
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(mlen2)]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(mlen2)] 
                    
            attrs[k][3] =  (len(attrs[k][0]),len(attrs[k][0][0]))

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1,6))
            attrs[k][4] =  (len(attrs[k][0])+nr[0],1+nr[1],len(attrs[k][0][0])+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))



        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0][0][0]]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
               attrs[k][5][1],
               attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][1]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],
                           attrs[k][5][1],
                           attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][1]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0][0][0]]*attrs[k][4][0]
                    if i  == attrs[k][5][1] :
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][1]:
                            res2 = map(lambda *row: list(row), *attrs[k][0])
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = res2[j-attrs[k][5][2]]

                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                    res = [attrs[k][0][0][0]]*attrs[k][4][0]
                    if i  == attrs[k][5][1] :
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][1]:
                            res2 = map(lambda *image: map(lambda *row: list(row), *image), *value[k])
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = res2[0][j-attrs[k][5][2]]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                
                    

        f.close()
        os.remove(fname)



    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d_double_third(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ] for c2 in range(mlen2)  ] 
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [[ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] for c2 in range(mlen2)] 
            else:    
                if k == 'bool':
                    attrs[k][0] =  [[ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] for c2 in range(mlen2)]
                else:
                    attrs[k][0] =  [[ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ] for c2 in range(mlen2)] 
                    
            attrs[k][3] =  (len(attrs[k][0]),len(attrs[k][0][0]))

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1,6))
            attrs[k][4] =  (1+nr[0],len(attrs[k][0])+nr[1],len(attrs[k][0][0])+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))



        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0][0][0]]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0],
               attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][0],
               attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][1]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0],
                           attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][0],
                           attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][1]]
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][0]:
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][1]:
                            res[attrs[k][5][0]]  = attrs[k][0][i-attrs[k][5][1]][j-attrs[k][5][2]]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})


                    res = [attrs[k][0][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][0]:
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][1]:
                            res2 = value[k][0]
                            res[attrs[k][5][0]]  = res2[i-attrs[k][5][1]][j-attrs[k][5][2]]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                
                    

        f.close()
        os.remove(fname)



    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d_single_first(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ] 
            else:    
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] 
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false") for c in range(mlen) ]
                    
            attrs[k][3] =  (len(attrs[k][0]),)

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1,6))
            attrs[k][4] =  (len(attrs[k][0])+nr[0],1+nr[1],1+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))



        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0][0]]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0],attrs[k][5][1],attrs[k][5][2]] = attrs[k][0]
            value[k] =  el[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0], attrs[k][5][1], attrs[k][5][2]]

        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0][0]]*attrs[k][4][0]
                    if i == attrs[k][5][1]:
                        if j == attrs[k][5][2]:
                            res = [attrs[k][0][0]]*attrs[k][4][0]
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = attrs[k][0]


                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                    res = [attrs[k][0][0]]*attrs[k][4][0]
                    if i == attrs[k][5][1]:
                        if j == attrs[k][5][2]:
                            res = [attrs[k][0][0]]*attrs[k][4][0]
                            res[attrs[k][5][0]:attrs[k][5][0]+attrs[k][3][0]]  = value[k]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})

        f.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d_single_second(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1))  for c in range(mlen) ]
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ]
                    
            attrs[k][3] =  (len(attrs[k][0]),)

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1,6))
            attrs[k][4] =  (1+nr[0],len(attrs[k][0])+nr[1],1+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))



        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0][0]]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0],
               attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][0],
               attrs[k][5][2]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0],
                           attrs[k][5][1]:attrs[k][5][1]+attrs[k][3][0],
                           attrs[k][5][2]]
            
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][0]:
                        if j == attrs[k][5][2]:
                            res[attrs[k][5][0]]  = attrs[k][0][i-attrs[k][5][1]]


                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})

                    res = [attrs[k][0][0]]*attrs[k][4][0]
                    if i>= attrs[k][5][1] and i < attrs[k][5][1]+attrs[k][3][0]:
                        if j == attrs[k][5][2]:
                            res[attrs[k][5][0]]  = value[k][0][i-attrs[k][5][1]]


                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})

                    

        f.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d_single_third(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            if attrs[k][2] == "string":
                
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(1, 3)  for c in range(mlen)  ]
            elif attrs[k][2] != "bool":
                attrs[k][0] =  [ attrs[k][0]*self.__rnd.randint(0, 3)  for c in range(mlen) ]
            else:    
                if k == 'bool':
                    attrs[k][0] =  [ bool(self.__rnd.randint(0,1))  for c in range(mlen) ] 
                else:
                    attrs[k][0] =  [ ("true" if self.__rnd.randint(0,1) else "false")   for c in range(mlen) ]
                    
            attrs[k][3] =  (len(attrs[k][0]),)

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1,6))
            attrs[k][4] =  (1+nr[0],1+nr[1],len(attrs[k][0])+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))



        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0][0]]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0],
               attrs[k][5][1],
               attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][0]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0],
                           attrs[k][5][1],
                           attrs[k][5][2]:attrs[k][5][2]+attrs[k][3][0]]
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0][0]]*attrs[k][4][0]
                    if i== attrs[k][5][1]:
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][0]:
                            res[attrs[k][5][0]]  = attrs[k][0][j-attrs[k][5][2]]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})


                    res = [attrs[k][0][0]]*attrs[k][4][0]
                    if i== attrs[k][5][1]:
                        if j>= attrs[k][5][2] and j < attrs[k][5][2]+attrs[k][3][0]:
                            res[attrs[k][5][0]]  = value[k][0][0][j-attrs[k][5][2]]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                
                    

        f.close()
        os.remove(fname)

    ## constructor test
    # \brief It tests default settings
    def test_get_set_3d_scalar(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        value = {}
        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),(1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,), (1,)],
            }
        value = {}


        el = {} 
        quin = 0
        quot = 0

        for k in attrs: 
            quot = (quot + 1) %4
            grow = quot-1  if quot else  None
            quin = (quin+1) % 5 

            mlen = self.__rnd.randint(2, 6)
            mlen2 = self.__rnd.randint(2, 6)
            attrs[k][3] =  ()

            nr = (self.__rnd.randint(1, 6),self.__rnd.randint(1, 6),self.__rnd.randint(1,6))
            attrs[k][4] =  (1+nr[0],1+nr[1],1+nr[2])
            attrs[k][5] =  (self.__rnd.randint(0, nr[0]),self.__rnd.randint(0, nr[1]),self.__rnd.randint(0, nr[2]))



        
        for k in attrs:
            el = FieldArray(nxFile, k, attrs[k][2],attrs[k][4])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][4])
            self.assertEqual(el.chunk, None)
            value[k] = el.read()
            
            el.write([[[attrs[k][0]*0]*attrs[k][4][2]]*attrs[k][4][1]]*attrs[k][4][0])
            el[attrs[k][5][0],
               attrs[k][5][1],
               attrs[k][5][2]]= attrs[k][0]
            value[k] =  el[attrs[k][5][0],
                           attrs[k][5][1],
                           attrs[k][5][2]]
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            for i in range(attrs[k][4][1]):
                for j in range(attrs[k][4][2]):
                    res = [attrs[k][0]*0]*attrs[k][4][0]
                    if i== attrs[k][5][1]:
                        if j == attrs[k][5][2]:
                            res[attrs[k][5][0]]  = attrs[k][0]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})


                    res = [attrs[k][0]*0]*attrs[k][4][0]
                    if i== attrs[k][5][1]:
                        if j == attrs[k][5][2]:
                            res[attrs[k][5][0]]  = value[k][0][0][0]
                    self._sc.checkSingleSpectrumField(f, "%s_%s_%s" % (k,i,j), 
                                                      attrs[k][2] if attrs[k][2] else 'string', 
                                                      attrs[k][1], res,
                                                      attrs[k][6] if len(attrs[k])> 6 else 0, 
                                                      attrs = {})
                
                    

        f.close()
        os.remove(fname)





    ## constructor test
    # \brief It tests default settings
    def test_attr_1d(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,)],
            "int":[-123,"NX_INT", "int64", (1,)],
            "int8":[12,"NX_INT8", "int8", (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,)],
            }



        
        for k in attrs:
            print k
            slen = self.__rnd.randint(0, 3)
            attrs[k][3] = tuple([self.__rnd.randint(2, 6) for s in range(slen)])
            

            el = FieldArray(nxFile, k, "string",attrs[k][3])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, "string")
            self.assertEqual(el.shape, attrs[k][3])
            self.assertEqual(el.chunk, None)
            el.attr(k,attrs[k][2]).value= attrs[k][0]
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            if len(attrs[k][3]) <= 1:
                fl = f.open(k)
                at = fl.attr(k)
                self.assertTrue(isinstance(at,nx.nxh5.NXAttribute))
                self.assertTrue(at.valid)
                self.assertTrue(hasattr(at.shape,"__iter__"))
                self.assertEqual(len(at.shape),0)
                self.assertEqual(at.dtype,attrs[k][2])
                self.assertEqual(at.name,k)
                if len(attrs[k]) > 4 :
                    self.assertTrue(abs(at.value-attrs[k][0])<= attrs[k][4])
                else:
                    self.assertEqual(at.value,attrs[k][0])
            elif len(attrs[k][3]) == 2:
                for i in range(attrs[k][3][1]):
                    fl = f.open("%s_%s" %(k,i))
                    at = fl.attr(k)
                    self.assertTrue(isinstance(at,nx.nxh5.NXAttribute))
                    self.assertTrue(at.valid)
                    self.assertTrue(hasattr(at.shape,"__iter__"))
                    self.assertEqual(len(at.shape),0)
                    self.assertEqual(at.dtype,attrs[k][2])
                    self.assertEqual(at.name,k)
                    if len(attrs[k]) > 4 :
                        self.assertTrue(abs(at.value-attrs[k][0])<= attrs[k][4])
                    else:
                        self.assertEqual(at.value,attrs[k][0])
                        
            elif len(attrs[k][3]) == 3:
                for i in range(attrs[k][3][1]):
                    for j in range(attrs[k][3][2]):
                        fl = f.open("%s_%s_%s" %(k,i,j))
                        at = fl.attr(k)
                        self.assertTrue(isinstance(at,nx.nxh5.NXAttribute))
                        self.assertTrue(at.valid)
                        self.assertTrue(hasattr(at.shape,"__iter__"))
                        self.assertEqual(len(at.shape),0)
                        self.assertEqual(at.dtype,attrs[k][2])
                        self.assertEqual(at.name,k)
                        if len(attrs[k]) > 4 :
                            self.assertTrue(abs(at.value-attrs[k][0])<= attrs[k][4])
                        else:
                            self.assertEqual(at.value,attrs[k][0])
            
        f.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_grow(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,)],
            }



        
        for k in attrs:
            slen = self.__rnd.randint(0, 3)
            attrs[k][3] = tuple([self.__rnd.randint(2, 6) for s in range(slen)])
            dim, val = (self.__rnd.randint(0, max(0,slen-1)),self.__rnd.randint(0, 6))
            attrs[k][4] = list(attrs[k][3])
            if slen:
                attrs[k][4][dim] = attrs[k][3][dim] + val
                attrs[k][4] = tuple(attrs[k][4])
            else:
                attrs[k][4] = (1+val,)

            el = FieldArray(nxFile, k, attrs[k][2], attrs[k][3])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][3])
            self.assertEqual(el.chunk, None)
            if dim ==0 :
                self.assertEqual(el.grow(dim,val), None)
            else:
                self.myAssertRaise(ValueError,el.grow,dim,val)
                attrs[k][4] = attrs[k][3]
            self.assertEqual(el.shape, attrs[k][4])
            
            
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            if len(attrs[k][4]) <= 1:
                fl = f.open(k)
                self.assertEqual(fl.shape, attrs[k][4])
            elif len(attrs[k][4]) == 2:
                for i in range(attrs[k][4][1]):
                    fl = f.open("%s_%s" %(k,i))
                    self.assertEqual(fl.shape, (attrs[k][4][0],))
                        
            elif len(attrs[k][4]) == 3:
                for i in range(attrs[k][4][1]):
                    for j in range(attrs[k][4][2]):
                        fl = f.open("%s_%s_%s" %(k,i,j))
                        self.assertEqual(fl.shape, (attrs[k][4][0],))
            
        f.close()
        os.remove(fname)

    ## constructor test
    # \brief It tests default settings
    def test_grow_dim0(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,)],
            }



        
        for k in attrs:
            slen = self.__rnd.randint(0, 3)
            attrs[k][3] = tuple([self.__rnd.randint(2, 6) for s in range(slen)])
            dim, val = (0,self.__rnd.randint(0, 6))
            attrs[k][4] = list(attrs[k][3])
            if slen:
                attrs[k][4][dim] = attrs[k][3][dim] + val
                attrs[k][4] = tuple(attrs[k][4])
            else:
                attrs[k][4] = (1+val,)

            el = FieldArray(nxFile, k, attrs[k][2], attrs[k][3])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][3])
            self.assertEqual(el.chunk, None)
            if dim ==0 :
                self.assertEqual(el.grow(dim,val), None)
            else:
                self.myAssertRaise(ValueError,el.grow,dim,val)
                attrs[k][4] = attrs[k][3]
            self.assertEqual(el.shape, attrs[k][4])
            
            
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            if len(attrs[k][4]) <= 1:
                fl = f.open(k)
                self.assertEqual(fl.shape, attrs[k][4])
            elif len(attrs[k][4]) == 2:
                for i in range(attrs[k][4][1]):
                    fl = f.open("%s_%s" %(k,i))
                    self.assertEqual(fl.shape, (attrs[k][4][0],))
                        
            elif len(attrs[k][4]) == 3:
                for i in range(attrs[k][4][1]):
                    for j in range(attrs[k][4][2]):
                        fl = f.open("%s_%s_%s" %(k,i,j))
                        self.assertEqual(fl.shape, (attrs[k][4][0],))
            
        f.close()
        os.remove(fname)



    ## constructor test
    # \brief It tests default settings
    def test_grow_val1(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,)],
            }



        
        for k in attrs:
            slen = self.__rnd.randint(0, 3)
            attrs[k][3] = tuple([self.__rnd.randint(2, 6) for s in range(slen)])
            dim, val = (0,1)
            attrs[k][4] = list(attrs[k][3])
            if slen:
                attrs[k][4][dim] = attrs[k][3][dim] + val
                attrs[k][4] = tuple(attrs[k][4])
            else:
                attrs[k][4] = (1+val,)

            el = FieldArray(nxFile, k, attrs[k][2], attrs[k][3])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][3])
            self.assertEqual(el.chunk, None)
            if dim ==0 :
                self.assertEqual(el.grow(dim), None)
            else:
                self.myAssertRaise(ValueError,el.grow,dim,val)
                attrs[k][4] = attrs[k][3]
            self.assertEqual(el.shape, attrs[k][4])
            
            
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            if len(attrs[k][4]) <= 1:
                fl = f.open(k)
                self.assertEqual(fl.shape, attrs[k][4])
            elif len(attrs[k][4]) == 2:
                for i in range(attrs[k][4][1]):
                    fl = f.open("%s_%s" %(k,i))
                    self.assertEqual(fl.shape, (attrs[k][4][0],))
                        
            elif len(attrs[k][4]) == 3:
                for i in range(attrs[k][4][1]):
                    for j in range(attrs[k][4][2]):
                        fl = f.open("%s_%s_%s" %(k,i,j))
                        self.assertEqual(fl.shape, (attrs[k][4][0],))
            
        f.close()
        os.remove(fname)


    ## constructor test
    # \brief It tests default settings
    def test_grow_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
        ## file handle
        nxFile = nx.create_file(fname, overwrite=True).root()

        attrs = {
            "string":["Mystring","NX_CHAR", "string" , (1,), (1,)],
            "datetime":["12:34:34","NX_DATE_TIME", "string", (1,), (1,) ],
            "iso8601":["12:34:34","ISO8601", "string", (1,), (1,)],
            "int":[-123,"NX_INT", "int64", (1,), (1,)],
            "int8":[12,"NX_INT8", "int8", (1,), (1,)],
            "int16":[-123,"NX_INT16", "int16", (1,), (1,)],
            "int32":[12345,"NX_INT32", "int32", (1,), (1,)],
            "int64":[-12345,"NX_INT64", "int64", (1,), (1,)],
            "uint":[123,"NX_UINT", "uint64", (1,), (1,)],
            "uint8":[12,"NX_UINT8", "uint8", (1,), (1,)],
            "uint16":[123,"NX_UINT16", "uint16", (1,), (1,)],
            "uint32":[12345,"NX_UINT32", "uint32", (1,), (1,)],
            "uint64":[12345,"NX_UINT64", "uint64", (1,), (1,)],
            "float":[-12.345,"NX_FLOAT", "float64", (1,), (1,),1.e-14],
            "number":[-12.345e+2,"NX_NUMBER",  "float64", (1,), (1,),1.e-14],
            "float32":[-12.345e-1,"NX_FLOAT32", "float32", (1,), (1,), 1.e-5],
            "float64":[-12.345,"NX_FLOAT64", "float64", (1,), (1,), 1.e-14],
            "bool":[True,"NX_BOOLEAN", "bool", (1,), (1,)],
            }



        
        for k in attrs:
            slen = self.__rnd.randint(0, 3)
            attrs[k][3] = tuple([self.__rnd.randint(2, 6) for s in range(slen)])
            dim, val = (0,1)
            attrs[k][4] = list(attrs[k][3])
            if slen:
                attrs[k][4][dim] = attrs[k][3][dim] + val
                attrs[k][4] = tuple(attrs[k][4])
            else:
                attrs[k][4] = (1+val,)

            el = FieldArray(nxFile, k, attrs[k][2], attrs[k][3])
            self.assertEqual(el.name, k)
            self.assertEqual(el.dtype, attrs[k][2])
            self.assertEqual(el.shape, attrs[k][3])
            self.assertEqual(el.chunk, None)
            if dim ==0 :
                self.assertEqual(el.grow(), None)
            else:
                self.myAssertRaise(ValueError,el.grow,dim,val)
                attrs[k][4] = attrs[k][3]
            self.assertEqual(el.shape, attrs[k][4])
            
            
        nxFile.close()
    
        f = nx.open_file(fname,readonly=True)
        self.assertEqual(6, f.nattrs)
        self.assertEqual( f.attr("file_name").value, fname)
        self.assertTrue(f.attr("NX_class").value,"NXroot")
        
        for k in attrs:
            if len(attrs[k][4]) <= 1:
                fl = f.open(k)
                self.assertEqual(fl.shape, attrs[k][4])
            elif len(attrs[k][4]) == 2:
                for i in range(attrs[k][4][1]):
                    fl = f.open("%s_%s" %(k,i))
                    self.assertEqual(fl.shape, (attrs[k][4][0],))
                        
            elif len(attrs[k][4]) == 3:
                for i in range(attrs[k][4][1]):
                    for j in range(attrs[k][4][2]):
                        fl = f.open("%s_%s_%s" %(k,i,j))
                        self.assertEqual(fl.shape, (attrs[k][4][0],))
            
        f.close()
        os.remove(fname)

if __name__ == '__main__':
    unittest.main()
