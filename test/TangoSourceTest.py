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


#import pni.io.nx.h5 as nx


from ndts.DataSources import DataSource
from ndts.DataSources import TangoSource
from ndts.Errors import DataSourceSetupError

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class TangoSourceTest(unittest.TestCase):

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
        self.assertEqual(ds.__str__(), "Tango Device %s : %s (%s)" % (None, None, None))

        ds.device = device
        ds.name = None
        ds.memberType = None
        self.assertEqual(ds.__str__(), "Tango Device %s : %s (%s)" % (device, None, None))

        ds.device = None
        ds.name = dname
        ds.memberType = None
        self.assertEqual(ds.__str__(), "Tango Device %s : %s (%s)" % (None, dname, None))

        ds.device = None
        ds.name = None
        ds.memberType = mtype
        self.assertEqual(ds.__str__(), "Tango Device %s : %s (%s)" % (None, None, mtype))

        ds.device = device
        ds.name = dname
        ds.memberType = mtype
        self.assertEqual(ds.__str__(), "Tango Device %s : %s (%s)" % (device, dname, mtype))




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
        self.assertEqual(ds.hostname, '')
        self.assertEqual(ds.port, '')
        self.assertEqual(ds.encoding, '')


        ds.device = None
        ds.name = None
        ds.memberType = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' member ='%s'/> </datasource>" % 
                 (dname,device,ctype))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, ctype)
        self.assertEqual(ds.hostname, '')
        self.assertEqual(ds.port, '')
        self.assertEqual(ds.encoding, '')



        ds.device = None
        ds.name = None
        ds.memberType = None
        ds.setup("<datasource> <record name='%s'/> <device name='%s' member ='%s'/> </datasource>" % 
                 (dname,device,'strange'))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, atype)
        self.assertEqual(ds.hostname, '')
        self.assertEqual(ds.port, '')
        self.assertEqual(ds.encoding, '')


        ds.device = None
        ds.name = None
        ds.memberType = None
        
        ds.setup("<datasource> <record name='%s'/> <device name='%s' hostname='%s'/> </datasource>" % 
                 (dname,device,host))
        self.assertEqual(ds.name, dname)
        self.assertEqual(ds.device, device)
        self.assertEqual(ds.memberType, atype)
        self.assertEqual(ds.hostname, host)
        self.assertEqual(ds.port, '')
        self.assertEqual(ds.encoding, '')



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
        self.assertEqual(ds.encoding, '')


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
        self.assertEqual(ds.hostname, '')
        self.assertEqual(ds.port, '')
        self.assertEqual(ds.encoding, encoding)



    ## getData test
    # \brief It tests default settings
    def test_getData(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.getData(), None)


    ## isValid test
    # \brief It tests default settings
    def test_isValid(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.isValid(), True)




    ## getText test
    # \brief It tests default settings
    def test_getText_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = TangoSource()
        self.assertTrue(isinstance(el, object))
        self.myAssertRaise(AttributeError,el._getText, None) 

        dom = minidom.parseString("<tag/>")
        node = dom.getElementsByTagName("tag")
        self.assertEqual(el._getText(node[0]).strip(),'') 

        text = "My test \n text"
        dom = minidom.parseString("<tag> %s</tag>" % text)
        node = dom.getElementsByTagName("tag")
        self.assertEqual(el._getText(node[0]).strip(),text) 


        text = "My test text"
        dom = minidom.parseString("<node> %s</node>" % text)
        node = dom.getElementsByTagName("node")
        self.assertEqual(el._getText(node[0]).strip(),text) 


        dom = minidom.parseString("<node></node>" )
        node = dom.getElementsByTagName("node")
        self.assertEqual(el._getText(node[0]).strip(),'') 


    
if __name__ == '__main__':
    unittest.main()
