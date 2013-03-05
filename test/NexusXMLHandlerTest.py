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
from ndts.Element import Element
from ndts.H5Elements import (EGroup, EField, EAttribute, ELink, EDoc, ESymbol, 
                        EDimensions, EDim, EStrategy, FElement, EFile, FElement)
from ndts.DataSourceFactory import DataSourceFactory

from xml import sax

try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)



from  xml.sax import SAXParseException


from ndts.NexusXMLHandler import NexusXMLHandler

## test element
class TElement(object):
    ## The last TElement instance
    instance = None
    ## groupTypes
    groupTypes = {"NXmyentry":"myentry1"}

    ## consturctor
    def __init__(self, attrs, last):
        TElement.instance = self
        ## costructor flag
        self.constructed = True
        ## fetchName flag
        self.fetched = False
        ## createLink flag
        self.linked = False
        ## store flag
        self.stored=False
        ## sax attributes
        self.attrs = attrs
        ## tag content 
        self.content = []
        ## the last object
        self.last = last
        ## groupTypes
        self.groupTypes = {}

    ## fetches names   
    def fetchName(self, groupTypes):
        self.fetched = True
        for k in TElement.groupTypes:
            groupTypes[k] = TElement.groupTypes[k]


    ## creates links
    def createLink(self, groupTypes):
        self.linked = True
        self.groupTypes = {}
        for k in groupTypes:
            self.groupTypes[k] = groupTypes[k]

    ## stores names   
    def store(self):
        self.stored = True





## test element
class TElementOS(object):
    ## The last TElement instance
    instance = None
    ## groupTypes
    groupTypes = {"NXmyentry":"myentry1"}

    ## consturctor
    def __init__(self, attrs, last):
        TElementOS.instance = self
        ## costructor flag
        self.constructed = True
        ## fetchName flag
        self.fetched = False
        ## createLink flag
        self.linked = False
        ## store flag
        self.stored=False
        ## sax attributes
        self.attrs = attrs
        ## tag content 
        self.content = []
        ## the last object
        self.last = last
        ## groupTypes
        self.groupTypes = {}

    ## fetches names   
    def fetchName(self, groupTypes):
        self.fetched = True
        for k in TElement.groupTypes:
            groupTypes[k] = TElementOS.groupTypes[k]


    ## creates links
    def createLink(self, groupTypes):
        self.linked = True
        self.groupTypes = {}
        for k in groupTypes:
            self.groupTypes[k] = groupTypes[k]




## test element
class TElementOL(object):
    ## The last TElement instance
    instance = None
    ## groupTypes
    groupTypes = {"NXmyentry":"myentry1"}

    ## consturctor
    def __init__(self, attrs, last):
        TElementOL.instance = self
        ## costructor flag
        self.constructed = True
        ## fetchName flag
        self.fetched = False
        ## createLink flag
        self.linked = False
        ## store flag
        self.stored=False
        ## sax attributes
        self.attrs = attrs
        ## tag content 
        self.content = []
        ## the last object
        self.last = last
        ## groupTypes
        self.groupTypes = {}

    ## fetches names   
    def fetchName(self, groupTypes):
        self.fetched = True
        for k in TElement.groupTypes:
            groupTypes[k] = TElementOL.groupTypes[k]




