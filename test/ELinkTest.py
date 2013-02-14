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


import pni.io.nx.h5 as nx


from ndts.H5Elements import FElement
from ndts.H5Elements import ELink
from ndts.Element import Element
from ndts.H5Elements import EFile
from ndts.Types import NTP, Converters
from ndts.H5Elements import XMLSettingSyntaxError

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

        self._gattrs = {"name":"test","type":"NXentry" }
        self._gname = "testLink"
        self._gtype = "NXentry"


        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"


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
        li = ELink( self._gattrs, eFile)
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




if __name__ == '__main__':
    unittest.main()
