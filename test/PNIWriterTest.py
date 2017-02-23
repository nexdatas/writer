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
## \package test nexdatas
## \file ElementTest.py
# unittests for field Tags running Tango Server
#
import unittest
import os
import sys
import subprocess
import struct
import random
import binascii
import string

import nxswriter.FileWriter as FileWriter
import nxswriter.PNIWriter as PNIWriter

try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx


## if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)

class testwriter(object):
    def __init__(self):
        self.commands = []
        self.params = []
        self.result = None

    def open_file(self, filename, readonly=False):
        """ open the new file
        """
        self.commands.append("open_file")
        self.params.append([filename, readonly])
        return self.result


    def create_file(self,filename, overwrite=False):
        """ create a new file
        """
        self.commands.append("create_file")
        self.params.append([filename, overwrite])
        return self.result


    def link(self,target, parent, name):
        """ create link
        """
        self.commands.append("link")
        self.params.append([target, parent, name])
        return self.result


    def deflate_filter(self):
        self.commands.append("deflate_filter")
        self.params.append([])
        return self.result



## test fixture
class PNIWriterTest(unittest.TestCase):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        try:
            self.__seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            self.__seed  = long(time.time() * 256)
#        self.__seed =241361343400098333007607831038323262554

        self.__rnd = random.Random(self.__seed)


    ## test starter
    # \brief Common set up
    def setUp(self):
        print "\nsetting up..."
        print "SEED =", self.__seed

    ## test closer
    # \brief Common tear down
    def tearDown(self):
        print "tearing down ..."

    ## Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error =  False
            method(*args, **kwargs)
        except exception, e:
            error = True
        self.assertEqual(error, True)


    ## constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        w = "weerew"
        el = FileWriter.FTObject(w)

        self.assertEqual(el.h5object, w)

    ## default createfile test
    # \brief It tests default settings
    def test_default_createfile(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )

        try:
            fl = PNIWriter.create_file(self._fname)
            fl.close()
            fl = PNIWriter.create_file(self._fname, True)
            fl.close()

            fl = nx.open_file(self._fname, readonly=True)
            f = fl.root()
            self.assertEqual(6, len(f.attributes))
            for at in f.attributes:
                print at.name , at.read() , at.dtype
                at.close()
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 0)
            f.close()
            fl.close()

            fl = PNIWriter.open_file(self._fname, readonly=True)
            f = fl.root()
            self.assertEqual(6, len(f.attributes))
            atts = []
            for at in f.attributes:
                print at
                print at.name , at.read() , at.dtype
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 0)
            fl.close()

            fl.reopen()
            self.assertEqual(6, len(f.attributes))
            atts = []
            for at in f.attributes:
                print at
                print at.name , at.read() , at.dtype
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 0)
            fl.close()

            self.myAssertRaise(
                Exception, PNIWriter.create_file, self._fname)

            self.myAssertRaise(
                Exception, PNIWriter.create_file, self._fname,
                False)

            fl2 = PNIWriter.create_file(self._fname, overwrite=True)
            fl2.close()
        finally:
            os.remove(self._fname)

    ## default createfile test
    # \brief It tests default settings
    def test_pnifile(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )

        try:
            overwrite = False
            nxfl = nx.create_file(self._fname, overwrite)
            fl = PNIWriter.PNIFile(nxfl, self._fname)
            self.assertTrue(
                isinstance(fl, FileWriter.FTFile))

            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, nx._nxh5.nxfile))
            self.assertEqual(fl.parent, None)

            rt = fl.root()
            fl.flush()
            self.assertEqual(
                fl.h5object.root().filename,
                rt.h5object.filename)
            self.assertEqual(
                fl.h5object.root().name,
                rt.h5object.name)
            self.assertEqual(
                fl.h5object.root().path,
                rt.h5object.path)
            self.assertEqual(
                len(fl.h5object.root().attributes),
                len(rt.h5object.attributes))
            self.assertEqual(fl.is_valid, True)
            self.assertEqual(fl.h5object.is_valid, True)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.h5object.readonly, False)
            fl.close()
            self.assertEqual(fl.is_valid, False)
            self.assertEqual(fl.h5object.is_valid, False)

            fl.reopen()
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, nx._nxh5.nxfile))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.h5object.readonly, False)

            fl.close()

            fl.reopen(True)
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, nx._nxh5.nxfile))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, True)
            self.assertEqual(fl.h5object.readonly, True)

            fl.close()
            
            self.myAssertRaise(
                Exception, fl.reopen, True, True)
            self.myAssertRaise(
                Exception, fl.reopen, False, True)

            
            fl = PNIWriter.open_file(self._fname, readonly=True)
            f = fl.root()
            self.assertEqual(6, len(f.attributes))
            atts = []
            for at in f.attributes:
                print at.name, at.read(), at.dtype
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(
                f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 0)
            fl.close()

        finally:
            os.remove(self._fname)

    ## default createfile test
    # \brief It tests default settings
    def test_pnigroup(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)

        try:
            overwrite = False
            FileWriter.writer = PNIWriter
            fl = FileWriter.create_file(self._fname)

            rt = fl.root()
            nt = rt.create_group("notype")
            entry = rt.create_group("entry12345", "NXentry")
            ins = entry.create_group("instrument", "NXinstrument")
            ins = entry.create_group("detector", "NXdetector")
            dt = entry.create_group("data", "NXdata")
            strscalar = entry.create_field("strscalar", "string")
            floatscalar = entry.create_field("floatscalar", "float64")
            intscalar = entry.create_field("intscalar", "uint64")
            strspec = ins.create_field("strspec", "string", [10], [6])
            floatspec = ins.create_field("floatspec", "float32", [20], [16])
            intspec = ins.create_field("intspec", "int64", [30], [5])
            strimage = dt.create_field("strimage", "string", [2,2], [2,1])
            floatimage = dt.create_field("floatimage", "float64", [20,10], [10, 10])
            intimage = dt.create_field("intimage", "uint32", [0, 30], [1, 30])
            strvec = dt.create_field("strvec", "string", [0,2,2], [1,2,2])
            floatvec = dt.create_field("floatvec", "float64", [1, 20,10], [1, 10, 10])
            intvec = dt.create_field("intvec", "uint32", [0, 2, 30], [1, 2, 30])
            ## add links, attributes and filters, no chunk
            
            print dir(rt)

            self.assertTrue(
                isinstance(rt, PNIWriter.PNIGroup))
            self.assertEqual(rt.name, "/")
            self.assertEqual(rt.path, "/")
            self.assertEqual(
                len(fl.h5object.root().attributes),
                len(rt.h5object.attributes))
            attr = rt.attributes
            self.assertTrue(
                isinstance(attr, PNIWriter.PNIAttributeManager))
            self.assertEqual(
                fl.h5object.root().path,
                rt.h5object.path)
            self.assertEqual(rt.is_valid, True)
            self.assertEqual(rt.h5object.is_valid, True)
            self.assertEqual(rt.parent, fl)
            self.assertEqual(rt.exists("entry12345"), True)
            self.assertEqual(rt.exists("strument"), False)
            
            fl.flush()
            self.assertEqual(
                fl.h5object.root().filename,
                rt.h5object.filename)
            self.assertEqual(
                fl.h5object.root().name,
                rt.h5object.name)
            self.assertEqual(
                fl.h5object.root().path,
                rt.h5object.path)
            self.assertEqual(fl.is_valid, True)
            self.assertEqual(fl.h5object.is_valid, True)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.h5object.readonly, False)
            fl.close()
            self.assertEqual(fl.is_valid, False)
            self.assertEqual(fl.h5object.is_valid, False)

            fl.reopen()
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, nx._nxh5.nxfile))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.h5object.readonly, False)

            fl.close()

            fl.reopen(True)
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, nx._nxh5.nxfile))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, True)
            self.assertEqual(fl.h5object.readonly, True)

            fl.close()
            
            self.myAssertRaise(
                Exception, fl.reopen, True, True)
            self.myAssertRaise(
                Exception, fl.reopen, False, True)

            
            fl = PNIWriter.open_file(self._fname, readonly=True)
            f = fl.root()
            self.assertEqual(6, len(f.attributes))
            atts = []
            for at in f.attributes:
                print at.name, at.read(), at.dtype
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(
                f.attributes["NX_class"][...], "NXroot")
            self.assertEqual(f.size, 2)
            fl.close()

        finally:
            os.remove(self._fname)


if __name__ == '__main__':
    unittest.main()
