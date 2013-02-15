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
## \file DBFieldTagWriterTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import random
import struct
import binascii
import time


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


from pni.io.nx.h5 import open_file
from  xml.sax import SAXParseException

from ndts import TangoDataWriter, Types
from ndts.TangoDataWriter  import TangoDataWriter 
from Checkers import Checker

import MySQLdb


## test fixture
class DBFieldTagWriterTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        try:
            ## random seed
            self.seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            self.seed  = long(time.time() * 256) # use fractional seconds
         
        self.__rnd = random.Random(self.seed)



        self._counter =  [1,-2,6,-8,9,-11]
        self._fcounter =  [1.1,-2.4,6.54,-8.456,9.456,-0.46545]
        self._sc = Checker(self)
        self._mca1 = [[self.__rnd.randint(-100, 100) for e in range(256)] for i in range(3)]
        self._mca2 = [[self.__rnd.randint(0, 100) for e in range(256)] for i in range(3)]
        self._fmca1 = [self._sc.nicePlot(1024, 10) for i in range(4)]
#        self._fmca2 = [(float(e)/(100.+e)) for e in range(2048)]
        self._pco1 = [[[self.__rnd.randint(0, 100) for e1 in range(8)]  for e2 in range(10)] for i in range(3)]
        self._fpco1 = [self._sc.nicePlot2D(20, 30, 5) for i in range(4)]
        self._mydb = None

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        

    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."
        args = {}
        args["db"] = 'tango'
        args["host"] = 'localhost'
        args["read_default_file"] = '/etc/my.cnf'
        self._mydb = MySQLdb.connect(**args)
        print "SEED =", self.seed 
        print "CHECKER SEED =", self._sc.seed 

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."
        self._mydb.close()

    ## opens writer
    # \param fname file name     
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer instance   
    def openWriter(self, fname, xml, json = None):
        tdw = TangoDataWriter(fname)
        tdw.numThreads = 1

        tdw.openNXFile()
        tdw.xmlSettings = xml
        if json:
            tdw.json = json
        tdw.openEntry()
        return tdw

    ## closes writer
    # \param tdw Tango Data Writer instance
    # \param json JSON Record with client settings
    def closeWriter(self, tdw, json = None):
        if json:
            tdw.json = json
        tdw.closeEntry()
        tdw.closeNXFile()

    ## performs one record step
    def record(self, tdw, string):
        tdw.record(string)

    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbScalar(self):
        print "Run: %s.test_dbScalar() " % self.__class__.__name__
        fname= '%s/dbscalar.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <field units="m" name="pid_scalar_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field units="m" name="pid_scalar2_string" type="NX_CHAR">
          <dimensions rank="1" />
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar3_string" type="NX_CHAR">
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field units="m" name="pid_scalar4_string" type="NX_CHAR">
          <dimensions rank="0" />
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field  units="m" name="pid_scalar_uint" type="NX_UINT">
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>



        <field  units="m" name="pid_scalar_int64" type="NX_INT64">
          <strategy mode="STEP"/>
          <dimensions rank="0" />
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar_float64" type="NX_FLOAT64">
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="pid_scalar_float32" type="NX_FLOAT32">
          <dimensions rank="0" /> 
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid2_image_string" type="NX_CHAR" units="m" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="pid3_image_string" type="NX_CHAR" units="m" >
          <dimensions rank="2" />
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="init_pid_scalar_int32" type="NX_INT32">
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="init_pid_scalar_string" type="NX_CHAR">
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="final_pid_scalar_float32" type="NX_FLOAT32">
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="m" name="final_pid_scalar_float64" type="NX_FLOAT64">
          <dimensions rank="0" />
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="final_pid_scalar_string" type="NX_CHAR" units="m" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>

        <field name="final_pid2_scalar_string" type="NX_CHAR" units="m" >
          <dimensions rank="2"/>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>




        <field name="final_pid3_scalar_string" type="NX_CHAR" units="m" >
          <dimensions rank="0"/>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""
        
        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        scalar = str(cursor.fetchone()[0])
        cursor.close()


        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw,'{ }')

        self.closeWriter(tdw)
        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkFieldTree(f, fname , 17)
        self._sc.checkScalarField(det, "pid_scalar_string", "string", "NX_CHAR", [scalar] *3)
        self._sc.checkScalarField(det, "pid_scalar2_string", "string", "NX_CHAR", [scalar] *3)
        self._sc.checkScalarField(det, "pid_scalar3_string", "string", "NX_CHAR", [scalar] *3)
        self._sc.checkScalarField(det, "pid_scalar4_string", "string", "NX_CHAR", [scalar] *3)
        self._sc.checkScalarField(det, "pid_scalar_uint", self._buint, "NX_UINT", [int(scalar)] *3)
        self._sc.checkScalarField(det, "pid_scalar_int64","int64", "NX_INT64", [int(scalar)] *3)
        self._sc.checkScalarField(det, "pid_scalar_float64", "float64", "NX_FLOAT64", [float(scalar)] *3, 
                                  error = 1e-14)
        self._sc.checkScalarField(det, "pid_scalar_float32", "float32", "NX_FLOAT32", [float(scalar)] *3, 
                                  error = 1e-5)
        self._sc.checkScalarField(det, "pid2_image_string", "string", "NX_CHAR", 
                                       [str(scalar)]*3)
        self._sc.checkScalarField(det, "pid3_image_string", "string", "NX_CHAR", 
                                       [str(scalar)]*3)
       

        self._sc.checkSingleScalarField(det, "init_pid_scalar_int32", "int32", "NX_INT32", int(scalar))
        self._sc.checkSingleScalarField(det, "init_pid_scalar_string", "string", "NX_CHAR", scalar)
        self._sc.checkSingleScalarField(det, "final_pid_scalar_float32", "float32", "NX_FLOAT32", 
                                        float(scalar), error = 1e-6)
        self._sc.checkSingleScalarField(det, "final_pid_scalar_float64", "float64", "NX_FLOAT64", 
                                        float(scalar), error = 1e-14)
        self._sc.checkSingleScalarField(det, "final_pid_scalar_string", "string", "NX_CHAR", 
                                        str(scalar))
        self._sc.checkSingleScalarField(det, "final_pid2_scalar_string", "string", "NX_CHAR", 
                                        str(scalar))
        self._sc.checkSingleScalarField(det, "final_pid3_scalar_string", "string", "NX_CHAR", 
                                        str(scalar))








        f.close()
        os.remove(fname)



    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbSpectrum(self):
        print "Run: %s.test_dbSpectrum() " % self.__class__.__name__
        fname= '%s/dbspectrum.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">



        <field units="" name="pid_spectrum_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="10"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_string" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>



        <field units="" name="pid_spectrum_int32" type="NX_UINT32">
          <dimensions rank="1">
            <dim index="1" value="10"/>
          </dimensions>
          <strategy mode="STEP" grows="2"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>



        <field units="" name="pid_spectrum_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="10"/>
          </dimensions>
          <strategy mode="STEP" comporession="true" rate="4" shuffle="true"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>


        <field  units="" name="pid_scalar_int32" type="NX_INT32">
          <dimensions rank="1" />
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>





        <field  units="" name="pid_scalar_int64" type="NX_INT64">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="pid_scalar_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="name_spectrum_string" type="NX_CHAR" units="" >
          <dimensions rank="2" />
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT name FROM device limit 10
            </query>
          </datasource>
        </field>


        <field  units="" name="init_pid_scalar_int64" type="NX_INT64">
          <dimensions rank="1"/>
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="final_pid_scalar_float32" type="NX_FLOAT32">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="init_pid_spectrum_int32" type="NX_INT32">
          <dimensions rank="1" />
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>


        <field  units="" name="final_pid_spectrum_float64" type="NX_FLOAT64">
          <dimensions rank="1">
            <dim index="1" value="10"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>



        <field  units="" name="final_pid_scalar_string" type="NX_CHAR">
          <dimensions rank="1">
            <dim index="1" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field  units="" name="init_pid_spectrum_string" type="NX_CHAR">
          <dimensions rank="1" />
          <strategy mode="INIT"/>
          <datasource name="single_mysql_record_int" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>


        <field name="final_pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>


        <field name="final_pid_spectrum_string" type="NX_CHAR" units="" >
          <dimensions rank="2" />
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>






      </group>
    </group>
  </group>
