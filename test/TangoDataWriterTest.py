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

from  xml.sax import SAXParseException

from ndts import TangoDataWriter 
from ndts.TangoDataWriter  import TangoDataWriter 


## test fixture
class TangoDataWriterTest(unittest.TestCase):

    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."

    ## test closer
    # \brie Common tear down
    def tearDown(self):
        print "\ntearing down ..."

    ## openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile(self):
        print "Run: TangoDataWriterTest.test_openFile() "
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
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlSettings, "")
            self.assertEqual(tdw.json, "{}")
            self.assertTrue(tdw.getNXFile() is None)
            self.assertTrue(tdw.numThreads > 0)
            self.assertTrue(isinstance(tdw.numThreads,(int, long)))
            self.assertTrue(tdw.getNXFile() is None)
            

            # check the created file

            f = open_file(fname,readonly=True)
            self.assertEqual(f.name, fname)

#            print "\nFile attributes:"
            cnt = 0
            for at in f.attributes:
                cnt += 1
#                print at.name,"=",at.value
            self.assertEqual(cnt, f.nattrs)
            self.assertEqual(6, f.nattrs)
#            print ""    

            self.assertEqual(f.attr("file_name").value, fname)
            self.assertTrue(f.attr("NX_class").value,"NXroot")

            self.assertEqual(f.nchildren, 0)

            cnt = 0
            for ch in f.children:
                cnt += 1
            self.assertEqual(cnt, f.nchildren)

            f.close()

        finally:
            os.remove(fname)



    ## openEntry test
    # \brief It tests validation of opening and closing entry in H5 files.
    def test_openEntry(self):
        print "Run: TangoDataWriterTest.test_openEntry() "
        fname = "test.h5"
        xml = """<definition> <group type="NXentry" name="entry"/></definition>"""
        try:
            tdw = TangoDataWriter(fname)
            
            tdw.openNXFile()

            tdw.xmlSettings = xml
            tdw.openEntry()

            tdw.closeEntry()

            self.assertTrue(tdw.getNXFile() is not None)
            self.assertTrue(tdw.getNXFile().valid)
            self.assertFalse(tdw.getNXFile().readonly)
            self.assertEqual(tdw.fileName, fname)
            self.assertNotEqual(tdw.xmlSettings, "")
            self.assertEqual(tdw.json, "{}")
            self.assertTrue(tdw.numThreads > 0)
            self.assertTrue(isinstance(tdw.numThreads,(int, long)))

            tdw.closeNXFile()
           
             # check the created file
            
            f = open_file(fname,readonly=True)
            self.assertEqual(f.name, fname)

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, f.nattrs)

            self.assertEqual(f.attr("file_name").value, fname)
            self.assertTrue(f.attr("NX_class").value,"NXroot")

            self.assertEqual(f.nchildren, 1)

            cnt = 0
            for ch in f.children:
                self.assertTrue(ch.valid)
                self.assertEqual(ch.name,"entry")
                self.assertEqual(ch.nattrs,1)
                cnt += 1
                for at in ch.attributes:
                    self.assertTrue(at.valid)
                    self.assertTrue(hasattr(at.shape,"__iter__"))
                    self.assertEqual(len(at.shape),0)
                    self.assertEqual(at.dtype,"string")
#                    self.assertEqual(at.dtype,"string")
                    self.assertEqual(at.name,"NX_class")
                    self.assertEqual(at.value,"NXentry")
                    
                
            self.assertEqual(cnt, f.nchildren)

            f.close()

        finally:
            os.remove(fname)



    ## openEntry test
    # \brief It tests validation of opening and closing entry in H5 files.
    def test_openEntryWithSAXParseException(self):
        print "Run: TangoDataWriterTest.test_openEntryWithSAXParseException() "
        fname = "test.h5"
        wrongXml = """Ala ma kota."""
        xml = """<definition/>"""
        try:
            tdw = TangoDataWriter(fname)
            
            tdw.openNXFile()

            tdw.xmlSettings = wrongXml
            try:
                error = None
                tdw.openEntry()
            except SAXParseException,e:
                error = True
            except Exception,e:
                error = False
            self.assertTrue(error is not None)
            self.assertEqual(error, True)
                


            tdw.xmlSettings = xml
            try:
                error = None
                tdw.openEntry()
            except SAXParseException,e:
                error = True
            except Exception,e:
                error = False
            self.assertTrue(error is None)
                                
            tdw.closeEntry()

            tdw.closeNXFile()
            

            # check the created file
            
            f = open_file(fname,readonly=True)
            self.assertEqual(f.name, fname)

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, f.nattrs)

            self.assertEqual(f.attr("file_name").value, fname)
            self.assertTrue(f.attr("NX_class").value,"NXroot")

            self.assertEqual(f.nchildren, 0)

            cnt = 0
            for ch in f.children:
                cnt += 1
                
            self.assertEqual(cnt, f.nchildren)

            f.close()



        finally:
            os.remove(fname)
