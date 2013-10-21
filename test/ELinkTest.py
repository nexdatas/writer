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
## \file ELinkTest.py
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


try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx


from ndts.FElement import FElement
from ndts.ELink import ELink
from ndts.EField import EField
from ndts.EGroup import EGroup
from ndts.Element import Element
from ndts.H5Elements import EFile
from ndts.Types import NTP, Converters
from ndts.Errors import XMLSettingSyntaxError
from ndts.FetchNameHandler import TNObject

from Checkers import Checker 

#from  xml.sax import SAXParseException

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


## test fixture
class ELinkTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._fname = "test.h5"
        self._nxFile = None
        self._eFile = None        

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"name":"testField","units":"m" }
        self._fattrs2 = {"name":"testField","type":"NX_INT","units":"m" }
        self._gattrs = {"name":"testGroup","type":"NXentry" }
        self._gname = "testGroup"
        self._gtype = "NXentry"
        self._fdname = "testField"
        self._fdtype = "int64"




        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"


        self._sc = Checker(self)

    ## test starter
    # \brief Common set up
    def setUp(self):
        ## file handle
        print "\nsetting up..."        
        print "CHECKER SEED =", self._sc.seed 

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
        eFile = EFile( {}, None, self._nxFile)
        li = ELink({}, eFile)
        self.assertTrue(isinstance(li, Element))
        self.assertTrue(isinstance(li, FElement))
        self.assertEqual(li.tagName, "link")
        self.assertEqual(li.content, [])

        self.assertEqual(li.h5Object, None)
