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
import subprocess

import PyTango
import time
from pni.nx.h5 import open_file


## test fixture
class TangoDataServerTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)
        self._new_device_info_writer = PyTango.DbDevInfo()
        self._new_device_info_writer._class = "TangoDataServer"
        self._new_device_info_writer.server = "TangoDataServer/TDWTEST"
        self._new_device_info_writer.name = "testp09/testtdw/testr228"

        self._psub = None


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."
        db = PyTango.Database()
        db.add_device(self._new_device_info_writer)
        db.add_server("TangoDataServer/TDWTEST", self._new_device_info_writer)
        
        if os.path.isfile("../TDS2"):
            self._psub = subprocess.Popen(
                "cd ..; ./TDS2 TDWTEST &",
                stdout = subprocess.PIPE, 
                stderr =  subprocess.PIPE,  shell= True)
        elif os.path.isfile("../TDS"):
            self._psub = subprocess.Popen(
                "cd ..; ./TDS TDWTEST &",stdout =  subprocess.PIPE, 
                stderr =  subprocess.PIPE,  shell= True)
        else:
            self._psub = subprocess.Popen(
                "TDS TDWTEST &",stdout =  subprocess.PIPE, 
                stderr =  subprocess.PIPE , shell= True)
#            raise ErrorValue, "Cannot find the server instance"
        print "waiting for server..."    
        time.sleep(1)

    ## test closer
    # \brief Common tear down
    def tearDown(self): 
        print "tearing down ..."
        db = PyTango.Database()
        db.delete_server(self._new_device_info_writer.server)
        
        output = ""
        pipe = subprocess.Popen(
            "ps -ef | grep 'TangoDataServer.py TDWTEST'", stdout=subprocess.PIPE , shell= True).stdout

        res = pipe.read().split("\n")
        for r in res:
#            print r
            sr = r.split()
            if len(sr)>2:
                 subprocess.call("kill -9 %s" % sr[1],stderr=subprocess.PIPE , shell= True)

        

    ## openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile(self):     
        print "Run: TangoDataServerTest.test_openFile()"
        try:
            fname= '%s/test.h5' % os.getcwd()   
            dp = PyTango.DeviceProxy("testp09/testtdw/testr228")
            #        print 'attributes', dp.attribute_list_query()
            print dp.state()
            self.assertEqual(dp.state(),PyTango.DevState.ON)
            dp.FileName = fname
            dp.OpenFile()
            self.assertEqual(dp.state(),PyTango.DevState.INIT)
            self.assertEqual(dp.TheXMLSettings,"")
            self.assertEqual(dp.TheJSONRecord, "{}")
            dp.CloseFile()
            self.assertEqual(dp.state(),PyTango.DevState.ON)


            # check the created file
            f = open_file(fname,readonly=True)
#            self.assertEqual(f.name, fname)
            self.assertEqual(f.path, fname)
        
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
        fname= '%s/test2.h5' % os.getcwd()   
        xml = """<definition> <group type="NXentry" name="entry"/></definition>"""
        try:
            dp = PyTango.DeviceProxy("testp09/testtdw/testr228")
            #        print 'attributes', dp.attribute_list_query()
            dp.FileName = fname
            self.assertEqual(dp.state(),PyTango.DevState.ON)

            dp.OpenFile()

            self.assertEqual(dp.state(),PyTango.DevState.INIT)

            dp.TheXMLSettings = xml
            self.assertEqual(dp.state(),PyTango.DevState.INIT)


            dp.OpenEntry()
            self.assertEqual(dp.state(),PyTango.DevState.OPEN)

            dp.CloseEntry()
            self.assertEqual(dp.state(),PyTango.DevState.INIT)


            dp.CloseFile()
            self.assertEqual(dp.state(),PyTango.DevState.ON)



           
             # check the created file
            
            f = open_file(fname,readonly=True)
            self.assertEqual(f.path, fname)

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
            pass
#            os.remove(fname)
