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
## \file UTF8decoderTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct

from ndts.DecoderPool import UTF8decoder



## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)




## test fixture
class UTF8decoderTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)



        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"
        self.__name = 'UTF8'

    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."        

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        print "Run: %s.test_constructor() " % self.__class__.__name__
        dc = UTF8decoder()
        self.assertEqual(dc.name, self.__name)
        self.assertEqual(dc.format, None)
        self.assertEqual(dc.dtype, None)





if __name__ == '__main__':
    unittest.main()