#        self.assertEqual(type(el.h5Object), None)
#        self.assertEqual(el.h5Object.name, self._gattrs["name"])
#        self.assertEqual(el.h5Object.nattrs, 1)
#        self.assertEqual(el.h5Object.attr("NX_class").value, self._gattrs["type"])
#        self.assertEqual(el.h5Object.attr("NX_class").dtype, "string")
#        self.assertEqual(el.h5Object.attr("NX_class").shape, ())
        

        self._nxFile.close()
        os.remove(self._fname)




    ## default constructor test
    # \brief It tests default settings
    def test_createLink_default(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s.h5' % (os.getcwd(), fun )  
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        eFile = EFile( {}, None, self._nxFile)
        fi = EField( self._fattrs, eFile)
        fi.content = ["1 "]
        fi.store()
        gr = EGroup( self._gattrs, eFile)
        gr.store()
        gr2 = EGroup({"type":"NXentry"}, eFile)
        gr2.store()
        gr3 = EGroup({"type":"NXentry", "name":"entry3"}, eFile)
        gr3.store()

        atts1 = {"name":"link1","target":"/NXentry/testField"}
        atts2 = {"name":"link2","target":"/entry:NXentry/testField"}
        atts3 = {"name":"link3","target":"entry3/testField"}
        atts4 = {"name":"link4","target":"/testField"}
        atts5 = {"name":"link5","target":"/testGroup"}
        atts6 = {"name":"link5","target":"/testField"}
        gT1 = TNObject()
        ch  = TNObject("testGroup","NXentry",gT1)
        gT2 = TNObject()
        ch = TNObject("entry3","NXentry",gT2)

        li0 = ELink({}, eFile)
        li1 = ELink(atts1, eFile)
        li2 = ELink(atts2, eFile)
        li3 = ELink(atts3, eFile)
        li4 = ELink(atts4, eFile)
        li5 = ELink(atts5, eFile)
        li6 = ELink(atts6, eFile)

        fi2 = EField( self._fattrs, gr)
        fi2.content = ["2 "]
        fi2.store()

        fi3 = EField( self._fattrs, gr2)
        fi3.content = ["3 "]
        fi3.store()


        fi4 = EField( self._fattrs, gr3)
        fi4.content = ["4 "]
        fi4.store()

        self.assertTrue(isinstance(li1, Element))
        self.assertTrue(isinstance(li1, FElement))
        self.assertEqual(li1.tagName, "link")
        self.assertEqual(li1.content, [])

        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.myAssertRaise(XMLSettingSyntaxError, li1.createLink,TNObject())
        li1.createLink(gT1)
        self.assertEqual(li1.h5Object, None)
        li2.createLink(TNObject())
        self.myAssertRaise(XMLSettingSyntaxError, li3.createLink,TNObject())
        li3.createLink(gT2)
        li4.createLink(TNObject())
        li5.createLink(TNObject())
        self.myAssertRaise(XMLSettingSyntaxError, li5.createLink,TNObject())
        self.myAssertRaise(XMLSettingSyntaxError, li6.createLink,TNObject())
        self.assertEqual(li0.h5Object, None)
        self.assertEqual(li1.h5Object, None)
        self.assertEqual(li2.h5Object, None)
        self.assertEqual(li3.h5Object, None)
        self.assertEqual(li4.h5Object, None)
        self.assertEqual(li5.h5Object, None)
        
        l1 = self._nxFile.open("link1")
        self.assertEqual(l1.read(), fi2.h5Object.read() )
        self.assertEqual(l1.dtype, fi2.h5Object.dtype )
        self.assertEqual(l1.shape, fi2.h5Object.shape )
        self.assertEqual(l1.nattrs, fi2.h5Object.nattrs )
        self.assertEqual(l1.attr("units").value, fi2.h5Object.attr("units").value )
        self.assertEqual(l1.attr("units").dtype, fi2.h5Object.attr("units").dtype )
        self.assertEqual(l1.attr("units").shape, fi2.h5Object.attr("units").shape )

        l2 = self._nxFile.open("link2")
        self.assertEqual(l2.read(), fi3.h5Object.read() )
        self.assertEqual(l2.dtype, fi3.h5Object.dtype )
        self.assertEqual(l2.shape, fi3.h5Object.shape )
        self.assertEqual(l2.nattrs, fi3.h5Object.nattrs )
        self.assertEqual(l2.attr("units").value, fi3.h5Object.attr("units").value )
        self.assertEqual(l2.attr("units").dtype, fi3.h5Object.attr("units").dtype )
        self.assertEqual(l2.attr("units").shape, fi3.h5Object.attr("units").shape )


        l3 = self._nxFile.open("link3")
        self.assertEqual(l3.read(), fi4.h5Object.read() )
        self.assertEqual(l3.dtype, fi4.h5Object.dtype )
        self.assertEqual(l3.shape, fi4.h5Object.shape )
        self.assertEqual(l3.nattrs, fi4.h5Object.nattrs )
        self.assertEqual(l3.attr("units").value, fi4.h5Object.attr("units").value )
        self.assertEqual(l3.attr("units").dtype, fi4.h5Object.attr("units").dtype )
        self.assertEqual(l3.attr("units").shape, fi4.h5Object.attr("units").shape )



        l4 = self._nxFile.open("link4")
        self.assertEqual(l4.read(), fi.h5Object.read() )
        self.assertEqual(l4.dtype, fi.h5Object.dtype )
        self.assertEqual(l4.shape, fi.h5Object.shape )
        self.assertEqual(l4.nattrs, fi.h5Object.nattrs )
        self.assertEqual(l4.attr("units").value, fi.h5Object.attr("units").value )
        self.assertEqual(l4.attr("units").dtype, fi.h5Object.attr("units").dtype )
        self.assertEqual(l4.attr("units").shape, fi.h5Object.attr("units").shape )
        

        l5 = self._nxFile.open("testGroup")
        self.assertEqual(l5.attr("NX_class").value, gr.h5Object.attr("NX_class").value )
        self.assertEqual(l5.attr("NX_class").dtype, gr.h5Object.attr("NX_class").dtype )
        self.assertEqual(l5.attr("NX_class").shape, gr.h5Object.attr("NX_class").shape )
        self.assertEqual(l5.name, gr.h5Object.name )



        self._nxFile.close()
        os.remove(self._fname)




if __name__ == '__main__':
    unittest.main()
