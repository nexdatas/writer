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
## \file TangoDataWriterTest.py
# unittests for TangoDataWriter
#
import unittest
import os
from pni.nx.h5 import open_file

from  xml.sax import SAXParseException

from ndts import TangoDataWriter 
from ndts.TangoDataWriter  import TangoDataWriter 


## test fixture
class TangoDataWriterTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

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
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

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
            except Exception, e:
                error = False
            self.assertTrue(error is not None)
            self.assertEqual(error, True)
                


            tdw.xmlSettings = xml
            try:
                error = None
                tdw.openEntry()
            except SAXParseException,e:
                error = True
            except Exception, e:
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
        print "Run: TangoDataWriterTest.test_scanRecord() "
        fname = "scantest.h5"
        try:
            tdw = TangoDataWriter(fname)
            
            tdw.openNXFile()

            tdw.xmlSettings = self._scanXml
            tdw.openEntry()



            tdw.record('{"data": {"exp_c01":'+str(self._counter[0])+', "p09/mca/exp.02":'\
                           + str(self._mca1)+ '  } }')

            tdw.record('{"data": {"exp_c01":'+str(self._counter[1])+', "p09/mca/exp.02":'\
                           + str(self._mca2)+ '  } }')

            tdw.closeEntry()

            tdw.closeNXFile()
           



             # check the created file
            
            f = open_file(fname,readonly=True)
            self.assertEqual(f.name, fname)
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
            value = cnt.read()
#            value = cnt[:]
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

