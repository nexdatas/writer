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
## \file DataSourceFactoryTest.py
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


#import pni.io.nx.h5 as nx

from ndts.DataSourceFactory import DataSourceFactory
from ndts.DataSources import TangoSource,ClientSource,DBaseSource,DataSource
from ndts.DataSourcePool import DataSourcePool
from ndts.Element import Element
from ndts.H5Elements import EField
from ndts import DataSources
from ndts.Errors import DataSourceSetupError

from ndts.DecoderPool import DecoderPool

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



## test fixture
class DataSourceFactoryTest(unittest.TestCase):

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

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name":"test","units":"m" }



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


        ds = DataSourceFactory(self._fattrs, None)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, self._fattrs)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, None)

        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(self._fattrs, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, self._fattrs)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)




    ## constructor test
    # \brief It tests default settings
    def test_store_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(self._fattrs, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, self._fattrs)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.store(["<datasource>","","</datasource>"]), None)
        self.assertEqual(type(ds._last.source),DataSources.DataSource)
        self.assertTrue(not hasattr(ds._last,"tagAttributes"))

        atts = {"type":"TANGO"}
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.store(["<datasource>","","</datasource>"]), None)
        self.assertEqual(type(ds._last.source),DataSources.DataSource)
        self.assertTrue(not hasattr(ds._last,"tagAttributes"))


        atts = {"type":"CLIENT"}
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.myAssertRaise(DataSourceSetupError,ds.store,["<datasource>","","</datasource>"])
        self.assertTrue(not hasattr(ds._last,"tagAttributes"))


        atts = {"type":"CLIENT"}
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.myAssertRaise(DataSourceSetupError,ds.store,["<datasource type='CLIENT'>","<record/>","</datasource>"])
        self.assertTrue(not hasattr(ds._last,"tagAttributes"))


        atts = {"type":"CLIENT"}
        name = "myRecord"
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='CLIENT'>",
                                   '<record name="%s"/>' %name,
                                   "</datasource>"]),None)
        self.assertEqual(type(ds._last.source),DataSources.ClientSource)
        self.assertEqual(ds._last.source.name,name)
        self.assertEqual(ds._last.source.name,name)
        self.assertEqual(ds._last.source.__str__(), " Client record %s from JSON: %s or %s " 
                         % (name,None,None))
        self.assertTrue(not hasattr(ds._last,"tagAttributes"))



        atts = {"type":"CLIENT"}
        name = "myRecord"
        el = EField(self._fattrs, None )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='CLIENT'>",
                                   '<record name="%s"/>' %name,
                                   "</datasource>"]),None)
        self.assertEqual(type(ds._last.source),DataSources.ClientSource)
        self.assertEqual(ds._last.source.name,name)
        self.assertEqual(ds._last.source.name,name)
        self.assertEqual(ds._last.source.__str__(), " Client record %s from JSON: %s or %s " 
                         % (name,None,None)) 
        self.assertEqual(len(ds._last.tagAttributes),1)
        self.assertEqual(ds._last.tagAttributes["nexdatas_source"],('NX_CHAR','<datasource type=\'CLIENT\'><record name="myRecord"/></datasource>'))



        atts = {"type":"CLIENT"}
        name = "myRecord"
        wjson = json.loads('{"datasources":{"CL":"DataSources.ClientSource"}}')
        gjson = json.loads('{"data":{"myRecord":"1"}}')
        
        el = EField(self._fattrs, None )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='CLIENT'>",
                                   '<record name="%s"/>' %name,
                                   "</datasource>"],gjson),None)
        self.assertEqual(type(ds._last.source),DataSources.ClientSource)
        self.assertEqual(ds._last.source.name,name)
        self.assertEqual(ds._last.source.name,name)
        self.assertEqual(ds._last.source.__str__(), " Client record %s from JSON: %s or %s " 
                         % (name, None, str(gjson)))
        self.assertEqual(len(ds._last.tagAttributes),1)
        self.assertEqual(ds._last.tagAttributes["nexdatas_source"],('NX_CHAR', '<datasource type=\'CLIENT\'><record name="myRecord"/></datasource>'))

        



    ## constructor test
    # \brief It tests default settings
    def test_setDecoders_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        dname = 'writer'
        device = 'p09/tdw/r228'
        ctype = 'command'
        atype = 'attribute'
        host = 'haso.desy.de'
        port = '10000'
        encoding = 'UTF8'


        atts = {"type":"TANGO"}
        name = "myRecord"
        wjson = json.loads('{"datasources":{"CL":"DataSources.ClientSource"}}')
        gjson = json.loads('{"data":{"myRecord":"1"}}')
        
        el = EField(self._fattrs, None )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='TANGO'>",
                                   "<record name='%s'/> <device name='%s' encoding='%s'/>" % (dname,device,encoding),
                                   "</datasource>"],gjson),None)
        self.assertEqual(type(ds._last.source),DataSources.TangoSource)
        self.assertEqual(ds._last.source.name,dname)
        self.assertEqual(ds._last.source.device,device)
        self.assertEqual(ds._last.source.encoding,encoding)
        self.assertEqual(ds._last.source.__str__() , " Tango Device %s : %s (%s)" % (device, dname, atype))
        self.assertEqual(len(ds._last.tagAttributes),1)
        self.assertEqual(ds._last.tagAttributes["nexdatas_source"],('NX_CHAR', "<datasource type='TANGO'><record name='writer'/> <device name='p09/tdw/r228' encoding='UTF8'/></datasource>") )



    ## constructor test
    # \brief It tests default settings
    def test_setDecoders(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        dname = 'writer'
        device = 'p09/tdw/r228'
        ctype = 'command'
        atype = 'attribute'
        host = 'haso.desy.de'
        port = '10000'
        encoding = 'UTF8'


        atts = {"type":"TANGO"}
        name = "myRecord"
        wjson = json.loads('{"datasources":{"CL":"DataSources.ClientSource"}}')
        gjson = json.loads('{"data":{"myRecord":"1"}}')
        
        el = EField(self._fattrs, None )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds._last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='TANGO'>",
                                   "<record name='%s'/> <device name='%s' encoding='%s'/>" % (dname,device,encoding),
                                   "</datasource>"],gjson),None)
        self.assertEqual(type(ds._last.source),DataSources.TangoSource)
        self.assertEqual(ds._last.source.name,dname)
        self.assertEqual(ds._last.source.device,device)
        self.assertEqual(ds._last.source.encoding,encoding)
        self.assertEqual(ds._last.source.__str__() , " Tango Device %s : %s (%s)" % (device, dname, atype))
        self.assertEqual(len(ds._last.tagAttributes),1)
        self.assertEqual(ds._last.tagAttributes["nexdatas_source"],('NX_CHAR', "<datasource type='TANGO'><record name='writer'/> <device name='p09/tdw/r228' encoding='UTF8'/></datasource>") )
        dp = DecoderPool()
        self.assertEqual(ds.setDecoders(dp),None)
        

        
if __name__ == '__main__':
    unittest.main()