## test element
class TElementOF(object):
    ## The last TElement instance
    instance = None
    ## groupTypes
    groupTypes = {"NXmyentry":"myentry1"}

    ## consturctor
    def __init__(self, attrs, last):
        TElementOF.instance = self
        ## costructor flag
        self.constructed = True
        ## fetchName flag
        self.fetched = False
        ## createLink flag
        self.linked = False
        ## store flag
        self.stored=False
        ## sax attributes
        self.attrs = attrs
        ## tag content 
        self.content = []
        ## the last object
        self.last = last
        ## groupTypes
        self.groupTypes = {}




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
        self.assertEqual(nh.withXMLinput, {'datasource':DataSourceFactory, 'doc':EDoc} )
        self.assertEqual(nh.elementClass, {'group':EGroup, 'field':EField, 'attribute':EAttribute,
                                           'link':ELink,
                                           'symbols':Element, 'symbol':ESymbol, 
                                           'dimensions':EDimensions, 
                                           'dim':EDim, 'enumeration':Element, 'item':Element,
                                           'strategy':EStrategy
                                           })
        self.assertEqual(nh.transparentTags, ['definition'] )
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

        os.remove(self._fname)



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


    ## constructor test
    # \brief It tests default settings
    def test_XML_field(self):
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
 
        attr1 = {"name":"counter","type":"NX_CHAR", "axis":1}
        sattr1 = {attr1["type"]:attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        parser = sax.make_parser()
        sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"counter")
        self.assertEqual(en.nattrs,2)
        self.assertEqual(en.read(), value)
        self.assertTrue(hasattr(en.shape,"__iter__"))
        self.assertEqual(len(en.shape),1)
        self.assertEqual(en.shape[0],1)
        

        at = en.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_CHAR")

        at = en.attr("axis")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"int64")
        self.assertEqual(at.name,"axis")
        self.assertEqual(at.value, 1)

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)




    ## constructor test
    # \brief It tests default settings
    def test_field(self):
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
 
        attr1 = {"name":"counter","type":"NX_CHAR"}
        sattr1 = {attr1["type"]:attr1["name"]}

        self.assertEqual(el.startElement("field",attr1), None)
        self.assertEqual(el.characters("field"), None)
        self.assertEqual(el.endElement("field"), None)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"counter")
        self.assertEqual(en.nattrs,1)
        self.assertEqual(en.read(),"field")
        self.assertTrue(hasattr(en.shape,"__iter__"))
        self.assertEqual(len(en.shape),1)
        self.assertEqual(en.shape[0],1)
        

        at = en.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_CHAR")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_field_empty(self):
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
 
        attr1 = {"name":"counter","type":"NX_CHAR"}
        sattr1 = {attr1["type"]:attr1["name"]}

        self.assertEqual(el.startElement("field",attr1), None)
        self.assertEqual(el.characters(""), None)
        self.assertEqual(el.endElement("field"), None)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"counter")
        self.assertEqual(en.nattrs,1)
        self.assertEqual(en.read(),"")
        self.assertTrue(hasattr(en.shape,"__iter__"))
        self.assertEqual(len(en.shape),1)
        self.assertEqual(en.shape[0],1)
        

        at = en.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_CHAR")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)


    ## constructor test
    # \brief It tests default settings
    def test_XML_field_empty(self):
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
 
        attr1 = {"name":"counter","type":"NX_CHAR"}
        sattr1 = {attr1["type"]:attr1["name"]}


        value = ''
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        parser = sax.make_parser()
        sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"counter")
        self.assertEqual(en.nattrs,1)
        self.assertEqual(en.read(),"")
        self.assertTrue(hasattr(en.shape,"__iter__"))
        self.assertEqual(len(en.shape),1)
        self.assertEqual(en.shape[0],1)
        

        at = en.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_CHAR")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)


    ## constructor test
    # \brief It tests default settings
    def test_field_value_error(self):
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
 
        attr1 = {"name":"counter","type":"NX_INT"}
        sattr1 = {attr1["type"]:attr1["name"]}

        self.assertEqual(el.startElement("field",attr1), None)
        self.assertEqual(el.characters(""), None)
        self.myAssertRaise(ValueError,el.endElement,"field")

        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_XML_field_value_error(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._eFile = EFile([], None, self._nxFile)

        el = NexusXMLHandler(self._eFile)


        attr1 = {"name":"counter","type":"NX_INT"}
        sattr1 = {attr1["type"]:attr1["name"]}


        value = ''
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        parser = sax.make_parser()
        self.myAssertRaise(ValueError,sax.parseString,xml, el)
 


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_group_field(self):
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

        attr2 = {"name":"counter","type":"NX_INT"}
        sattr2 = {attr2["type"]:attr2["name"]}

        self.assertEqual(el.startElement("group",attr1), None)
        self.assertEqual(el.startElement("field",attr2), None)
        self.assertEqual(el.characters("1234"), None)
        self.assertEqual(el.endElement("field"), None)
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

        cnt = en.open(attr2["name"])
        self.assertTrue(cnt.valid)
        self.assertEqual(cnt.name,"counter")
        self.assertEqual(cnt.nattrs,1)
        self.assertEqual(cnt.read(),1234)
        self.assertTrue(hasattr(cnt.shape,"__iter__"))
        self.assertEqual(len(cnt.shape),1)
        self.assertEqual(cnt.shape[0],1)
        
        at = cnt.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_INT")


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_XML_group_field(self):
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

        attr2 = {"name":"counter","type":"NX_INT"}
        sattr2 = {attr2["type"]:attr2["name"]}



        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a]) 
        xml += '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        xml +=  '</group>'
        
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

        cnt = en.open(attr2["name"])
        self.assertTrue(cnt.valid)
        self.assertEqual(cnt.name,"counter")
        self.assertEqual(cnt.nattrs,1)
        self.assertEqual(cnt.read(),1234)
        self.assertTrue(hasattr(cnt.shape,"__iter__"))
        self.assertEqual(len(cnt.shape),1)
        self.assertEqual(cnt.shape[0],1)

        at = cnt.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_INT")


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)


    ## constructor test
    # \brief It tests default settings
    def test_XML_group_attribute(self):
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

        attr2 = {"name":"counter","type":"NX_INT32"}
        sattr2 = {attr2["type"]:attr2["name"]}

  


        value = '1234'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<group%s>' % (st)
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a]) 
        xml += '<attribute%s>' % (st)
        xml +=  value
        xml +=  '</attribute>'
        xml +=  '</group>'
        
        parser = sax.make_parser()
        sax.parseString(xml, el)


        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry1")
        self.assertEqual(en.nattrs,2)

        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")

        at = en.attr(attr2["name"])
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.name,"counter")
        self.assertEqual(at.dtype,"int32")
        self.assertEqual(at.value,1234)
        


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_group_attribute(self):
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

        attr2 = {"name":"counter","type":"NX_INT32"}
        sattr2 = {attr2["type"]:attr2["name"]}

        self.assertEqual(el.startElement("group",attr1), None)
        self.assertEqual(el.startElement("attribute",attr2), None)
        self.assertEqual(el.characters("1234"), None)
        self.assertEqual(el.endElement("attribute"), None)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry1")
        self.assertEqual(en.nattrs,2)

        at = en.attr("NX_class")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"NX_class")
        self.assertEqual(at.value,"NXentry")

        at = en.attr(attr2["name"])
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.name,"counter")
        self.assertEqual(at.dtype,"int32")
        self.assertEqual(at.value,1234)
        


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)






    ## constructor test
    # \brief It tests default settings
    def test_XML_field_attribute(self):
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
 
        attr1 = {"name":"entry1","type":"NX_CHAR"}
        sattr1 = {attr1["type"]:attr1["name"]}

        attr2 = {"name":"counter","type":"NX_INT32"}
        sattr2 = {attr2["type"]:attr2["name"]}

  


        value1 = '1234'
        value2 = '34'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value1
        st = ''
        for a in attr2:
            st += ' %s="%s"' % (a, attr2[a]) 
        xml += '<attribute%s>' % (st)
        xml +=  value2
        xml +=  '</attribute>'
        xml +=  '</field>'
        
        parser = sax.make_parser()
        sax.parseString(xml, el)


        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry1")
        self.assertEqual(en.nattrs,2)
        self.assertEqual(en.read(),'1234')
        self.assertTrue(hasattr(en.shape,"__iter__"))
        self.assertEqual(len(en.shape),1)
        self.assertEqual(en.shape[0],1)

        at = en.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_CHAR")

        at = en.attr(attr2["name"])
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.name,"counter")
        self.assertEqual(at.dtype,"int32")
        self.assertEqual(at.value,34)
        


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)



    ## constructor test
    # \brief It tests default settings
    def test_field_attribute(self):
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
 
        attr1 = {"name":"entry1","type":"NX_INT"}
        sattr1 = {attr1["type"]:attr1["name"]}

        attr2 = {"name":"counter","type":"NX_INT32"}
        sattr2 = {attr2["type"]:attr2["name"]}

        self.assertEqual(el.startElement("field",attr1), None)
        self.assertEqual(el.characters("12"), None)
        self.assertEqual(el.startElement("attribute",attr2), None)
        self.assertEqual(el.characters("1234"), None)
        self.assertEqual(el.endElement("attribute"), None)
        self.assertEqual(el.endElement("field"), None)

        self.assertEqual(el.triggerPools, {})
        
        en = self._nxFile.open(attr1["name"])
        self.assertTrue(en.valid)
        self.assertEqual(en.name,"entry1")
        self.assertEqual(en.nattrs,2)
        self.assertTrue(hasattr(en.shape,"__iter__"))
        self.assertEqual(len(en.shape),1)
        self.assertEqual(en.shape[0],1)
        self.assertEqual(en.read(),12)

        at = en.attr("type")
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.dtype,"string")
        self.assertEqual(at.name,"type")
        self.assertEqual(at.value,"NX_INT")

        at = en.attr(attr2["name"])
        self.assertTrue(at.valid)
        self.assertTrue(hasattr(at.shape,"__iter__"))
        self.assertEqual(len(at.shape),0)
        self.assertEqual(at.name,"counter")
        self.assertEqual(at.dtype,"int32")
        self.assertEqual(at.value,1234)
        


        self.assertEqual(el.close(), None)

        self._nxFile.close()
        os.remove(self._fname)




    ## constructor test
    # \brief It tests default settings
    def test_TE_field(self):
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
        TElement.instance = None
        el.elementClass = {"field":TElement}


        attr1 = {"name":"counter","type":"NX_CHAR", "axis":1}
        sattr1 = {attr1["type"]:attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        parser = sax.make_parser()
        sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        
        ins = TElement.instance
        self.assertTrue(isinstance(ins, TElement))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertEqual(TElement.groupTypes, {"NXmyentry":"myentry1"})
        self.assertTrue(ins.fetched)
        self.assertTrue(ins.linked)
        self.assertTrue(ins.stored)
        self.assertEqual(len(TElement.groupTypes)+1, len(ins.groupTypes))
        for a in TElement.groupTypes:
            self.assertEqual(str(TElement.groupTypes[a]), ins.groupTypes[a])
        self.assertEqual("", ins.groupTypes[""])
        
        


        self._nxFile.close()
        os.remove(self._fname)


    ## constructor test
    # \brief It tests default settings
    def test_TEOS_field(self):
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
        TElementOS.instance = None
        el.elementClass = {"field":TElementOS}


        attr1 = {"name":"counter","type":"NX_CHAR", "axis":1}
        sattr1 = {attr1["type"]:attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        parser = sax.make_parser()
        sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        
        ins = TElementOS.instance
        self.assertTrue(isinstance(ins, TElementOS))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertEqual(TElementOS.groupTypes, {"NXmyentry":"myentry1"})
        self.assertTrue(ins.fetched)
        self.assertTrue(ins.linked)
        self.assertEqual(len(TElementOS.groupTypes)+1, len(ins.groupTypes))
        for a in TElementOS.groupTypes:
            self.assertEqual(str(TElementOS.groupTypes[a]), ins.groupTypes[a])
        self.assertEqual("", ins.groupTypes[""])
                

        self._nxFile.close()
        os.remove(self._fname)




    ## constructor test
    # \brief It tests default settings
    def test_TEOL_field(self):
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
        TElementOL.instance = None
        el.elementClass = {"field":TElementOL}


        attr1 = {"name":"counter","type":"NX_CHAR", "axis":1}
        sattr1 = {attr1["type"]:attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        parser = sax.make_parser()
        sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        
        ins = TElementOL.instance
        self.assertTrue(isinstance(ins, TElementOL))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertEqual(TElementOL.groupTypes, {"NXmyentry":"myentry1"})
        self.assertTrue(ins.fetched)
        self.assertEqual(len(ins.groupTypes), 0)
                

        self._nxFile.close()
        os.remove(self._fname)


    ## constructor test
    # \brief It tests default settings
    def test_TEOF_field(self):
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
        TElementOF.instance = None
        el.elementClass = {"field":TElementOF}


        attr1 = {"name":"counter","type":"NX_CHAR", "axis":1}
        sattr1 = {attr1["type"]:attr1["name"]}

        value = 'myfield'
        st = ''
        for a in attr1:
            st += ' %s="%s"' % (a, attr1[a]) 
        xml = '<field%s>' % (st)
        xml +=  value
        xml +=  '</field>'
        parser = sax.make_parser()
        sax.parseString(xml, el)

        self.assertEqual(el.triggerPools, {})
        
        ins = TElementOF.instance
        self.assertTrue(isinstance(ins, TElementOF))
        self.assertTrue(ins.constructed)
        self.assertEqual(len(attr1), len(ins.attrs))
        for a in attr1:
            self.assertEqual(str(attr1[a]), ins.attrs[a])
        self.assertEqual(ins.last, self._eFile)
        self.assertEqual(ins.content, [value])
        self.assertEqual(TElementOF.groupTypes, {"NXmyentry":"myentry1"})
        self.assertEqual(len(ins.groupTypes), 0)
                

        self._nxFile.close()
        os.remove(self._fname)



if __name__ == '__main__':
    unittest.main()
