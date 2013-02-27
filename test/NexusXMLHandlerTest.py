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
        ## file handle
        self._nxFile = nx.create_file(self._fname, overwrite=True)
        ## element file objects
        self._eFile = EFile([], None, self._nxFile)

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

        self._nxFile.close()
        os.remove(self._fname)

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
        print "Run: %s.test_constructor() " % self.__class__.__name__
        fname = "test.h5"
        nh = NexusXMLHandler(self._eFile)
        self.assertTrue(isinstance(nh.initPool,ThreadPool))
        self.assertTrue(isinstance(nh.stepPool,ThreadPool))
        self.assertTrue(isinstance(nh.finalPool,ThreadPool))
        self.assertEqual(nh.triggerPools, {})
        self.assertEqual(nh.close(), None)

if __name__ == '__main__':
    unittest.main()
