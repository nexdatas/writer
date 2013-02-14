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
## \file EGroupTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import random
import numpy


import pni.io.nx.h5 as nx


from ndts.H5Elements import FElementWithAttr
from ndts.H5Elements import FElement
from ndts.H5Elements import EGroup
from ndts.Element import Element
from ndts.H5Elements import EFile
from ndts.Types import NTP, Converters
from ndts.H5Elements import XMLSettingSyntaxError

from Checkers import Checker 

#from  xml.sax import SAXParseException



## test fixture
class EGroupTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None        

        self._gattrs = {"name":"test","type":"NXentry" }
        self._gname = "testGroup"
        self._gtype = "NXentry"


        self._sc = Checker(self)

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

    ## default constructor test
    # \brief It tests default settings
    def test_default_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile( [], None, self._nxFile)
        el = EGroup( self._gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), nx.nxh5.NXGroup)
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(el.h5Object.nattrs, 1)
        self.assertEqual(el.h5Object.attr("NX_class").value, self._gattrs["type"])
        self.assertEqual(el.h5Object.attr("NX_class").dtype, "string")
        self.assertEqual(el.h5Object.attr("NX_class").shape, ())
        

        self._nxFile.close()
        os.remove(self._fname)



    ## default constructor test
    # \brief It tests default settings
    def test_constructor_noname(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile( [], None, self._nxFile)
        gattrs = {"type":"NXentry" , "short_name":"shortname" }
        el = EGroup( gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), nx.nxh5.NXGroup)
        self.assertEqual(el.h5Object.name, gattrs["type"][2:])
        self.assertEqual(el.h5Object.nattrs, 2)
        self.assertEqual(el.h5Object.attr("NX_class").value, gattrs["type"])
        self.assertEqual(el.h5Object.attr("NX_class").dtype, "string")
        self.assertEqual(el.h5Object.attr("NX_class").shape, ())
        self.assertEqual(el.h5Object.attr("short_name").value, gattrs["short_name"])
        self.assertEqual(el.h5Object.attr("short_name").dtype, "string")
        self.assertEqual(el.h5Object.attr("short_name").shape, ())
        

        self._nxFile.close()
        os.remove(self._fname)


    ## default constructor test
    # \brief It tests default settings
    def test_constructor_noobject(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        gattrs = {"type":"NXentry" , "short_name":"shortname" }
        self.myAssertRaise(XMLSettingSyntaxError, EGroup, gattrs, None)




    ## default constructor test
    # \brief It tests default settings
    def test_constructor_notype(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile( [], None, self._nxFile)

        gattrs = {"short_name":"shortname" }
        self.myAssertRaise(XMLSettingSyntaxError, EGroup, gattrs, eFile)

        self._nxFile.close()
        os.remove(self._fname)



    ## default constructor test
    # \brief It tests default settings
    def test_constructor_aTn(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile( [], None, self._nxFile)
        gattrs = {"type":"NXentry" , "name":"shortname" }   ## map of tag attribute types 
        maTn = {"signal":1, "axis":2, "primary":3, "offset":4, 
          "stride":6, "file_time":"12:34", 
          "file_update_time":"12:45", "restricted":12, 
          "ignoreExtraGroups":True, "ignoreExtraFields":False,
          "ignoreExtraAttributes":True, "minOccus":1, "maxOccus":2
        }
        gattrs = dict(gattrs,**(maTn))
        el = EGroup( gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), nx.nxh5.NXGroup)
        self.assertEqual(el.h5Object.name, gattrs["name"])
        self.assertEqual(el.h5Object.nattrs, 14)
        self.assertEqual(el.h5Object.attr("NX_class").value, gattrs["type"])
        self.assertEqual(el.h5Object.attr("NX_class").dtype, "string")
        self.assertEqual(el.h5Object.attr("NX_class").shape, ())
        
        for k in maTn.keys():
            self.assertEqual(el.h5Object.attr(k).value, gattrs[k])
            self.assertEqual(el.h5Object.attr(k).dtype, NTP.nTnp[NTP.aTn[k]])
            self.assertEqual(el.h5Object.attr(k).shape, ())
            

        self._nxFile.close()
        os.remove(self._fname)



    ## default constructor test
    # \brief It tests default settings
    def test_constructor_aTnv(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile( [], None, self._nxFile)
        gattrs = {"type":"NXentry" , "name":"shortname" }   ## map of tag attribute types 
        maTnv = {"vector":[1,2,3,4,5]}
        gattrs = dict(gattrs,**(maTnv))
        el = EGroup( gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        self.assertEqual(type(el.h5Object), nx.nxh5.NXGroup)
        self.assertEqual(el.h5Object.name, gattrs["name"])
        self.assertEqual(el.h5Object.nattrs, 2)
        self.assertEqual(el.h5Object.attr("NX_class").value, gattrs["type"])
        self.assertEqual(el.h5Object.attr("NX_class").dtype, "string")
        self.assertEqual(el.h5Object.attr("NX_class").shape, ())
        
        for k in maTnv.keys():
            for i in range(len(gattrs[k])):
                self.assertEqual(el.h5Object.attr(k).value[i], gattrs[k][i])
            self.assertEqual(el.h5Object.attr(k).dtype, NTP.nTnp[NTP.aTnv[k]])
            self.assertEqual(el.h5Object.attr(k).shape, (len(gattrs[k]),))
            

        self._nxFile.close()
#        os.remove(self._fname)



    ## default store method
    # \brief It tests default settings
    def test_store_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile( [], None, self._nxFile)
        el = EGroup( self._gattrs, eFile)
        self.assertTrue(isinstance(el, Element))
        self.assertTrue(isinstance(el, FElement))
        self.assertTrue(isinstance(el, FElementWithAttr))
        self.assertEqual(el.tagName, "group")
        self.assertEqual(el.content, [])

        el.store()
        self.assertEqual(el.h5Object.name, self._gattrs["name"])
        self.assertEqual(el.h5Object.nattrs, 1)
        self.assertEqual(el.h5Object.attr("NX_class").value, self._gattrs["type"])
#        self.myAssertRaise(ValueError, el.store)
        
        self._nxFile.close()
        os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
