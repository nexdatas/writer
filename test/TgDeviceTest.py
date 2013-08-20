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
import json
import PyTango

import SimpleServerSetUp


from ndts.DataSources import DataSource
from ndts.DataSources import TangoSource
from ndts.DataSources import TgMember
from ndts.DataSources import TgGroup
from ndts.DataSources import TgDevice
from ndts.DecoderPool import DecoderPool
from ndts.Element import Element
from ndts.H5Elements import EField
from ndts.DataSourceFactory import DataSourceFactory
from ndts.Errors import DataSourceSetupError
from ndts.DataSourcePool import DataSourcePool
from ndts import DataSources

import threading
import thread

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test pool
class pool(object):

    def __init__(self):
        self.common = {}
        self.lock = threading.Lock()
        self.counter = 0
    
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
        ## file handle
        print "SEED =",self.__seed 

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        pass

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


        name ="myname%s"% self.__rnd.randint(0, 9)
        proxy = "proxy%s"% self.__rnd.randint(0, 9)

        dv = TgDevice(name)
        self.assertEqual(dv.device, name)
        self.assertEqual(dv.members, {})
        self.assertEqual(dv.attributes, [])
        self.assertEqual(dv.properties, [])
        self.assertEqual(dv.commands, [])
        self.assertEqual(dv.proxy, None)

        dv = TgDevice(name,proxy)
        self.assertEqual(dv.device, name)
        self.assertEqual(dv.members, {})
        self.assertEqual(dv.attributes, [])
        self.assertEqual(dv.properties, [])
        self.assertEqual(dv.commands, [])
        self.assertEqual(dv.proxy, proxy)


    ## constructor test
    # \brief It tests default settings
    def test_setMember(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        device ="device/%s"% self.__rnd.randint(0, 9)
        proxy = "proxy%s"% self.__rnd.randint(0, 9)

        dv = TgDevice(device)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {})
        self.assertEqual(dv.attributes, [])
        self.assertEqual(dv.properties, [])
        self.assertEqual(dv.commands, [])
        self.assertEqual(dv.proxy, None)


        name1 ="myname%s"% self.__rnd.randint(0, 9)
        mb1 = TgMember(name1)
        self.assertEqual(dv.setMember(mb1), mb1)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1})
        self.assertEqual(dv.attributes, [name1])
        self.assertEqual(dv.properties, [])
        self.assertEqual(dv.commands, [])
        self.assertEqual(dv.proxy, None)


        name2 ="wmyname%s"% self.__rnd.randint(0, 9)
        mb2 = TgMember(name2)
        self.assertEqual(dv.setMember(mb2), mb2)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2})
        self.assertEqual(dv.attributes, [name1, name2])
        self.assertEqual(dv.properties, [])
        self.assertEqual(dv.commands, [])
        self.assertEqual(dv.proxy, None)


        name3 ="cmyname%s"% self.__rnd.randint(0, 9)
        mb3 = TgMember(name3, "command")
        self.assertEqual(dv.setMember(mb3), mb3)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3})
        self.assertEqual(dv.attributes, [name1, name2])
        self.assertEqual(dv.properties, [])
        self.assertEqual(dv.commands, [name3])
        self.assertEqual(dv.proxy, None)




        name4 ="c2myname%s"% self.__rnd.randint(0, 9)
        mb4 = TgMember(name4, "command")
        self.assertEqual(dv.setMember(mb4), mb4)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4})
        self.assertEqual(dv.attributes, [name1, name2])
        self.assertEqual(dv.properties, [])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)



        name5 ="pmyname%s"% self.__rnd.randint(0, 9)
        mb5 = TgMember(name5, "property")
        self.assertEqual(dv.setMember(mb5), mb5)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5})
        self.assertEqual(dv.attributes, [name1, name2])
        self.assertEqual(dv.properties, [name5])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)



        name6 ="ppmyname%s"% self.__rnd.randint(0, 9)
        mb6 = TgMember(name6, "property")
        self.assertEqual(dv.setMember(mb6), mb6)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6})
        self.assertEqual(dv.attributes, [name1, name2])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)





        name7 ="aamyname%s"% self.__rnd.randint(0, 9)
        mb7 = TgMember(name7, "attribute")
        self.assertEqual(dv.setMember(mb7), mb7)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)


        mb8= TgMember(name1, "attribute")
        self.assertEqual(dv.setMember(mb8), mb1)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)



        mb9= TgMember(name2, "attribute")
        self.assertEqual(dv.setMember(mb9), mb2)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)


        mb10= TgMember(name3, "attribute")
        self.assertEqual(dv.setMember(mb10), mb3)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)

        mb11= TgMember(name4, "attribute")
        self.assertEqual(dv.setMember(mb11), mb4)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)

        mb12= TgMember(name5, "attribute")
        self.assertEqual(dv.setMember(mb12), mb5)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)

        mb13= TgMember(name6, "attribute")
        self.assertEqual(dv.setMember(mb13), mb6)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)

        mb14= TgMember(name7, "attribute")
        self.assertEqual(dv.setMember(mb14), mb7)
        self.assertEqual(dv.device, device)
        self.assertEqual(dv.members, {name1:mb1, name2:mb2, name3:mb3, name4:mb4, name5:mb5, name6:mb6, name7:mb7})
        self.assertEqual(dv.attributes, [name1, name2, name7])
        self.assertEqual(dv.properties, [name5, name6])
        self.assertEqual(dv.commands, [name3, name4])
        self.assertEqual(dv.proxy, None)
















    
if __name__ == '__main__':
    unittest.main()
