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
## \file TangoDataServerTest.py
# unittests for TangoDataServer
#
import unittest
import os
import sys
import subprocess

import PyTango
import time
from pni.nx.h5 import open_file
from  xml.sax import SAXParseException


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

        self._scanXml = """
<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <attribute name ="short_name"> scan instrument </attribute> 
      <group type="NXdetector" name="detector">
        <field units="m" type="NX_FLOAT" name="counter1">
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="exp_c01"/>
          </datasource>
        </field>
        <field units="" type="NX_FLOAT" name="mca">
          <dimensions rank="1">
            <dim value="2048" index="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource type="CLIENT">
            <record name="p09/mca/exp.02"/>
          </datasource>
        </field>
      </group>
    </group>
    <group type="NXdata" name="data">
      <link target="/NXentry/NXinstrument/NXdetector/mca" name="data">
        <doc>
          Link to mca in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
      <link target="/NXentry/NXinstrument/NXdetector/counter1" name="counter1">
        <doc>
          Link to counter1 in /NXentry/NXinstrument/NXdetector
        </doc>
      </link>
    </group>
  </group>
</definition>
"""
        self._counter =  [0.1, 0.2]
        self._mca1 = [e*0.1 for e in range(2048)]
        self._mca2 = [(float(e)/(100.+e)) for e in range(2048)]



    ## test starter
    # \brief Common set up of Tango Server
    def setUp(self):
        print "\nsetting up..."
        db = PyTango.Database()
        db.add_device(self._new_device_info_writer)
        db.add_server("TangoDataServer/TDWTEST", self._new_device_info_writer)
        
#        if os.path.isfile("../TDS2"):
#            self._psub = subprocess.Popen(
#                "cd ..; ./TDS2 TDWTEST &",
#                stdout = subprocess.PIPE, 
#                stderr =  subprocess.PIPE,  shell= True)
#        elif os.path.isfile("../TDS"):
        if os.path.isfile("../TDS"):
            self._psub = subprocess.Popen(
                "cd ..; ./TDS TDWTEST &",stdout =  subprocess.PIPE, 
                stderr =  subprocess.PIPE,  shell= True)
        else:
            self._psub = subprocess.Popen(
                "TDS TDWTEST &",stdout =  subprocess.PIPE, 
                stderr =  subprocess.PIPE , shell= True)
#            raise ErrorValue, "Cannot find the server instance"
        print "waiting for server",
#        time.sleep(1)

        found = False
        cnt = 0
        while not found and cnt < 1000:
            try:
                print "\b.",
                time.sleep(0.02)
                dp = PyTango.DeviceProxy(self._new_device_info_writer.name)
                if dp.state() == PyTango.DevState.ON:
                    found = True
            except:    
                found = False
            cnt +=1
        print ""

    ## test closer
    # \brief Common tear down oif Tango Server
    def tearDown(self): 
        print "tearing down ..."
        db = PyTango.Database()
        db.delete_server(self._new_device_info_writer.server)
        
        output = ""
        pipe = subprocess.Popen(
            "ps -ef | grep 'TangoDataServer.py TDWTEST'", stdout=subprocess.PIPE , shell= True).stdout

        res = pipe.read().split("\n")
        for r in res:
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

            self.assertEqual(f.nchildren, 1)

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
        print "Run: TangoDataServerTest.test_openEntry() "
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

            self.assertEqual(f.nchildren, 2)

            cnt = 0
            for ch in f.children:
                self.assertTrue(ch.valid)
                cnt += 1
                if ch.name == "entry":
                    self.assertEqual(ch.name,"entry")
                    self.assertEqual(ch.nattrs,1)
                    for at in ch.attributes:
                        self.assertTrue(at.valid)
                        self.assertTrue(hasattr(at.shape,"__iter__"))
                        self.assertEqual(len(at.shape),0)
                        self.assertEqual(at.dtype,"string")
                    #                    self.assertEqual(at.dtype,"string")
                        self.assertEqual(at.name,"NX_class")
                        self.assertEqual(at.value,"NXentry")
                else:
                    self.assertEqual(ch.name,"NexusConfigurationLogs")
                    self.assertEqual(ch.nattrs,0)

                    
                
            self.assertEqual(cnt, f.nchildren)

            f.close()

        finally:
            os.remove(fname)



    ## openEntryWithSAXParseException test
    # \brief It tests validation of opening and closing entry with SAXParseException
    def test_openEntryWithSAXParseException(self):
        print "Run: TangoDataServerTest.test_openEntryWithSAXParseException() "
        fname= '%s/test2.h5' % os.getcwd()   
        wrongXml = """Ala ma kota."""
        xml = """<definition/>"""
        try:
            dp = PyTango.DeviceProxy("testp09/testtdw/testr228")
            #        print 'attributes', dp.attribute_list_query()
            dp.FileName = fname
            self.assertEqual(dp.state(),PyTango.DevState.ON)

            dp.OpenFile()

            self.assertEqual(dp.state(),PyTango.DevState.INIT)

            dp.TheXMLSettings = wrongXml
            self.assertEqual(dp.state(),PyTango.DevState.INIT)


            try:
                error = None
                dp.OpenEntry()
            except PyTango.DevFailed,e:
                error = True
            except Exception, e: 
                error = False
            self.assertEqual(error, True)
            self.assertTrue(error is not None)
                


            self.assertEqual(dp.state(),PyTango.DevState.INIT)

