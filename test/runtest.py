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
## \file runtest.py
# the unittest runner
#


try:
    import PyTango
    ## if module PyTango avalable
    PYTANGO_AVAILABLE = True
except ImportError, e:
    PYTANGO_AVAILABLE = False
    print "PyTango is not available: %s" % e
    
## list of available databases
DB_AVAILABLE = []
    
try:
    import MySQLdb
    args = {}
    args["db"] = 'tango'
    args["host"] = 'localhost'
    args["read_default_file"] = '/etc/my.cnf'
    mydb = MySQLdb.connect(**args)
    mydb.close()
    DB_AVAILABLE.append("MYSQL")
except ImportError, e:
    print "MYSQL not available: %s" % e
except:
    print "MYSQL not available"
    

import unittest

import TangoDataWriterTest
import ClientFieldTagWriterTest
import XMLFieldTagWriterTest
import TangoFieldTagWriterTest
import NexusXMLHandlerTest
import ElementTest
import FElementTest
import FElementWithAttrTest
import EStrategyTest

if "MYSQL" in DB_AVAILABLE:
    import DBFieldTagWriterTest

if PYTANGO_AVAILABLE:
    import TangoDataServerTest
    import ClientFieldTagServerTest
    import XMLFieldTagServerTest
    import TangoFieldTagServerTest
    if "MYSQL" in DB_AVAILABLE:
        import DBFieldTagServerTest

#import TestServerSetUp

## main function
def main():




    ## test server    
    ts = None    
    
    ## test suit
    suite = unittest.TestSuite()

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ElementTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EStrategyTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FElementTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FElementWithAttrTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(NexusXMLHandlerTest) )
    
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(TangoDataWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ClientFieldTagWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(XMLFieldTagWriterTest) )

    if "MYSQL" in DB_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(DBFieldTagWriterTest) )

    if PYTANGO_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoDataServerTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ClientFieldTagServerTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(XMLFieldTagServerTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoFieldTagWriterTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoFieldTagServerTest) )

        if "MYSQL" in DB_AVAILABLE:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(DBFieldTagServerTest) )

    
    ## test runner
    runner = unittest.TextTestRunner()
    ## test result
    result = runner.run(suite)

 #   if ts:
 #       ts.tearDown()

if __name__ == "__main__":
    main()