</definition>
"""
        
        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        scalar = str(cursor.fetchone()[0])
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 10")
        spectrum = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name FROM device limit 10")
        name = cursor.fetchall()
        cursor.close()
        
        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw,'{ }')

        self.closeWriter(tdw)
        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkFieldTree(f, fname , 33)
        self._sc.checkStringSpectrumField(det, "pid_spectrum_string", "string", "NX_CHAR", 
                                          [[str(sub[0]) for sub in spectrum ]]*3)
        self._sc.checkSpectrumField(det, "pid_spectrum_int32", "uint32", "NX_UINT32", 
                                    [[sub[0] for sub in spectrum ]]*3, grows=2)
        self._sc.checkSpectrumField(det, "pid_spectrum_float64", "float64", "NX_FLOAT64", 
                                    [[float(sub[0]) for sub in spectrum ]]*3)
        self._sc.checkSpectrumField(det, "pid_scalar_int64", "int64", "NX_INT64", 
                                    [[int(scalar)] ]*3)
        self._sc.checkSpectrumField(det, "pid_scalar_float64", "float64", "NX_FLOAT64", 
                                    [[float(scalar)] ]*3)
        self._sc.checkStringSpectrumField(det, "name_spectrum_string", "string", "NX_CHAR", 
                                       [[str(sub[0]) for sub in name]]*3)
        self._sc.checkSingleSpectrumField(det, "init_pid_scalar_int64", "int64", "NX_INT64", 
                                          [int(scalar)] )
        self._sc.checkSingleSpectrumField(det, "final_pid_scalar_float32", "float32", "NX_FLOAT32", 
                                          [float(scalar)] )
        self._sc.checkSingleSpectrumField(det, "init_pid_spectrum_int32", "int32", "NX_INT32", 
                                          [sub[0] for sub in spectrum ] )
        self._sc.checkSingleSpectrumField(det, "final_pid_spectrum_float64", "float64", "NX_FLOAT64", 
                                          [sub[0] for sub in spectrum ] )
       

        self._sc.checkSingleStringSpectrumField(det, "init_pid_spectrum_string", "string", "NX_CHAR", 
                                                [str(sub[0]) for sub in spectrum ])
        self._sc.checkSingleStringSpectrumField(det, "final_pid_scalar_string", "string", "NX_CHAR", 
                                                [scalar])
        self._sc.checkSingleStringSpectrumField(det, "final_pid_image_string", "string", "NX_CHAR", 
                                    [str(sub[0]) for sub in spectrum])
        self._sc.checkSingleStringSpectrumField(det, "final_pid_spectrum_string", "string", "NX_CHAR", 
                                    [str(sub[0]) for sub in spectrum])


        self._sc.checkSpectrumField(det, "pid_scalar_int32", "int32", "NX_INT32", 
                                  [[int(scalar)] ]*3)



        f.close()
        os.remove(fname)




    ## scanRecord test
    # \brief It tests recording of simple h5 file
    def test_dbImage(self):
        print "Run: %s.test_dbImage() " % self.__class__.__name__
        fname= '%s/dbimage.h5' % os.getcwd()   
        xml= """<definition>
  <group type="NXentry" name="entry1">
    <group type="NXinstrument" name="instrument">
      <group type="NXdetector" name="detector">

        <field name="name_pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT name, pid FROM device limit 10
            </query>
          </datasource>
        </field>

        <field name="name_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT name FROM device limit 10
            </query>
          </datasource>
        </field>



        <field name="pid_image_string" type="NX_CHAR" units="" >
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>




        <field name="pid_image_int" type="NX_INT" units="" >
          <dimensions rank="2">
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid_image_uint" type="NX_UINT" units="" >
          <dimensions rank="2"/>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="init_pid_spectrum_float64" type="NX_FLOAT64" units="" >
          <dimensions rank="2"/>
          <strategy mode="INIT"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>



        <field name="pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2"> 
            <dim index="1" value="10"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>

        <field name="pid_image_int32" type="NX_INT32" units="" >
          <dimensions rank="2"> 
            <dim index="1" value="10"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" grows="2" compression="true"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>


        <field name="pid_image_int64" type="NX_INT64" units="" >
          <dimensions rank="2"> 
            <dim index="1" value="10"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="STEP" grows="3"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>

        <field name="pid_exported_image_int" type="NX_INT" units="">
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP"  />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 10
            </query>
          </datasource>
        </field>

        <field name="pid_exported_image_uint32" type="NX_UINT32" units="">
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="STEP" compression="true" grows="3" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 10
            </query>
          </datasource>
        </field>

        <field name="final_pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2" />
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>


        <field name="pid_exported_image_float32" type="NX_FLOAT32" units="">
          <dimensions rank="2" />
          <strategy mode="STEP" compression="true" rate="2" shuffle="false" grows="2" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 10
            </query>
          </datasource>
        </field>

        <field name="init_pid_exported_image_int64" type="NX_INT64" units="">
          <dimensions rank="2" />
          <strategy mode="INIT" compression="true" grows="3" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 10
            </query>
          </datasource>
        </field>


        <field name="init_pid_exported_image_string" type="NX_CHAR" units="">
          <dimensions rank="2" />
          <strategy mode="INIT" compression="true" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 10
            </query>
          </datasource>
        </field>


        <field name="pid_spectrum_float32" type="NX_FLOAT32" units="" >
          <dimensions rank="2" />
          <strategy mode="STEP" grows="2"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>



        <field name="final_pid_exported_image_float64" type="NX_FLOAT64" units="">
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="2"/>
          </dimensions>
          <strategy mode="FINAL" compression="true" rate="2" shuffle="false" grows="2" />
          <datasource name="pid_exported" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="IMAGE">
              SELECT pid, exported FROM device limit 10
            </query>
          </datasource>
        </field>



        <field name="final_pid_image_float64" type="NX_FLOAT64" units="" >
          <dimensions rank="2">
            <dim index="1" value="10"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="FINAL"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SPECTRUM">
              SELECT pid FROM device limit 10
            </query>
          </datasource>
        </field>




        <field name="init_pid_image_float" type="NX_FLOAT" units="" >
          <dimensions rank="2" >
            <dim index="1" value="1"/>
            <dim index="2" value="1"/>
          </dimensions>
          <strategy mode="INIT"/>
          <datasource name="mysql_record" type="DB">
            <database dbname="tango" dbtype="MYSQL" hostname="localhost"/>
            <query format="SCALAR">
              SELECT pid FROM device limit 1
            </query>
          </datasource>
        </field>




      </group>
    </group>
  </group>
