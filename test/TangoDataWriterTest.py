#!/usr/bin/env python3
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
import sys

from pni.io.nx.h5 import open_file

from  xml.sax import SAXParseException

from nxswriter import TangoDataWriter 
from nxswriter.TangoDataWriter  import TangoDataWriter 
import struct

    

## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

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
      <link target="%s://entry1/instrument/detector/counter1" name="cnt1">
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



        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"


    ## test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")



    ## Exception tester
    # \param exception expected exception
    # \param method called method      
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except exception as e:
            error = True
        self.assertEqual(error, True)



    ## openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "test.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            
            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            
            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            self.assertTrue(tdw.getFile() is None)
            

            # check the created file

            f = open_file(fname,readonly=True)
            f = f.root()

            cnt = 0
            print("ATTR %s %s" % (f.attributes, len(f.attributes)))
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(6, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            os.remove(fname)



    ## openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile_valueerror(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "test.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            
            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            try:
                error = False
                tdw.jsonrecord =  "}"
            except ValueError as e:
                error = True
            self.assertEqual(error, True)

            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            self.assertTrue(tdw.getFile() is None)
            

            # check the created file

            f = open_file(fname,readonly=True)
            f = f.root()

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(6, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            os.remove(fname)




    ## openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFile_typeerror(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "test.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            
            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            try:
                error = False
                tdw.jsonrecord =  1223
            except TypeError as e:
                error = True
            self.assertEqual(error, True)

            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            self.assertTrue(tdw.getFile() is None)
            

            # check the created file

            f = open_file(fname,readonly=True)
            f = f.root()

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(6, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            os.remove(fname)



    ## openFile test
    # \brief It tests validation of opening and closing H5 files.
    def test_openFileDir(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        
        directory = '#nexdatas_test_directoryS#' 
        dirCreated = False
        dirExists = False
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                dirCreated = True
                dirExists = True
            except:
                pass
        else:
             dirExists = True
             

        if dirExists:
            fname = '%s/%s/%s%s.h5' % (os.getcwd(), directory, self.__class__.__name__, fun )  
        else:
            fname = '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )  
            
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            
            tdw.openFile()
            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            
            tdw.closeFile()
            self.assertEqual(tdw.fileName, fname)
            self.assertEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.getFile() is None)
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))
            self.assertTrue(tdw.getFile() is None)
            

            # check the created file

            f = open_file(fname,readonly=True)
            f = f.root()
            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))
            self.assertEqual(6, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            os.remove(fname)
            if dirCreated:
                os.removedirs(directory)

    ## openEntry test
    # \brief It tests validation of opening and closing entry in H5 files.
    def test_openEntry(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "test.h5"
        xml = """<definition> <group type="NXentry" name="entry"/></definition>"""
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            tdw.openFile()

            tdw.xmlsettings = xml
            tdw.openEntry()

            tdw.closeEntry()

            self.assertTrue(tdw.getFile() is not None)
            self.assertTrue(tdw.getFile().is_valid)
            self.assertFalse(tdw.getFile().readonly)
            self.assertEqual(tdw.fileName, fname)
            self.assertNotEqual(tdw.xmlsettings, "")
            self.assertEqual(tdw.jsonrecord, "{}")
            self.assertTrue(tdw.numberOfThreads > 0)
            self.assertTrue(isinstance(tdw.numberOfThreads, int))

            tdw.closeFile()
           
             # check the created file
            
            f = open_file(fname,readonly=True)
            f = f.root()

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")

            self.assertEqual(f.size, 2)

            cnt = 0
            for ch in f:
                self.assertTrue(ch.is_valid)
                cnt += 1
                if ch.name == "entry":
                    self.assertEqual(ch.name,"entry")
                    self.assertEqual(len(ch.attributes),1)
                    for at in ch.attributes:
                        self.assertTrue(at.is_valid)
                        self.assertTrue(hasattr(at.shape,"__iter__"))
                        self.assertEqual(len(at.shape),1)
                        self.assertEqual(at.shape,(1,))
                        self.assertEqual(at.dtype,"string")
                    #                    self.assertEqual(at.dtype,"string")
                        self.assertEqual(at.name,"NX_class")
                        self.assertEqual(at[...],"NXentry")                
                else:
                    self.assertEqual(ch.name,"NexusConfigurationLogs")
                    for c in ch:
                        if c.name == "Nexus__entry__1_XML":
                            self.assertEqual(
                                c.read(), 
                                '<definition> <group type="NXentry" name="entry"/></definition>')
                            print(c.read())
                        else:
                            self.assertEqual(c.name,"python_version")
                            self.assertEqual(c.read(),sys.version)
                            
                    self.assertEqual(len(ch.attributes),1)
                    for at in ch.attributes:
                        self.assertTrue(at.is_valid)
                        self.assertTrue(hasattr(at.shape,"__iter__"))
                        self.assertEqual(len(at.shape),1)
                        self.assertEqual(at.shape,(1,))
                        self.assertEqual(at.dtype,"string")
                    #                    self.assertEqual(at.dtype,"string")
                        self.assertEqual(at.name,"NX_class")
                        self.assertEqual(at[...],"NXcollection")                
                        
                    
                
            self.assertEqual(cnt, f.size)

            f.close()

        finally:
            os.remove(fname)



    ## openEntryWithSAXParseException test
    # \brief It tests validation of opening and closing entry with SAXParseException
    def test_openEntryWithSAXParseException(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "test.h5"
        wrongXml = """Ala ma kota."""
        xml = """<definition/>"""
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname

            tdw.openFile()

            try:
                error = None
                tdw.xmlsettings = wrongXml
            except SAXParseException as e:
                error = True
            except Exception as e:
                error = False
            self.assertTrue(error is not None)
            self.assertEqual(error, True)
                


            try:
                tdw.xmlsettings = xml
                error = None
                tdw.openEntry()
            except SAXParseException as e:
                error = True
            except Exception as e:
                error = False
            self.assertTrue(error is None)
                                
            tdw.closeEntry()

            tdw.closeFile()
            

            # check the created file
            
            f = open_file(fname,readonly=True)
            f = f.root()

            cnt = 0
            for at in f.attributes:
                cnt += 1
            self.assertEqual(cnt, len(f.attributes))

            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")

            self.assertEqual(f.size, 1)

            cnt = 0
            for ch in f:
                cnt += 1
                
            self.assertEqual(cnt, f.size)

            f.close()



        finally:
            os.remove(fname)




    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_scanRecord(self): 
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))
        fname = "scantest.h5"
        try:
            tdw = TangoDataWriter()
            tdw.fileName = fname
            
            tdw.openFile()

            tdw.xmlsettings = self._scanXml % fname
            tdw.openEntry()



            tdw.record('{"data": {"exp_c01":'+str(self._counter[0])+', "p09/mca/exp.02":'\
                           + str(self._mca1)+ '  } }')

            tdw.record('{"data": {"exp_c01":'+str(self._counter[1])+', "p09/mca/exp.02":'\
                           + str(self._mca2)+ '  } }')

            tdw.closeEntry()

            tdw.closeFile()
           



             # check the created file
            
            f = open_file(fname,readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(f.attributes["file_name"][...], fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 2)
            
            en = f.open("entry1")
            self.assertTrue(en.is_valid)
            self.assertEqual(en.name,"entry1")
            self.assertEqual(len(en.attributes),1)
            self.assertEqual(en.size, 2)

            at = en.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at[...],"NXentry")

#            ins = f.open("entry1/instrument:NXinstrument")    #bad exception
#            ins = f.open("entry1/instrument")
            ins = en.open("instrument")
            self.assertTrue(ins.is_valid)
            self.assertEqual(ins.name,"instrument")
            self.assertEqual(len(ins.attributes),2)
            self.assertEqual(ins.size, 1)

            
            at = ins.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at[...],"NXinstrument")


            at = ins.attributes["short_name"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"short_name")
            self.assertEqual(at[...],"scan instrument")


            det = ins.open("detector")
            self.assertTrue(det.is_valid)
            self.assertEqual(det.name,"detector")
            self.assertEqual(len(det.attributes),1)
            self.assertEqual(det.size, 2)
            
            at = det.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at[...],"NXdetector")
            
