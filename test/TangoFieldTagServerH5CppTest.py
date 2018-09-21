#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
# \package test nexdatas
# \file TangoFieldTagServerH5CppTest.py
# unittests for field Tags running Tango Server
#
import unittest
import PyTango


import ServerSetUp
import TangoFieldTagWriterH5CppTest
from ProxyHelper import ProxyHelper

# test fixture


class TangoFieldTagServerH5CppTest(
        TangoFieldTagWriterH5CppTest.TangoFieldTagWriterH5CppTest):
    # server counter
    serverCounter = 0

    # constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        TangoFieldTagWriterH5CppTest.TangoFieldTagWriterH5CppTest.__init__(
            self, methodName)
        unittest.TestCase.__init__(self, methodName)

        TangoFieldTagServerH5CppTest.serverCounter += 1
        sins = self.__class__.__name__ + \
            "%s" % TangoFieldTagServerH5CppTest.serverCounter
        self._sv = ServerSetUp.ServerSetUp("testp09/testtdw/" + sins, sins)

        self.__status = {
            PyTango.DevState.OFF: "Not Initialized",
            PyTango.DevState.ON: "Ready",
            PyTango.DevState.OPEN: "File Open",
            PyTango.DevState.EXTRACT: "Entry Open",
            PyTango.DevState.RUNNING: "Writing ...",
            PyTango.DevState.FAULT: "Error",
        }

        self._dbhost = None
        self._dbport = None

    # test starter
    # \brief Common set up
    def setUp(self):
        self._sv.setUp()
        self._simps.setUp()
        self._dbhost = self._simps.dp.get_db_host()
        self._dbport = self._simps.dp.get_db_port()
        print("SEED = %s" % self.seed)
        print("CHECKER SEED = %s" % self._sc.seed)

    # test closer
    # \brief Common tear down
    def tearDown(self):
        self._simps.tearDown()
        self._sv.tearDown()

    def setProp(self, rc, name, value):
        db = PyTango.Database()
        name = "" + name[0].upper() + name[1:]
        db.put_device_property(
            self._sv.new_device_info_writer.name,
            {name: value})
        rc.Init()

    # opens writer
    # \param fname file name
    # \param xml XML settings
    # \param json JSON Record with client settings
    # \returns Tango Data Writer proxy instance
    def openWriter(self, fname, xml, json=None):
        tdw = PyTango.DeviceProxy(self._sv.new_device_info_writer.name)
        self.assertTrue(ProxyHelper.wait(tdw, 10000))
        self.setProp(tdw, "writer", "h5cpp")
        tdw.FileName = fname
        self.assertEqual(tdw.state(), PyTango.DevState.ON)
        self.assertEqual(tdw.status(), self.__status[tdw.state()])

        tdw.OpenFile()

        self.assertEqual(tdw.state(), PyTango.DevState.OPEN)
        self.assertEqual(tdw.status(), self.__status[tdw.state()])

        tdw.XMLSettings = xml
        self.assertEqual(tdw.state(), PyTango.DevState.OPEN)
        self.assertEqual(tdw.status(), self.__status[tdw.state()])
        if json:
            tdw.JSONRecord = json
        tdw.OpenEntry()
        self.assertEqual(tdw.state(), PyTango.DevState.EXTRACT)
        self.assertEqual(tdw.status(), self.__status[tdw.state()])
        return tdw

    # closes writer
    # \param tdw Tango Data Writer proxy instance
    # \param json JSON Record with client settings
    def closeWriter(self, tdw, json=None):
        self.assertEqual(tdw.state(), PyTango.DevState.EXTRACT)

        if json:
            tdw.JSONRecord = json
        tdw.CloseEntry()
        self.assertEqual(tdw.state(), PyTango.DevState.OPEN)
        self.assertEqual(tdw.status(), self.__status[tdw.state()])

        tdw.CloseFile()
        self.assertEqual(tdw.state(), PyTango.DevState.ON)
        self.assertEqual(tdw.status(), self.__status[tdw.state()])

    # performs one record step
    def record(self, tdw, string):
        tdw.Record(string)


if __name__ == '__main__':
    unittest.main()
