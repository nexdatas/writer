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
import TangoDataWriterTest
import TangoDataServerTest
import FieldTagWriterTest
import FieldTagServerTest

## main function
def main():

    try:
        import PyTango
    ## if module PyTango avalable
        PYTANGO_AVAILABLE = True
    except ImportError, e:
        PYTANGO_AVAILABLE = False
        print "PyTango is not available: %s" % e

    ## test suit
    suite = unittest.TestSuite()
    
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(TangoDataWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FieldTagWriterTest) )

    if PYTANGO_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoDataServerTest) )

    if PYTANGO_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(FieldTagServerTest) )

    
    ## test runner
    runner = unittest.TextTestRunner()
    ## test result
    result = runner.run(suite)

if __name__ == "__main__":
    main()
