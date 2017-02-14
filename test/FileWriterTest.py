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
import nxswriter.H5PYWriter as H5PYWriter

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
class FileWriterTest(unittest.TestCase):

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

        self.assertEqual(el.getobject(), w)

    ## test
    # \brief It tests default settings
    def test_openfile(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        tw = testwriter()
        FileWriter.writer = tw
        for _ in range(10):
            res = self.__rnd.randint(1, 10)
            tw.result = res
            chars = string.ascii_uppercase + string.digits
            fn = ''.join(self.__rnd.choice(chars) for _ in range(res))
            tres = FileWriter.open_file(fn)
            self.assertEqual(tres, res)
            self.assertEqual(tw.commands[-1], "open_file")
            self.assertEqual(tw.params[-1], [fn, False])
        for _ in range(10):
            res = self.__rnd.randint(1, 10)
            tw.result = res
            chars = string.ascii_uppercase + string.digits
            fn = ''.join(self.__rnd.choice(chars) for _ in range(res))
            rb =  bool(self.__rnd.randint(0,1))
            tres = FileWriter.open_file(fn, rb)
            self.assertEqual(tres, res)
            self.assertEqual(tw.commands[-1], "open_file")
            self.assertEqual(tw.params[-1], [fn, rb])

    ## test
    # \brief It tests default settings
    def test_createfile(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        tw = testwriter()
        FileWriter.writer = tw
        for _ in range(10):
            res = self.__rnd.randint(1, 10)
            tw.result = res
            chars = string.ascii_uppercase + string.digits
            fn = ''.join(self.__rnd.choice(chars) for _ in range(res))
            tres = FileWriter.create_file(fn)
            self.assertEqual(tres, res)
            self.assertEqual(tw.commands[-1], "create_file")
            self.assertEqual(tw.params[-1], [fn, False])
        for _ in range(10):
            res = self.__rnd.randint(1, 10)
            tw.result = res
            chars = string.ascii_uppercase + string.digits
            fn = ''.join(self.__rnd.choice(chars) for _ in range(res))
            rb =  bool(self.__rnd.randint(0,1))
            tres = FileWriter.create_file(fn, rb)
            self.assertEqual(tres, res)
            self.assertEqual(tw.commands[-1], "create_file")
            self.assertEqual(tw.params[-1], [fn, rb])

    ## test
    # \brief It tests default settings
    def test_link(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        tw = testwriter()
        FileWriter.writer = tw
        for _ in range(10):
            res = self.__rnd.randint(1, 10)
            tw.result = res
            chars = string.ascii_uppercase + string.digits
            fn = ''.join(self.__rnd.choice(chars) for _ in range(res))
            fn2 = ''.join(self.__rnd.choice(chars) for _ in range(res*2))
            fn3 = ''.join(self.__rnd.choice(chars) for _ in range(res*3))
            tres = FileWriter.link(fn, fn2, fn3)
            self.assertEqual(tres, res)
            self.assertEqual(tw.commands[-1], "link")
            self.assertEqual(tw.params[-1], [fn, fn2, fn3])
            self.assertEqual(tres, res)

    ## test
    # \brief It tests default settings
    def test_deflate_filter(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        tw = testwriter()
        FileWriter.writer = tw
        for _ in range(10):
            res = self.__rnd.randint(1, 10)
            tw.result = res
            tres = FileWriter.deflate_filter()
            self.assertEqual(tres, res)
            self.assertEqual(tw.commands[-1], "deflate_filter")
            self.assertEqual(tw.params[-1], [])
            self.assertEqual(tres, res)

    ## default createfile test
    # \brief It tests default settings
    def test_default_createfile_pni(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )
        try:
            FileWriter.writer = PNIWriter
            fl = FileWriter.create_file(self._fname)
            fl.close()
            fl = FileWriter.create_file(self._fname, True)
            fl.close()

            f = nx.open_file(self._fname, readonly=True)
            f = f.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 0)
            f.close()
            fl.close()

            fl = FileWriter.open_file(self._fname, readonly=True)
            f = fl.root()
            self.assertEqual(6, len(f.attributes))
            for at in f.attributes:
                print at.name , at.read() , at.dtype
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 0)
            fl.close()

            self.myAssertRaise(
                Exception, FileWriter.create_file, self._fname)

            self.myAssertRaise(
                Exception, FileWriter.create_file, self._fname,
                False)

            fl2 = FileWriter.create_file(self._fname, True)
            fl2.close()

        finally:
            os.remove(self._fname)

    ## default createfile test
    # \brief It tests default settings
    def test_default_createfile_h5py(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )
        try:
            FileWriter.writer = H5PYWriter
            fl = FileWriter.create_file(self._fname)
            fl.close()
            fl = FileWriter.create_file(self._fname, True)
            fl.close()

            fl = nx.open_file(self._fname, readonly=True)
            f = fl.root()
            self.assertEqual(6, len(f.attributes))
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 0)
            f.close()
            fl.close()

            fl = FileWriter.open_file(self._fname, readonly=True)
            f = fl.root()
            self.assertEqual(6, len(f.attributes))
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
                print at.name , at.read() , at.dtype
            self.assertEqual(
                f.attributes["file_name"][...],
                self._fname)
            self.assertTrue(f.attributes["NX_class"][...],"NXroot")
            self.assertEqual(f.size, 0)
            fl.close()


            self.myAssertRaise(
                Exception, FileWriter.create_file, self._fname)

            self.myAssertRaise(
                Exception, FileWriter.create_file, self._fname,
                False)

            fl2 = FileWriter.create_file(self._fname, True)
            fl2.close()

        finally:
            os.remove(self._fname)

if __name__ == '__main__':
    unittest.main()