#            cnt = det.open("counter")              # bad exception
            cnt = det.open("counter1")
            self.assertTrue(cnt.is_valid)
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
                


            self.assertEqual(len(cnt.attributes),3)
            



            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at[...],"NX_FLOAT")


            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at[...],"m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")


            mca = det.open("mca")
            self.assertTrue(mca.is_valid)
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

            self.assertEqual(len(mca.attributes),3)

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at[...],"NX_FLOAT")


            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at[...],"")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            
            dt = en.open("data")
            self.assertTrue(dt.is_valid)
            self.assertEqual(dt.name,"data")
            self.assertEqual(len(dt.attributes),1)
            self.assertEqual(dt.size, 2)

            
            at = dt.attributes["NX_class"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape),1)
            self.assertEqual(at.shape,(1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"NX_class")
            self.assertEqual(at[...],"NXdata")






            cnt = dt.open("cnt1")
            self.assertTrue(cnt.is_valid)
            #            ???
            #            self.assertEqual(cnt.name,"cnt1")
            self.assertEqual(cnt.name,"counter1")
            
            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(cnt.shape), 1)
            self.assertEqual(cnt.shape, (2,))
            self.assertEqual(cnt.dtype, "float64")
            self.assertEqual(cnt.size, 2)
            value = cnt[:]
            for i in range(len(value)):
                self.assertEqual(self._counter[i], value[i])
                


            self.assertEqual(len(cnt.attributes),3)
            



            at = cnt.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at[...],"NX_FLOAT")


            at = cnt.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at[...],"m")

            at = cnt.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype,"string")


            mca = dt.open("data")
            self.assertTrue(mca.is_valid)
            self.assertEqual(mca.name,"data")
            

            self.assertTrue(hasattr(cnt.shape, "__iter__"))
            self.assertEqual(len(mca.shape), 2)
            self.assertEqual(mca.shape, (2,2048))
            self.assertEqual(mca.dtype,  "float64")
            self.assertEqual(mca.size, 4096)
            value = mca.read()
            for j in range(len(value[0])):
                self.assertEqual(self._mca1[i], value[0][i])
            for j in range(len(value[0])):
                self.assertEqual(self._mca2[i], value[1][i])

            self.assertEqual(len(mca.attributes),3)

            at = mca.attributes["type"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"type")
            self.assertEqual(at[...],"NX_FLOAT")


            at = mca.attributes["units"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype,"string")
            self.assertEqual(at.name,"units")
            self.assertEqual(at[...],"")

            at = mca.attributes["nexdatas_source"]
            self.assertTrue(at.is_valid)
            self.assertTrue(hasattr(at.shape,"__iter__"))
            self.assertEqual(len(at.shape), 1)
            self.assertEqual(at.shape, (1,))
            self.assertEqual(at.dtype,"string")

            f.close()

        finally:

            os.remove(fname)
#            pass


if __name__ == '__main__':
    unittest.main()