</definition>
"""

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name, pid FROM device limit 10")
        name_pid = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT name FROM device limit 10")
        name = cursor.fetchall()
        cursor.close()

        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 10")
        pid = cursor.fetchall()
        cursor.close()


        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid, exported FROM device limit 10")
        pid_exported = cursor.fetchall()
        cursor.close()


        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 1")
        scalar = str(cursor.fetchone()[0])
        cursor.close()


        cursor = self._mydb.cursor()
        cursor.execute("SELECT pid FROM device limit 10")
        spectrum = cursor.fetchall()
        cursor.close()

        tdw = self.openWriter(fname, xml)

        for c in range(3):
            self.record(tdw,'{ }')

        self.closeWriter(tdw)
        
        # check the created file
        
        f = open_file(fname,readonly=True)
        det = self._sc.checkFieldTree(f, fname , 57)
        self._sc.checkStringImageField(det, "name_pid_image_string", "string", "NX_CHAR", 
                                       [[[str(it) for it in sub] for sub in name_pid]]*3)
        self._sc.checkStringImageField(det, "name_image_string", "string", "NX_CHAR", 
                                       [[[str(it) for it in sub] for sub in name]]*3)
        self._sc.checkStringImageField(det, "pid_image_string", "string", "NX_CHAR", 
                                       [[[str(it) for it in sub] for sub in pid]]*3)
        self._sc.checkImageField(det, "pid_image_float", self._bfloat, "NX_FLOAT", 
                                       [[[float(it) for it in sub] for sub in pid]]*3)
        self._sc.checkImageField(det, "pid_image_int32", "int32", "NX_INT32", 
                                       [[[int(it) for it in sub] for sub in pid]]*3, grows=2)
        self._sc.checkImageField(det, "pid_image_int", self._bint, "NX_INT", 
                                       [[[int(pid[0][0])]]]*3)
        self._sc.checkImageField(det, "pid_image_int64", "int64", "NX_INT64", 
                                       [[[int(it) for it in sub] for sub in pid]]*3, grows=3)
        self._sc.checkImageField(det, "pid_exported_image_int", self._bint, "NX_INT", 
                                    [pid_exported]*3)
        self._sc.checkImageField(det, "pid_exported_image_uint32", "uint32", "NX_UINT32", 
                                    [pid_exported]*3, grows=3)
        self._sc.checkImageField(det, "pid_exported_image_float32", "float32", "NX_FLOAT32", 
                                    [pid_exported]*3, grows=2, error=1e-6)
        self._sc.checkSingleStringImageField(det, "init_pid_exported_image_string", "string", "NX_CHAR", 
                                    [[str(it) for it in sub] for sub in pid_exported])
        self._sc.checkSingleImageField(det, "init_pid_exported_image_int64", "int64", "NX_INT64", 
                                    pid_exported, grows=3)
        self._sc.checkSingleImageField(det, "final_pid_exported_image_float64", "float64", "NX_FLOAT64", 
                                    pid_exported, grows=2, error=1e-6)
        self._sc.checkSingleImageField(det, "final_pid_image_float64", "float64", "NX_FLOAT64", 
                                    [[float(sub[0])] for sub in pid])
        self._sc.checkSingleImageField(det, "init_pid_image_float", self._bfloat, "NX_FLOAT", 
                                    [[float(pid[0][0])]])



        self._sc.checkImageField(det, "pid_image_uint", self._buint, "NX_UINT", 
                                       [[[int(scalar)]]]*3)
        self._sc.checkSingleImageField(det, "final_pid_image_float", self._bfloat, "NX_FLOAT", 
                                        [[float(scalar)]])




        self._sc.checkSingleImageField(det, "init_pid_spectrum_float64", "float64", "NX_FLOAT64", 
                                    [[float(sub[0])] for sub in spectrum])

        self._sc.checkImageField(det, "pid_spectrum_float32", "float32", "NX_FLOAT32", 
                                       [[[float(sub[0])] for sub in spectrum]]*3, grows=2)

        f.close()
        os.remove(fname)



if __name__ == '__main__':
    unittest.main()
