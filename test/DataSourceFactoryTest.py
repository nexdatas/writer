#!/usr/bin/env python3
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

import TestDataSource 


from nxswriter.DataSourceFactory import DataSourceFactory
from nxswriter.DataSources import DataSource
from nxswriter.DataSourcePool import DataSourcePool
from nxswriter.DecoderPool import DecoderPool
from nxswriter.Element import Element
from nxswriter.EField import EField
from nxswriter import DataSources
from nxswriter import ClientSource
from nxswriter import PyEvalSource
from nxswriter.Errors import DataSourceSetupError

from nxswriter.DecoderPool import DecoderPool

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
        print("\nsetting up...")        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    ## Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except exception as e:
            error = True
        self.assertEqual(error, True)


    ## Data check 
    # \brief It check the source Data
    # \param data  tested data
    # \param format data format
    # \param value data value
    # \param ttype data Tango type    
    # \param shape data shape    
    def checkData(self, data, format, value, ttype, shape):
        self.assertEqual(data["rank"], format)
        self.assertEqual(data["tangoDType"], ttype)
        self.assertEqual(data["shape"], shape)
        if format == 'SCALAR': 
            self.assertEqual(data["value"], value)
        elif format == 'SPECTRUM': 
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(data["value"][i], value[i])
        else: 
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(len(data["value"][i]), len(value[i]))
                for j in range(len(value[i])):
                    self.assertEqual(data["value"][i][j], value[i][j])
                

    ## constructor test
    # \brief It tests default settings
    def test_constructor_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))


        ds = DataSourceFactory(self._fattrs, None)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, self._fattrs)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, None)

        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(self._fattrs, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, self._fattrs)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)




    ## constructor test
    # \brief It tests default settings
    def test_store_default(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))


        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(self._fattrs, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, self._fattrs)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.store(["<datasource>","","</datasource>"]), None)
        self.assertEqual(type(ds.last.source),DataSources.DataSource)
        self.assertTrue(not hasattr(ds.last,"tagAttributes"))

        atts = {"type":"TANGO"}
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.store(["<datasource>","","</datasource>"]), None)
        self.assertEqual(type(ds.last.source),DataSources.DataSource)
        self.assertTrue(not hasattr(ds.last,"tagAttributes"))


        atts = {"type":"CLIENT"}
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.myAssertRaise(DataSourceSetupError,ds.store,["<datasource>","","</datasource>"])
        self.assertTrue(not hasattr(ds.last,"tagAttributes"))


        atts = {"type":"CLIENT"}
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.myAssertRaise(DataSourceSetupError,ds.store,["<datasource type='CLIENT'>","<record/>","</datasource>"])
        self.assertTrue(not hasattr(ds.last,"tagAttributes"))


        atts = {"type":"CLIENT"}
        name = "myRecord"
        el = Element(self._tfname, self._fattrs )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='CLIENT'>",
                                   '<record name="%s"/>' %name,
                                   "</datasource>"]),None)
        self.assertEqual(type(ds.last.source),ClientSource.ClientSource)
        self.assertEqual(ds.last.source.name,name)
        self.assertEqual(ds.last.source.name,name)
        self.assertEqual(ds.last.source.__str__(), " CLIENT record %s" 
                         % (name))
        self.assertTrue(not hasattr(ds.last,"tagAttributes"))



        atts = {"type":"CLIENT"}
        name = "myRecord"
        el = EField(self._fattrs, None )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='CLIENT'>",
                                   '<record name="%s"/>' %name,
                                   "</datasource>"]),None)
        self.assertEqual(type(ds.last.source),ClientSource.ClientSource)
        self.assertEqual(ds.last.source.name,name)
        self.assertEqual(ds.last.source.name,name)
        self.assertEqual(ds.last.source.__str__(), " CLIENT record %s" 
                         % (name)) 
        self.assertEqual(len(ds.last.tagAttributes),1)
        self.assertEqual(ds.last.tagAttributes["nexdatas_source"],('NX_CHAR','<datasource type=\'CLIENT\'><record name="myRecord"/></datasource>'))



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
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='CLIENT'>",
                                   '<record name="%s"/>' %name,
                                   "</datasource>"],gjson),None)
        self.assertEqual(type(ds.last.source),ClientSource.ClientSource)
        self.assertEqual(ds.last.source.name,name)
        self.assertEqual(ds.last.source.name,name)
        self.assertEqual(ds.last.source.__str__(), " CLIENT record %s" 
                         % (name))
        self.assertEqual(len(ds.last.tagAttributes),1)
        self.assertEqual(ds.last.tagAttributes["nexdatas_source"],('NX_CHAR', '<datasource type=\'CLIENT\'><record name="myRecord"/></datasource>'))
        dt = ds.last.source.getData()
        self.checkData(dt,"SCALAR",'1',"DevString",[])



        atts = {"type":"PYEVAL"}
        name = "myRecord"
        wjson = json.loads('{"datasources":{"CL":"ClientSource.ClientSource"}}')
        gjson = json.loads('{"data":{"myRecord":1123}}')
        el = EField(self._fattrs, None )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        self.assertEqual(ds.setDataSources(DataSourcePool()),None)
        self.assertEqual(ds.store(["<datasource type='PYEVAL'>",
                                   """
<datasource type="CLIENT" name="myclient">
  <record name="%s"/>
</datasource>
<result> 
ds.result = ds.myclient + 1
</result>
""" %name,
                                   "</datasource>"],gjson),None)
        self.assertEqual(type(ds.last.source),PyEvalSource.PyEvalSource)
        self.assertEqual(ds.last.source.__str__(), " PYEVAL  \nds.result = ds.myclient + 1\n")
        self.assertEqual(len(ds.last.tagAttributes),1)
        self.assertEqual(ds.last.tagAttributes["nexdatas_source"],('NX_CHAR','<datasource type=\'PYEVAL\'>\n<datasource type="CLIENT" name="myclient">\n  <record name="myRecord"/>\n</datasource>\n<result> \nds.result = ds.myclient + 1\n</result>\n</datasource>' ))
        dt = ds.last.source.getData()
        self.checkData(dt,"SCALAR",1124,"DevLong64",[])
        


    ## constructor test
    # \brief It tests default settings
    def test_check_flow(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))



        atts = {"type":"CL"}
        name = "myRecord"
        wjson = json.loads('{"datasources":{"CL":"TestDataSource.TestDataSource"}}')
        gjson = json.loads('{"data":{"myRecord":1123}}')
        el = EField(self._fattrs, None )
        ds = DataSourceFactory(atts, el)
        self.assertTrue(isinstance(ds, Element))
        self.assertEqual(ds.tagName, "datasource")
        self.assertEqual(ds._tagAttrs, atts)
        self.assertEqual(ds.content, [])
        self.assertEqual(ds.doc, "")
        self.assertEqual(ds.last, el)
        dsp = DataSourcePool(wjson)
        dcp = DecoderPool()
        self.assertEqual(ds.setDataSources(dsp),None)
        self.assertEqual(ds.store(["<datasource type='CL'>",
                                   """
<datasource type="CLIENT" name="myclient">
  <record name="%s"/>
</datasource>
<result> 
ds.result = ds.myclient + 1
</result>
""" %name,
                                   "</datasource>"],gjson),None)
        td = ds.last.source
        self.assertEqual(len(td.stack), 7)
        self.assertEqual(td.stack[0], "setup")
        self.assertEqual(td.stack[1], '<datasource type=\'CL\'>\n<datasource type="CLIENT" name="myclient">\n  <record name="myRecord"/>\n</datasource>\n<result> \nds.result = ds.myclient + 1\n</result>\n</datasource>')
        self.assertEqual(td.stack[2], 'setJSON')
        self.assertEqual(td.stack[3],  {u'data': {u'myRecord': 1123}})
        self.assertEqual(td.stack[4], None)
        self.assertEqual(td.stack[5], "setDataSources")
        self.assertEqual(td.stack[6], dsp)

        
        ds.setDecoders(dcp)
        self.assertEqual(len(td.stack), 10)
        self.assertEqual(td.stack[7], "isValid")
        self.assertEqual(td.stack[8], "setDecoders")
        self.assertEqual(td.stack[9], dcp)
        self.assertEqual(type(ds.last.source),TestDataSource.TestDataSource)
        self.assertEqual(ds.last.source.__str__(), "Test DataSource")
        self.assertEqual(len(td.stack), 11)
        self.assertEqual(td.stack[10], '__str__')
        self.assertEqual(len(ds.last.tagAttributes),1)
        self.assertEqual(ds.last.tagAttributes["nexdatas_source"],('NX_CHAR','<datasource type=\'CL\'>\n<datasource type="CLIENT" name="myclient">\n  <record name="myRecord"/>\n</datasource>\n<result> \nds.result = ds.myclient + 1\n</result>\n</datasource>' ))
        dt = ds.last.source.getData()
        self.assertEqual(len(td.stack), 12)
        self.assertEqual(td.stack[11], 'getData')
        self.checkData(dt,"SCALAR",1,"DevLong",[0,0])

        



        
if __name__ == '__main__':
    unittest.main()
