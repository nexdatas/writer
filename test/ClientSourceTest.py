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
## \file ClientSourceTest.py
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
import json

#import pni.io.nx.h5 as nx


from ndts.DataSources import DataSource
from ndts.DataSources import ClientSource
from ndts.Errors import DataSourceSetupError

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class ClientSourceTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)



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
        
        
        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.name, None)
        

    ## __str__ test
    # \brief It tests default settings
    def test_str_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        name = 'myrecord'
        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), "Client record %s from JSON: %s or %s " % (None,None,None))

        ds = ClientSource()
        ds.name = name                 
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.__str__(), "Client record %s from JSON: %s or %s " % (name,None,None))

        ds = ClientSource()
        gjson = '{"data":{"myrecord":"1"}}'
        self.assertEqual(ds.setJSON(json.loads(gjson)),None)
        self.assertEqual(ds.__str__(), "Client record %s from JSON: %s or %s " % (name,None,json.loads(gjson)))

        ds = ClientSource()
        ljson = '{"data":{"myrecord2":1}}'
        self.assertEqual(ds.setJSON(json.loads(gjson),json.loads(ljson)),None)
        self.assertEqual(ds.__str__(), "Client record %s from JSON: %s or %s " % (name,json.loads(ljson),json.loads(gjson)))


    ## setup test
    # \brief It tests default settings
    def test_setup_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        dname = 'writer'
        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup,"<datasource/>")

        ds = ClientSource()
        self.assertTrue(isinstance(ds, DataSource))
        self.myAssertRaise(DataSourceSetupError, ds.setup,"<datasource><record/></datasource>")

        ds = ClientSource()
        self.assertEqual(ds.name ,None)
        self.assertTrue(isinstance(ds, DataSource))
        self.assertEqual(ds.setup("<datasource><record name='%s'/></datasource>" % dname),None)
        self.assertEqual(ds.name ,dname)



    ## getData test
    # \brief It tests default settings
    def test_getData(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = ClientSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.getData(), None)


    ## isValid test
    # \brief It tests default settings
    def test_isValid(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = ClientSource()
        self.assertTrue(isinstance(el, object))
        self.assertEqual(el.isValid(), True)




    ## getText test
    # \brief It tests default settings
    def test_getText_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)


        el = ClientSource()
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