#            dp.CloseFile()
#            dp.OpenFile()

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
                cnt += 1
                
            self.assertEqual(cnt, f.nchildren)

            f.close()



        finally:
            os.remove(fname)



    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord(self):
        print "Run: TangoDataServerTest.test_scanRecord() "
        fname= '%s/scantest2.h5' % os.getcwd()   
        xml = """<definition> <group type="NXentry" name="entry"/></definition>"""
        try:
            dp = PyTango.DeviceProxy("testp09/testtdw/testr228")
            #        print 'attributes', dp.attribute_list_query()
            dp.FileName = fname
            self.assertEqual(dp.state(),PyTango.DevState.ON)

            dp.OpenFile()

            self.assertEqual(dp.state(),PyTango.DevState.INIT)

            dp.TheXMLSettings = self._scanXml
            self.assertEqual(dp.state(),PyTango.DevState.INIT)


            dp.OpenEntry()
            self.assertEqual(dp.state(),PyTango.DevState.OPEN)

            dp.Record('{"data": {"exp_c01":'+str(self._counter[0])+', "p09/mca/exp.02":'\
                           + str(self._mca1)+ '  } }')
            self.assertEqual(dp.state(),PyTango.DevState.OPEN)
            dp.Record('{"data": {"exp_c01":'+str(self._counter[1])+', "p09/mca/exp.02":'\
                           + str(self._mca2)+ '  } }')


            dp.CloseEntry()
            self.assertEqual(dp.state(),PyTango.DevState.INIT)


            dp.CloseFile()
            self.assertEqual(dp.state(),PyTango.DevState.ON)



           



             # check the created file
            
            f = open_file(fname,readonly=True)
            self.assertEqual(f.path, fname)
            self.assertEqual(6, f.nattrs)
            self.assertEqual(f.attr("file_name").value, fname)
            self.assertTrue(f.attr("NX_class").value,"NXroot")
            self.assertEqual(f.nchildren, 2)
            
            en = f.open("entry1")
            self.assertTrue(en.valid)
            self.assertEqual(en.name,"entry1")
            self.assertEqual(en.nattrs,1)
            self.assertEqual(en.nchildren, 2)

            at = en.attr("NX_class")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at.value,"NXentry")

#            ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.valid)
            self.assertEqual(ins.name,"instrument")
            self.assertEqual(ins.nattrs,2)
            self.assertEqual(ins.nchildren, 1)

            
            at = ins.attr("NX_class")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at.value,"NXinstrument")


            at = ins.attr("short_name")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"short_name")
            self.assertEqual(at.value,"scan instrument")


            det = ins.open("detector")
            self.assertTrue(det.valid)
            self.assertEqual(det.name,"detector")
            self.assertEqual(det.nattrs,1)
            self.assertEqual(det.nchildren, 2)
            
            at = det.attr("NX_class")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at.value,"NXdetector")
            
#            cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.valid)
            self.assertEqual(cnt.name,"counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#            print cnt.read()
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])
                


            self.assertEqual(cnt.nattrs,2)
            



            at = cnt.attr("type")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at.value,"NX_FLOAT")


            at = cnt.attr("units")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at.value,"m")


            mca = det.open("mca")
            self.assertTrue(mca.valid)
            self.assertEqual(mca.name,"mca")
            

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for j in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for j in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(mca.nattrs,2)

            at = mca.attr("type")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at.value,"NX_FLOAT")


            at = mca.attr("units")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at.value,"")

            
            dt = en.open("data")
            self.assertTrue(dt.valid)
            self.assertEqual(dt.name,"data")
            self.assertEqual(dt.nattrs,1)
            self.assertEqual(dt.nchildren, 2)

            
            at = dt.attr("NX_class")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at.value,"NXdata")






            cnt = dt.open("counter1")
            self.assertTrue(cnt.valid)
            self.assertEqual(cnt.name,"counter1")
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
#            print cnt.read()
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])
                


            self.assertEqual(cnt.nattrs,2)
            



            at = cnt.attr("type")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at.value,"NX_FLOAT")


            at = cnt.attr("units")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at.value,"m")


            mca = dt.open("data")
            self.assertTrue(mca.valid)
            self.assertEqual(mca.name,"data")
            

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype, "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for j in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for j in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(mca.nattrs,2)

            at = mca.attr("type")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at.value,"NX_FLOAT")


            at = mca.attr("units")
            self.assertTrue(at.valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),0)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at.value,"")

            f.close()

        finally:

            os.remove(fname)
#            pass
