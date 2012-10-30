#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \file runtest.py
# the unittest runner
#
import unittest
import os
from pni.nx.h5 import open_file


from ndts import TangoDataWriter 
from ndts.TangoDataWriter  import TangoDataWriter 


# test fixture
class TangoDataWriterTest(unittest.TestCase):

    def setUp(self):
        print "setting up..."
        self._tdw = TangoDataWriter("tangodatawritertest.h5")
        self._tdw.openNXFile()

    def tearDown(self):
        print "tearing down ..."
        try:
            self._tdw.closeNXFile()
        finally:
            os.remove("tangodatawritertest.h5")


    def test_creation(self):
        print "Run: TangoDataWriterTest.test_creation() "
        fname = "test.h5"
        try:
            tdw = TangoDataWriter(fname)
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlSettings, "")
            self.assertEqual(tdw.json, "{}")
            self.assertTrue(tdw.getNXFile() is None)
            self.assertTrue(tdw.numThreads > 0)
            self.assertTrue(isinstance(tdw.numThreads,(int, long)))
            
            tdw.openNXFile()
            self.assertTrue(tdw.getNXFile() is not None)
            self.assertTrue(tdw.getNXFile().valid)
            self.assertFalse(tdw.getNXFile().readonly)
            
            tdw.closeNXFile()
            
            self.assertTrue(tdw.getNXFile() is None)
            

            f = open_file(fname,readonly=True)
            self.assertEqual(f.name, fname)

            print "\nFile attributes:"
            cnt = 0
            for at in f.attributes:
                cnt += 1
                print at.name,"=",at.value
            self.assertEqual(cnt, f.nattrs)
            print ""    

            self.assertEqual(f.attr("file_name").value, fname)
            self.assertTrue(f.attr("NX_class").value,"NXroot")

            self.assertEqual(f.nchildren, 0)

            cnt = 0
            for ch in f.children:
                cnt += 1
            self.assertEqual(cnt, f.nchildren)
            print ""    

#            print f.children.valid
            print "Path:" , f.path
            print "Base:", f.base

            f.close()

        finally:
            os.remove(fname)
