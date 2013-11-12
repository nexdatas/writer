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
## \file DBFieldTagAsynchTest.py
# unittests for field Tags running Tango Server inm asynchronous mode
#

import unittest
import os
import PyTango
import time

import ServerSetUp
import DBFieldTagWriterTest
from ProxyHelper import ProxyHelper

## test fixture
class DBFieldTagAsynchTest(DBFieldTagWriterTest.DBFieldTagWriterTest):
    ## server counter
    serverCounter = 0

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        DBFieldTagWriterTest.DBFieldTagWriterTest.__init__(self, methodName)

        DBFieldTagAsynchTest.serverCounter += 1
        sins = self.__class__.__name__+"%s" % DBFieldTagAsynchTest.serverCounter
        self._sv = ServerSetUp.ServerSetUp("testp09/testtdw/"+ sins, sins)

#        self._counter =  [1, 2]
#        self._fcounter =  [1.1,-2.4,6.54,-8.456,9.456,-0.46545]



    ## test starter
    # \brief Common set up of Tango Server
    def setUp(self):
        DBFieldTagWriterTest.DBFieldTagWriterTest.setUp(self)
        self._sv.setUp()
        print "SEED =", self.seed 
        print "CHECKER SEED =", self._sc.seed 


    ## test closer
    # \brief Common tear down oif Tango Server
    def tearDown(self): 
        DBFieldTagWriterTest.DBFieldTagWriterTest.tearDown(self)
        self._sv.tearDown()

            
        
    ## opens writer
    # \param fname file name     
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer proxy instance
    def openWriter(self, fname, xml, json = None):
        tdw = PyTango.DeviceProxy(self._sv.new_device_info_writer.name)
        self.assertTrue(ProxyHelper.wait(tdw, 10000))
        tdw.FileName = fname
        self.assertEqual(tdw.state(), PyTango.DevState.ON)
        
        tdw.OpenFile()
        
        self.assertEqual(tdw.state(), PyTango.DevState.OPEN)
        
        tdw.TheXMLSettings = xml
        self.assertEqual(tdw.state(), PyTango.DevState.OPEN)
        if json:
            tdw.TheJSONRecord = json
        self.assertEqual(tdw.state(), PyTango.DevState.OPEN)
        tdw.OpenEntryAsynch()
        self.assertTrue(ProxyHelper.wait(tdw, 10000))
        self.assertEqual(tdw.state(), PyTango.DevState.EXTRACT)
        return tdw


    ## closes writer
    # \param tdw Tango Data Writer proxy instance
    # \param json JSON Record with client settings
    def closeWriter(self, tdw, json = None):
        self.assertEqual(tdw.state(), PyTango.DevState.EXTRACT)

        if json:
            tdw.TheJSONRecord = json
        self.assertEqual(tdw.state(), PyTango.DevState.EXTRACT)
        tdw.CloseEntryAsynch()
        self.assertTrue(ProxyHelper.wait(tdw, 10000))
        self.assertEqual(tdw.state(), PyTango.DevState.OPEN)
        
        tdw.CloseFile()
        self.assertEqual(tdw.state(), PyTango.DevState.ON)
                



    ## performs one record step
    def record(self, tdw, string):
        self.assertEqual(tdw.state(), PyTango.DevState.EXTRACT)
        tdw.RecordAsynch(string)
        self.assertTrue(ProxyHelper.wait(tdw, 10000))
        self.assertEqual(tdw.state(), PyTango.DevState.EXTRACT)


if __name__ == '__main__':
    unittest.main()

