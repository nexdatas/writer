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
## \file NexusXMLHandlerTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
from ndts.H5Elements import EFile
from ndts.ThreadPool import ThreadPool

from xml import sax

try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



from  xml.sax import SAXParseException


from ndts.NexusXMLHandler import NexusXMLHandler

## test fixture
class NexusXMLHandlerTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None        

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

    ## test starter
    # \brief Common set up
    def setUp(self):
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
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._eFile = EFile([], None, self._nxFile)

        nh = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(nh,sax.ContentHandler))
        self.assertTrue(isinstance(nh.initPool,ThreadPool))
        self.assertTrue(isinstance(nh.stepPool,ThreadPool))
        self.assertTrue(isinstance(nh.finalPool,ThreadPool))
        self.assertEqual(nh.triggerPools, {})
        self.assertEqual(nh.close(), None)

        self._nxFile.close()
        os.remove(self._fname)

    ## constructor test
    # \brief It tests default settings
    def test_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool,ThreadPool))
        self.assertTrue(isinstance(el.stepPool,ThreadPool))
        self.assertTrue(isinstance(el.finalPool,ThreadPool))
        self.assertEqual(el.triggerPools, {})
 
        attr1 = {"name":"entry","type":"NXentry"}
        sattr1 = {attr1["type"]:attr1["name"]}

        self.assertEqual(el.startElement("group",attr1), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry")
        self.assertEqual(en.nattrs,1)
        self.assertEqual(en.nchildren, 0)
        

        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_XML_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._eFile = EFile([], None, self._nxFile)
        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool,ThreadPool))
        self.assertTrue(isinstance(el.stepPool,ThreadPool))
        self.assertTrue(isinstance(el.finalPool,ThreadPool))
        self.assertEqual(el.triggerPools, {})
 
        attr1 = {"name":"entry","type":"NXentry","shortname":"myentry"}
        sattr1 = {attr1["type"]:attr1["name"]}
        st = ''
        for a in attr1:
            st += ' %s ="%s"' % (a, attr1[a]) 
        xml = '<group%s/>' % (st)

        parser = sax.make_parser()
        sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry")
        self.assertEqual(en.nattrs,2)
        self.assertEqual(en.nchildren, 0)
        

        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")


        at = en.attr("shortname")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"shortname")
        self.assertEqual(at.value,"myentry")

        self.assertEqual(el.close(), None)

#        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_group_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool,ThreadPool))
        self.assertTrue(isinstance(el.stepPool,ThreadPool))
        self.assertTrue(isinstance(el.finalPool,ThreadPool))
        self.assertEqual(el.triggerPools, {})
 
        attr1 = {"name":"entry1","type":"NXentry"}
        sattr1 = {attr1["type"]:attr1["name"]}

        attr2 = {"name":"instrument","type":"NXinstrument"}
        sattr2 = {attr2["type"]:attr2["name"]}

        self.assertEqual(el.startElement("group",attr1), None)
        self.assertEqual(el.startElement("group",attr2), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry1")
        self.assertEqual(en.nattrs,1)
        self.assertEqual(en.nchildren, 1)

        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")

        ins = en.open(attr2["name"])
        self.assertTrue(ins.valid)
        self.assertEqual(ins.name,"instrument")
        self.assertEqual(ins.nattrs,1)
        self.assertEqual(ins.nchildren, 0)
        
        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)


    ## constructor test
    # \brief It tests default settings
    def test_XML_group_group(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(el.initPool,ThreadPool))
        self.assertTrue(isinstance(el.stepPool,ThreadPool))
        self.assertTrue(isinstance(el.finalPool,ThreadPool))
        self.assertEqual(el.triggerPools, {})
 
        attr1 = {"name":"entry1","type":"NXentry"}
        sattr1 = {attr1["type"]:attr1["name"]}

        attr2 = {"name":"instrument","type":"NXinstrument","signal":"1"}
        sattr2 = {attr2["type"]:attr2["name"]}
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<group%s>' % (st)

        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a]) 
        xml += '<group%s/>' % (st)
        xml += '</group>'

        parser = sax.make_parser()
        sax.parseString(xml, el)



        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry1")
        self.assertEqual(en.nattrs,1)
        self.assertEqual(en.nchildren, 1)

        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")

        ins = en.open(attr2["name"])
        self.assertTrue(ins.valid)
        self.assertEqual(ins.name,"instrument")
        self.assertEqual(ins.nattrs,2)
        self.assertEqual(ins.nchildren, 0)
        
        at = ins.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXinstrument")

        at = ins.attr("signal")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"int64")
        self.assertEqual(at.name,"signal")
        self.assertEqual(at.value,1)


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
