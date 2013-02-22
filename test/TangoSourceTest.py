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
## \file TangoSourceTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import numpy
from xml.dom import minidom
import PyTango 
import binascii
import time



import SimpleServerSetUp


#import pni.io.nx.h5 as nx

from ndts.DataSources import DataSource
from ndts.DataSources import TangoSource
from ndts.DecoderPool import DecoderPool
from ndts.Errors import DataSourceSetupError

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class TangoSourceTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()


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

        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            self.__seed  = long(time.time() * 256) # use fractional seconds
         
        self.__rnd = random.Random(self.__seed)





    ## test starter
    # \brief Common set up
    def setUp(self):
        self._simps.setUp()
        ## file handle

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        self._simps.tearDown()

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


        ds = TangoSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.name, None)
        self.assertEqual(ds.device, None)
        self.assertEqual(ds.memberType, None)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.encoding, None)


    ## __str__ test
    # \brief It tests default settings
    def test_str_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        dname = 'writer'
        device = 'p09/tdw/r228'
        mtype = 'attribute'
        ds = TangoSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), " Tango Device %s : %s (%s)" % (None, None, None))

        ds.device = device
        ds.name = None
        ds.memberType = None
        self.assertEqual(ds.__str__(), " Tango Device %s : %s (%s)" % (device, None, None))

        ds.device = None
        ds.name = dname
        ds.memberType = None
        self.assertEqual(ds.__str__(), " Tango Device %s : %s (%s)" % (None, dname, None))

        ds.device = None
        ds.name = None
        ds.memberType = mtype
        self.assertEqual(ds.__str__(), " Tango Device %s : %s (%s)" % (None, None, mtype))

        ds.device = device
        ds.name = dname
        ds.memberType = mtype
        self.assertEqual(ds.__str__(), " Tango Device %s : %s (%s)" % (device, dname, mtype))




    ## Data check 
    # \brief It check the source Data
    # \param data  tested data
    # \param format data format
    # \param value data value
    # \param ttype data Tango type    
    # \param shape data shape    
    # \param shape data shape    
    # \param encoding data encoding    
    # \param encoding data encoding    
    # \param decoders data decoders
    # \param error data error
    def checkData(self, data, format, value, ttype, shape, encoding = None, decoders = None, error = 0):
        self.assertEqual(data["format"], format)
        self.assertEqual(data["tangoDType"], ttype)
        self.assertEqual(data["shape"], shape)
        if encoding is not None:
            self.assertEqual(data["encoding"], encoding)
        if decoders is not None:
            self.assertEqual(data["decoders"], decoders)
        if format == 'SCALAR': 
                if error:
                    self.assertTrue(abs(data["value"]- value)<= error)
                else:
                    self.assertEqual(data["value"], value)
        elif format == 'SPECTRUM': 
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                if error:
                    self.assertTrue(abs(data["value"][i]- value[i])<= error)
                else:
                    self.assertEqual(data["value"][i], value[i])
        else:
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(len(data["value"][i]), len(value[i]))
                for j in range(len(value[i])):
                    if error:
                        self.assertTrue(abs(data["value"][i][j]-value[i][j])<=error)
                    else:
                        self.assertEqual(data["value"][i][j], value[i][j])
                

    ## setup test
    # \brief It tests default settings
    def test_setup_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        dname = 'writer'
        device = 'p09/tdw/r228'
        ctype = 'command'
        atype = 'attribute'
        host = 'haso.desy.de'
        port = '10000'
        encoding = 'UTF8'

        ds = TangoSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup,"<datasource/>")

        ds.device = None
        ds.name = None
        ds.memberType = None
        self.myAssertRaise(DataSourceSetupError, ds.setup,
                           "<datasource> <device name='%s'/> </datasource>" % device)

        ds.device = None
        ds.name = None
        ds.memberType = None
        self.myAssertRaise(DataSourceSetupError, ds.setup,
                           "<datasource> <record name='%s'/> </datasource>" % dname)

        ds.device = None
        ds.name = None
        ds.memberType = None
        self.myAssertRaise(DataSourceSetupError, ds.setup, "<datasource> <record/>  <device/> </datasource>")
        ds.device = None
        ds.name = None
        ds.memberType = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s'/> </datasource>" % (dname,device))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, atype)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.encoding, None)


        ds.device = None
        ds.name = None
        ds.memberType = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' member ='%s'/> </datasource>" % 
                 (dname,device,ctype))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, ctype)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.encoding, None)



        ds.device = None
        ds.name = None
        ds.memberType = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' member ='%s'/> </datasource>" % 
                 (dname,device,'strange'))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, atype)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.encoding, None)


        ds.device = None
        ds.name = None
        ds.memberType = None
        
        ds.setup("<datasource> <record name='%s'/> <device name='%s' hostname='%s'/> </datasource>" % 
                 (dname,device,host))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, atype)
        self.assertEqual(ds.hostname, host)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.encoding, None)



        ds.device = None
        ds.name = None
        ds.memberType = None
        ds.hostname = None
        ds.port = None
        
        ds.setup("<datasource> <record name='%s'/> <device name='%s' hostname='%s' port='%s'/> </datasource>" % 
                 (dname,device,host,port))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, atype)
        self.assertEqual(ds.hostname, host)
        self.assertEqual(ds.port, port)
        self.assertEqual(ds.encoding, None)


        ds.device = None
        ds.name = None
        ds.memberType = None
        ds.hostname = None
        ds.port = None
        ds.encoding = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' encoding='%s'/> </datasource>" % 
                 (dname,device,encoding))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, atype)
        self.assertEqual(ds.hostname, None)
        self.assertEqual(ds.port, None)
        self.assertEqual(ds.encoding, encoding)



    ## getData test
    # \brief It tests default settings
    def test_getData_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.getData(), None)

        el = TangoSource()
        el.device = 'stestp09/testss/s1r228'
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.getData(), None)


        el = TangoSource()
        el.device = 'stestp09/testss/s1r228'
        el.memberType = 'attribute'
        el.name = 'ScalarString'
        self.assertTrue(isinstance(el, object))
        dt = el.getData()
        self.checkData(dt,"SCALAR", "Hello!","DevString" ,[1,0],None,None)




    ## getData test
    # \brief It tests default settings
    def test_getData_scalar(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        arr1 = {
            "ScalarBoolean":[ "bool", "DevBoolean", True],
            "ScalarUChar":[ "uint8", "DevUChar", 23],
            "ScalarShort":[ "int16", "DevShort", -123],
            "ScalarUShort":[ "uint16", "DevUShort", 1234],
            "ScalarLong":[ self._bint, "DevLong", -124],
            "ScalarULong":[self._buint , "DevULong", 234],
            "ScalarLong64":[ "int64", "DevLong64", 234],
#            "ScalarULong64":[ "uint64", "DevULong64", 23],
            "ScalarFloat":[ "float32", "DevFloat", 12.234, 1e-5],
            "ScalarDouble":[ "float64", "DevDouble", -2.456673e+02,1e-14],
            "ScalarString":[ "string", "DevString", "MyTrue"],
            }



        arr2 = {
           "State":[ "string", "DevState", PyTango._PyTango.DevState.ON],
           }


        arr3 = {
           "ScalarEncoded":[ "string", "DevEncoded", ("UTF8","Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
           "SpectrumEncoded":[ "string", "DevEncoded", 
                               ('INT32', '\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
           }

        for k in arr1 :
            self._simps.dp.write_attribute( k, arr1[k][2])
            
        arr = dict(arr1,**(arr2))

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.memberType = 'attribute'
            el.name = k
            dt = el.getData()
            self.checkData(dt,"SCALAR", arr[k][2],arr[k][1],[1,0],None,None, arr[k][3] if len(arr[k])>3 else 0)

        for k in arr3:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.memberType = 'attribute'
            el.name = k
            el.encoding = arr3[k][2][0]
            dp = DecoderPool()
            dt = el.setDecoders(dp)
            dt = el.getData()
            self.checkData(dt,"SCALAR", arr3[k][2],arr3[k][1],[1,0],arr3[k][2][0],dp)






    ## getData test
    # \brief It tests default settings
    def test_getData_spectrum(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        
        arr = {
            "SpectrumBoolean":[ "bool", "DevBoolean", True, [1,0]],
            "SpectrumUChar":[ "uint8", "DevUChar", 23, [1,0]],
            "SpectrumShort":[ "int16", "DevShort", -123, [1,0]],
            "SpectrumUShort":[ "uint16", "DevUShort", 1234, [1,0]],
            "SpectrumLong":[ self._bint, "DevLong", -124, [1,0]],
            "SpectrumULong":[self._buint , "DevULong", 234, [1,0]],
            "SpectrumLong64":[ "int64", "DevLong64", 234, [1,0]],
            "SpectrumULong64":[ "uint64", "DevULong64", 23, [1,0]],
            "SpectrumFloat":[ "float32", "DevFloat", 12.234, [1,0], 1e-5],
            "SpectrumDouble":[ "float64", "DevDouble", -2.456673e+02, [1,0], 1e-14],
            "SpectrumString":[ "string", "DevString", "MyTrue", [1,0]],
            }




        for k in arr :

            if arr[k][1] != "DevBoolean":
                mlen = [self.__rnd.randint(1, 10),self.__rnd.randint(0, 3)]
                arr[k][2] =  [ arr[k][2]*self.__rnd.randint(0, 3) for c in range(mlen[0] )]
            else:    
                mlen = [self.__rnd.randint(1, 10)]
                arr[k][2] =  [ (True if self.__rnd.randint(0,1) else False)  for c in range(mlen[0]) ]

            arr[k][3] =  [mlen[0],0]
            self._simps.dp.write_attribute( k, arr[k][2])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.memberType = 'attribute'
            el.name = k
            dt = el.getData()
            self.checkData(dt,"SPECTRUM", arr[k][2],arr[k][1],arr[k][3],None,None, arr[k][4] if len(arr[k])>4 else 0)





    ## getData test
    # \brief It tests default settings
    def test_getData_image(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        
        arr = {
            "ImageBoolean":[ "bool", "DevBoolean", True, [1,0]],
            "ImageUChar":[ "uint8", "DevUChar", 23, [1,0]],
            "ImageShort":[ "int16", "DevShort", -123, [1,0]],
            "ImageUShort":[ "uint16", "DevUShort", 1234, [1,0]],
            "ImageLong":[ self._bint, "DevLong", -124, [1,0]],
            "ImageULong":[self._buint , "DevULong", 234, [1,0]],
            "ImageLong64":[ "int64", "DevLong64", 234, [1,0]],
            "ImageULong64":[ "uint64", "DevULong64", 23, [1,0]],
            "ImageFloat":[ "float32", "DevFloat", 12.234, [1,0], 1e-5],
            "ImageDouble":[ "float64", "DevDouble", -2.456673e+02, [1,0], 1e-14],
            "ImageString":[ "string", "DevString", "MyTrue", [1,0]],
            }




        for k in arr :


            mlen = [self.__rnd.randint(1, 10),self.__rnd.randint(1, 10), self.__rnd.randint(0,3)]
            if arr[k][1] != "DevBoolean":
                arr[k][2] =  [[ arr[k][2]*self.__rnd.randint(0,3) for r in range(mlen[1])] for c in range(mlen[0])]
            else:    
                mlen = [self.__rnd.randint(1, 10),self.__rnd.randint(1, 10) ]
                if arr[k][1] == 'DevBoolean':
                    arr[k][2] =  [[ (True if self.__rnd.randint(0,1) else False)  for c in range(mlen[1]) ] for r in range(mlen[0])]
                    
            arr[k][3] =  [mlen[0],mlen[1]]
            self._simps.dp.write_attribute( k, arr[k][2])


        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.memberType = 'attribute'
            el.name = k
            dt = el.getData()
            self.checkData(dt,"IMAGE", arr[k][2],arr[k][1],arr[k][3],None,None, arr[k][4] if len(arr[k])>4 else 0)



    ## getData test
    # \brief It tests default settings
    def test_getData_command(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        arr = {
            "GetBoolean":["ScalarBoolean", "bool", "DevBoolean", True],
#            "GetUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "GetShort":["ScalarShort", "int16", "DevShort", -123],
            "GetUShort":["ScalarUShort", "uint16", "DevUShort", 1234],
            "GetLong":["ScalarLong", self._bint, "DevLong", -124],
            "GetULong":["ScalarULong",self._buint , "DevULong", 234],
            "GetLong64":["ScalarLong64", "int64", "DevLong64", 234],
#            "GetULong64":["ScalarULong64", "uint64", "DevULong64", 23],
            "GetFloat":["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
            "GetDouble":["ScalarDouble", "float64", "DevDouble", -2.456673e+02,1e-14],
            "GetString":["ScalarString", "string", "DevString", "MyTrue"],
            }



        for k in arr :
            self._simps.dp.write_attribute(arr[k][0], arr[k][3])

        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.memberType = 'command'
            el.name = k
            dt = el.getData()
            self.checkData(dt,"SCALAR", arr[k][3],arr[k][2],[1,0],None,None, arr[k][4] if len(arr[k])>4 else 0)




    ## getData test
    # \brief It tests default settings
    def test_getData_dev_prop(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        arr = {
            "DeviceBoolean":["ScalarBoolean", "bool", "DevBoolean", True],
#            "DeviceUChar":["ScalarUChar", "uint8", "DevUChar", 23],
            "DeviceShort":["ScalarShort", "int16", "DevShort", -123],
            "DeviceUShort":["ScalarUShort", "uint16", "DevUShort", 1234],
            "DeviceLong":["ScalarLong", self._bint, "DevLong", -124],
            "DeviceULong":["ScalarULong",self._buint , "DevULong", 234],
#            "DeviceLong64":["ScalarLong64", "int64", "DevLong64", 234],
#            "DeviceULong64":["ScalarULong64", "uint64", "DevULong64", 23],
#            "DeviceFloat":["ScalarFloat", "float32", "DevFloat", 12.234, 1e-5],
#            "DeviceDouble":["ScalarDouble", "float64", "DevDouble", -2.456673e+02,1e-14],
            "DeviceFloat":["ScalarFloat", "float32", "DevFloat", 12.234],
            "DeviceDouble":["ScalarDouble", "float64", "DevDouble", -2.456673e+02],
            "DeviceString":["ScalarString", "string", "DevString", "MyTrue"],
            }




        for k in arr:
            el = TangoSource()
            el.device = 'stestp09/testss/s1r228'
            el.memberType = 'property'
            el.name = k
            dt = el.getData()
            self.checkData(dt,"SCALAR", str(self._simps.device_prop[k]),
                           'DevString',[1,0],None,None, arr[k][4] if len(arr[k])>4 else 0)
#            self.checkData(dt,"SCALAR", arr[k][3],arr[k][2],[1,0],None,None, arr[k][4] if len(arr[k])>4 else 0)






    ## isValid test
    # \brief It tests default settings
    def test_isValid(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.isValid(), True)


    
if __name__ == '__main__':
    unittest.main()
