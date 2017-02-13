#!/usr/bin/env python
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
## \file runtest.py
# the unittest runner
#

import os 
import unittest

import TangoDataWriterTest
import ClientFieldTagWriterTest
import XMLFieldTagWriterTest
import NexusXMLHandlerTest
import ElementTest
import FElementTest
import FElementH5PYTest
import FElementWithAttrTest
import FElementWithAttrH5PYTest
import EStrategyTest
import EFieldTest
import EFieldReshapeTest
import EGroupTest
import ELinkTest
import EAttributeTest
import EFileTest
import EDocTest
import ESymbolTest
import EDimensionsTest
import EDimTest
import ConvertersTest
import NTPTest
import ErrorsTest
import DataSourceTest
import ClientSourceTest
import PyEvalSourceTest
import DBaseSourceTest
import DataSourcePoolTest
import DataSourceFactoryTest
import DataSourceDecodersTest
import UTF8decoderTest
import UINT32decoderTest
import VDEOdecoderTest
import DecoderPoolTest
import DataHolderTest
import ElementThreadTest
import ThreadPoolTest
import FetchNameHandlerTest
import InnerXMLParserTest
import TNObjectTest
import TgDeviceTest
import StreamsTest
import FileWriterTest
import PNIWriterTest
import H5PYWriterTest

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
    ## connection arguments to MYSQL DB
    args = {}
    args["db"] = 'tango'
    args["host"] = 'localhost'
    args["read_default_file"] = '/etc/my.cnf'
    ## inscance of MySQLdb
    mydb = MySQLdb.connect(**args)
    mydb.close()
    DB_AVAILABLE.append("MYSQL")
except:
    try:
        import MySQLdb    
        from os.path import expanduser
        home = expanduser("~")
        ## connection arguments to MYSQL DB
        args2 = {'host': u'localhost', 'db': u'tango', 
                'read_default_file': u'%s/.my.cnf' % home, 'use_unicode': True}
        ## inscance of MySQLdb
        mydb = MySQLdb.connect(**args2)
        mydb.close()
        DB_AVAILABLE.append("MYSQL")
        
    except ImportError, e:
        print "MYSQL not available: %s" % e
    except Exception, e:
        print "MYSQL not available: %s" % e
    except:
        print "MYSQL not available"


try:
    import psycopg2
    ## connection arguments to PGSQL DB
    args = {}
    args["database"] = 'mydb'
    ## inscance of psycog2
    pgdb = psycopg2.connect(**args)
    pgdb.close()
    DB_AVAILABLE.append("PGSQL")
except ImportError, e:
    print "PGSQL not available: %s" % e
except Exception,e:
    print "PGSQL not available: %s" % e
except:
    print "PGSQL not available"



try:
    import cx_Oracle
    ## pwd
    passwd = open('%s/pwd' % os.path.dirname(ElementTest.__file__)).read()[:-1]

    ## connection arguments to ORACLE DB
    args = {}
    args["dsn"] = """(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=dbsrv01.desy.de)(PORT=1521))(LOAD_BALANCE=yes)(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=desy_db.desy.de)(FAILOVER_MODE=(TYPE=NONE)(METHOD=BASIC)(RETRIES=180)(DELAY=5))))"""
    args["user"] = "read"
    args["password"] = passwd
    ## inscance of cx_Oracle
    ordb = cx_Oracle.connect(**args)
    ordb.close()
    DB_AVAILABLE.append("ORACLE")
except ImportError, e:
    print "ORACLE not available: %s" % e
except Exception,e:
    print "ORACLE not available: %s" % e
except:
    print "ORACLE not available"
    

if "MYSQL" in DB_AVAILABLE:
    import DBFieldTagWriterTest
    import MYSQLSourceTest

if "PGSQL" in DB_AVAILABLE:
    import PGSQLSourceTest

if "ORACLE" in DB_AVAILABLE:
    import ORACLESourceTest

if PYTANGO_AVAILABLE:
    import TangoFieldTagWriterTest
    import NXSDataWriterTest
    import ClientFieldTagServerTest
    import XMLFieldTagServerTest
    import TangoFieldTagServerTest
    import ClientFieldTagAsynchTest
    import XMLFieldTagAsynchTest
    import TangoFieldTagAsynchTest
    import TangoSourceTest
    import TgMemberTest
    import TgGroupTest
    import ProxyToolsTest
    import PyEvalTangoSourceTest
    if "MYSQL" in DB_AVAILABLE:
        import DBFieldTagServerTest
        import DBFieldTagAsynchTest

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
        unittest.defaultTestLoader.loadTestsFromModule(FileWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(PNIWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(H5PYWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(StreamsTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EStrategyTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FElementTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FElementH5PYTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FElementWithAttrTest) )
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FElementWithAttrH5PYTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EFieldTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EFieldReshapeTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EGroupTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ELinkTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EAttributeTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EFileTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EDocTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ESymbolTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EDimensionsTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(EDimTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ConvertersTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(NTPTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ErrorsTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(NexusXMLHandlerTest) )
    
    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(TangoDataWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ClientFieldTagWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(XMLFieldTagWriterTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ClientSourceTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(PyEvalSourceTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DBaseSourceTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourcePoolTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceFactoryTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(UTF8decoderTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(UINT32decoderTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(VDEOdecoderTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DecoderPoolTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataHolderTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ElementThreadTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(DataSourceDecodersTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(ThreadPoolTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(FetchNameHandlerTest) )


    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(InnerXMLParserTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(TNObjectTest) )

    suite.addTests(
        unittest.defaultTestLoader.loadTestsFromModule(TgDeviceTest) )

    if "MYSQL" in DB_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(DBFieldTagWriterTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(MYSQLSourceTest) )


    if "PGSQL" in DB_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(PGSQLSourceTest) )

    if "ORACLE" in DB_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ORACLESourceTest) )

    if PYTANGO_AVAILABLE:
        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoSourceTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TgMemberTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TgGroupTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ProxyToolsTest) )


        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(NXSDataWriterTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ClientFieldTagServerTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(XMLFieldTagServerTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(ClientFieldTagAsynchTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(XMLFieldTagAsynchTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoFieldTagWriterTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoFieldTagServerTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(TangoFieldTagAsynchTest) )

        suite.addTests(
            unittest.defaultTestLoader.loadTestsFromModule(PyEvalTangoSourceTest) )



        if "MYSQL" in DB_AVAILABLE:
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(DBFieldTagServerTest) )
            suite.addTests(
                unittest.defaultTestLoader.loadTestsFromModule(DBFieldTagAsynchTest) )


    
    ## test runner
    runner = unittest.TextTestRunner()
    ## test result
    result = runner.run(suite)

 #   if ts:
 #       ts.tearDown()

if __name__ == "__main__":
    main()
