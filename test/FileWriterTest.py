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
import weakref

import nxswriter.FileWriter as FileWriter
import nxswriter.PNIWriter as PNIWriter
import nxswriter.H5PYWriter as H5PYWriter
import h5py

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



class FTCloser(FileWriter.FTObject):


    def __init__(self, h5object, tparent=None):
        FileWriter.FTObject.__init__(self, h5object, tparent)
        self.commands = []
        self._is_valid = True

    def close(self):
        """ close the new file
        """
        self.commands.append("close")
        self._is_valid = False
        FileWriter.FTObject.close(self)

    def reopen(self):
        """ reopen the new file
        """
        self.commands.append("reopen")
        self._is_valid = True
        self._reopen()

    def create(self):
        self.commands.append("create")
        g = FTCloser(self.commands, self)
        self.append(g)
        return g

    @property
    def is_valid(self):
        """ check if field is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._is_valid


def createClass(classname, basecls=FileWriter.FTObject):

    def __init__(self, h5object, tparent=None):
        basecls.__init__(self, h5object, tparent)
        self.commands = []
        self._is_valid = True

    def close(self):
        """ close the new file
        """
        self.commands.append("close")
        self._is_valid = False
        basecls.close(self)

    def reopen(self):
        """ reopen the new file
        """
        basecls.reopen(self)
        self.commands.append("reopen")
        self._is_valid = True

    def create(self, objectclass):
        self.commands.append("create")
        g = objectclass(self.commands, self)
        self.append(g)
        return g

    @property
    def is_valid(self):
        return self._is_valid

    newclass = type(
        classname, (basecls,),
        {
            "__init__": __init__,
            "close": close,
            "reopen": reopen,
            "create": create,
            "is_valid": is_valid
        }
    )
    return newclass


TAttribute = createClass("TAttribute", FileWriter.FTAttribute)
TGroup = createClass("TGroup", FileWriter.FTGroup)
TFile = createClass("TFile", FileWriter.FTFile)
TField = createClass("TField", FileWriter.FTField)
TAttributeManager = createClass("TAttributeManager", FileWriter.FTAttributeManager)
TLink = createClass("TLink", FileWriter.FTLink)

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

        self.assertEqual(el.h5object, w)

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

    ## default createfile test
    # \brief It tests default settings
    def test_ftobject(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        fto = FileWriter.FTObject(None)
        self.assertEqual(fto._h5object, None)
        self.assertEqual(fto.h5object, None)
        self.assertEqual(fto._tparent, None)
        self.assertEqual(fto.parent, None)
        self.assertEqual(fto.is_valid, True)
        fto2 = FileWriter.FTObject(fto)
        self.assertEqual(fto2._h5object, fto)
        self.assertEqual(fto2.h5object, fto)
        self.assertEqual(fto2._tparent, None)
        self.assertEqual(fto2.parent, None)
        self.assertEqual(fto.is_valid, True)
        fto3 = FileWriter.FTObject(fto2, fto)
        self.assertEqual(fto3._h5object, fto2)
        self.assertEqual(fto3.h5object, fto2)
        self.assertEqual(fto3._tparent, fto)
        self.assertEqual(fto3.parent, fto)
        self.assertEqual(fto.is_valid, True)

    ## default createfile test
    # \brief It tests default settings
    def test_ftcloser(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        fto = FTCloser(None)
        self.assertEqual(fto._h5object, None)
        self.assertEqual(fto.h5object, None)
        self.assertEqual(fto._tparent, None)
        self.assertEqual(fto.parent, None)
        self.assertEqual(fto.is_valid, True)
        fto2 = fto.create()
        self.assertEqual(fto2._h5object, fto.commands)
        self.assertEqual(fto2.h5object, fto.commands)
        self.assertEqual(fto2._tparent, fto)
        self.assertEqual(fto2.parent, fto)
        self.assertEqual(fto.is_valid, True)
        fto3 = fto2.create()
        self.assertEqual(fto3._h5object, fto2.commands)
        self.assertEqual(fto3.h5object, fto2.commands)
        self.assertEqual(fto3._tparent, fto2)
        self.assertEqual(fto3.parent, fto2)
        self.assertEqual(fto.is_valid, True)
        fto4 = fto2.create()
        self.assertEqual(fto4._h5object, fto2.commands)
        self.assertEqual(fto4.h5object, fto2.commands)
        self.assertEqual(fto4._tparent, fto2)
        self.assertEqual(fto4.parent, fto2)
        self.assertEqual(fto.is_valid, True)

        self.assertEqual(fto.commands, ['create'])
        self.assertEqual(fto2.commands, ['create','create'])
        self.assertEqual(fto3.commands, [])
        self.assertEqual(fto4.commands, [])
        self.assertEqual(fto.is_valid, True)
        self.assertEqual(fto2.is_valid, True)
        self.assertEqual(fto3.is_valid, True)
        self.assertEqual(fto4.is_valid, True)
        fto.close()
        self.assertEqual(fto.commands, ['create','close'])
        self.assertEqual(fto2.commands, ['create','create','close'])
        self.assertEqual(fto3.commands, ['close'])
        self.assertEqual(fto4.commands, ['close'])
        self.assertEqual(fto.is_valid, False)
        self.assertEqual(fto2.is_valid, False)
        self.assertEqual(fto3.is_valid, False)
        self.assertEqual(fto4.is_valid, False)
        fto.reopen()
        self.assertEqual(fto.commands, ['create','close' , 'reopen'])
        self.assertEqual(fto2.commands, ['create','create','close', 'reopen'])
        self.assertEqual(fto3.commands, ['close', 'reopen'])
        self.assertEqual(fto4.commands, ['close', 'reopen'])
        self.assertEqual(fto.is_valid, True)
        self.assertEqual(fto2.is_valid, True)
        self.assertEqual(fto3.is_valid, True)
        self.assertEqual(fto4.is_valid, True)

   ## default createfile test
    # \brief It tests default settings
    def test_ftobjects(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        fto = FileWriter.FTObject(None)
        self.assertEqual(fto.is_valid, True)
        self.assertEqual(fto.h5object, None)
        self.assertEqual(fto.parent, None)
        self.assertEqual(fto.is_valid, True)

        tf = TFile(fto, "myfile.txt")
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.h5object, fto)
        self.assertEqual(tf.parent, None)
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.name, "myfile.txt")
        self.assertTrue(hasattr(tf.root, "__call__"))
        self.assertTrue(hasattr(tf.flush, "__call__"))
        self.assertTrue(hasattr(tf, "readonly"))
        self.assertTrue(hasattr(tf.reopen, "__call__"))

        ta = tf.create(TAttribute)
        self.assertEqual(ta._h5object, tf.commands)
        self.assertEqual(ta.h5object, tf.commands)
        self.assertEqual(ta._tparent, tf)
        self.assertEqual(ta.parent, tf)
        self.assertEqual(ta.is_valid, True)
        self.assertTrue(hasattr(ta.read, "__call__"))
        self.assertTrue(hasattr(ta.write, "__call__"))
        self.assertTrue(hasattr(ta.__setitem__, "__call__"))
        self.assertTrue(hasattr(ta.__getitem__, "__call__"))
        self.assertTrue(hasattr(ta, "dtype"))
        self.assertTrue(hasattr(ta, "shape"))
        self.assertTrue(hasattr(ta.reopen, "__call__"))

        tg = tf.create(TGroup)
        self.assertEqual(tg._h5object, tf.commands)
        self.assertEqual(tg.h5object, tf.commands)
        self.assertEqual(tg._tparent, tf)
        self.assertEqual(tg.parent, tf)
        self.assertEqual(tg.is_valid, True)
        self.assertTrue(hasattr(tg.open, "__call__"))
        self.assertTrue(hasattr(tg.create_group, "__call__"))
        self.assertTrue(hasattr(tg.create_field, "__call__"))
        self.assertTrue(hasattr(tg, "size"))
        self.assertTrue(hasattr(tg, "parent"))
        self.assertTrue(hasattr(tg, "attributes"))
        self.assertTrue(hasattr(tg.exists, "__call__"))
        self.assertTrue(hasattr(tg.reopen, "__call__"))


        td = tf.create(TField)
        self.assertEqual(td._h5object, tf.commands)
        self.assertEqual(td.h5object, tf.commands)
        self.assertEqual(td._tparent, tf)
        self.assertEqual(td.parent, tf)
        self.assertEqual(td.is_valid, True)
        self.assertTrue(hasattr(td, "attributes"))
        self.assertTrue(hasattr(td.grow, "__call__"))
        self.assertTrue(hasattr(td.read, "__call__"))
        self.assertTrue(hasattr(td.write, "__call__"))
        self.assertTrue(hasattr(td.__setitem__, "__call__"))
        self.assertTrue(hasattr(td.__getitem__, "__call__"))
        self.assertTrue(hasattr(td, "dtype"))
        self.assertTrue(hasattr(td, "shape"))
        self.assertTrue(hasattr(td, "size"))
        self.assertTrue(hasattr(td, "parent"))
        self.assertTrue(hasattr(td.reopen, "__call__"))

        td2 = tg.create(TField)
        self.assertEqual(td2._h5object, tg.commands)
        self.assertEqual(td2.h5object, tg.commands)
        self.assertEqual(td2._tparent, tg)
        self.assertEqual(td2.parent, tg)
        self.assertEqual(td2.is_valid, True)

        tl = tf.create(TLink)
        self.assertEqual(tl._h5object, tf.commands)
        self.assertEqual(tl.h5object, tf.commands)
        self.assertEqual(tl._tparent, tf)
        self.assertEqual(tl.parent, tf)
        self.assertEqual(tl.is_valid, True)

        tm = tg.create(TAttributeManager)
        self.assertEqual(tm._h5object, tg.commands)
        self.assertEqual(tm.h5object, tg.commands)
        self.assertEqual(tm._tparent, tg)
        self.assertEqual(tm.parent, tg)
        self.assertEqual(tm.is_valid, True)

        ta2 = tg.create(TAttribute)
        self.assertEqual(ta2._h5object, tg.commands)
        self.assertEqual(ta2.h5object, tg.commands)
        self.assertEqual(ta2._tparent, tg)
        self.assertEqual(ta2.parent, tg)
        self.assertEqual(ta2.is_valid, True)

        self.assertTrue(isinstance(tf, FileWriter.FTObject))
        self.assertTrue(isinstance(tf, FileWriter.FTFile))
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.h5object, fto)
        self.assertEqual(tf.parent, None)
        self.assertEqual(tf.commands, ['create','create','create','create'])

        self.assertTrue(isinstance(ta, FileWriter.FTObject))
        self.assertTrue(isinstance(ta, FileWriter.FTAttribute))
        self.assertEqual(ta.is_valid, True)
        self.assertEqual(ta.h5object, tf.commands)
        self.assertEqual(ta.parent, tf)
        self.assertEqual(ta.commands, [])

        self.assertTrue(isinstance(td, FileWriter.FTObject))
        self.assertTrue(isinstance(td, FileWriter.FTField))
        self.assertEqual(td.is_valid, True)
        self.assertEqual(td.h5object, tf.commands)
        self.assertEqual(td.parent, tf)
        self.assertEqual(td.commands, [])

        self.assertTrue(isinstance(tl, FileWriter.FTObject))
        self.assertTrue(isinstance(tl, FileWriter.FTLink))
        self.assertEqual(tl.is_valid, True)
        self.assertEqual(tl.h5object, tf.commands)
        self.assertEqual(tl.parent, tf)
        self.assertEqual(tl.commands, [])

        self.assertTrue(isinstance(tg, FileWriter.FTObject))
        self.assertTrue(isinstance(tg, FileWriter.FTGroup))
        self.assertEqual(tg.is_valid, True)
        self.assertEqual(tg.h5object, tf.commands)
        self.assertEqual(tg.parent, tf)
        self.assertEqual(tg.commands, ['create','create','create'])

        self.assertTrue(isinstance(td2, FileWriter.FTObject))
        self.assertTrue(isinstance(td2, FileWriter.FTField))
        self.assertEqual(td2.is_valid, True)
        self.assertEqual(td2.h5object, tg.commands)
        self.assertEqual(td2.parent, tg)
        self.assertEqual(td2.commands, [])

        self.assertTrue(isinstance(tm, FileWriter.FTObject))
        self.assertTrue(isinstance(tm, FileWriter.FTAttributeManager))
        self.assertEqual(tm.is_valid, True)
        self.assertEqual(tm.h5object, tg.commands)
        self.assertEqual(tm.parent, tg)
        self.assertEqual(tm.commands, [])

        self.assertTrue(isinstance(ta2, FileWriter.FTObject))
        self.assertTrue(isinstance(ta2, FileWriter.FTAttribute))
        self.assertEqual(ta2.is_valid, True)
        self.assertEqual(ta2.h5object, tg.commands)
        self.assertEqual(ta2.parent, tg)
        self.assertEqual(ta2.commands, [])

        tf.close()

        self.assertTrue(isinstance(tf, FileWriter.FTObject))
        self.assertTrue(isinstance(tf, FileWriter.FTFile))
        self.assertEqual(tf.is_valid, False)
        self.assertEqual(tf.h5object, fto)
        self.assertEqual(tf.parent, None)
        self.assertEqual(
            tf.commands,
            ['create','create','create','create', 'close'])

        self.assertTrue(isinstance(ta, FileWriter.FTObject))
        self.assertTrue(isinstance(ta, FileWriter.FTAttribute))
        self.assertEqual(ta.is_valid, False)
        self.assertEqual(ta.h5object, tf.commands)
        self.assertEqual(ta.parent, tf)
        self.assertEqual(ta.commands, ['close'])

        self.assertTrue(isinstance(td, FileWriter.FTObject))
        self.assertTrue(isinstance(td, FileWriter.FTField))
        self.assertEqual(td.is_valid, False)
        self.assertEqual(td.h5object, tf.commands)
        self.assertEqual(td.parent, tf)
        self.assertEqual(td.commands, ['close'])

        self.assertTrue(isinstance(tl, FileWriter.FTObject))
        self.assertTrue(isinstance(tl, FileWriter.FTLink))
        self.assertEqual(tl.is_valid, False)
        self.assertEqual(tl.h5object, tf.commands)
        self.assertEqual(tl.parent, tf)
        self.assertEqual(tl.commands, ['close'])

        self.assertTrue(isinstance(tg, FileWriter.FTObject))
        self.assertTrue(isinstance(tg, FileWriter.FTGroup))
        self.assertEqual(tg.is_valid, False)
        self.assertEqual(tg.h5object, tf.commands)
        self.assertEqual(tg.parent, tf)
        self.assertEqual(
            tg.commands, ['create','create','create', 'close'])

        self.assertTrue(isinstance(td2, FileWriter.FTObject))
        self.assertTrue(isinstance(td2, FileWriter.FTField))
        self.assertEqual(td2.is_valid, False)
        self.assertEqual(td2.h5object, tg.commands)
        self.assertEqual(td2.parent, tg)
        self.assertEqual(td2.commands, ['close'])

        self.assertTrue(isinstance(tm, FileWriter.FTObject))
        self.assertTrue(isinstance(tm, FileWriter.FTAttributeManager))
        self.assertEqual(tm.is_valid, False)
        self.assertEqual(tm.h5object, tg.commands)
        self.assertEqual(tm.parent, tg)
        self.assertEqual(tm.commands, ['close'])

        self.assertTrue(isinstance(ta2, FileWriter.FTObject))
        self.assertTrue(isinstance(ta2, FileWriter.FTAttribute))
        self.assertEqual(ta2.is_valid, False)
        self.assertEqual(ta2.h5object, tg.commands)
        self.assertEqual(ta2.parent, tg)
        self.assertEqual(ta2.commands, ['close'])

        tf.reopen()

        self.assertTrue(isinstance(tf, FileWriter.FTObject))
        self.assertTrue(isinstance(tf, FileWriter.FTFile))
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.h5object, fto)
        self.assertEqual(tf.parent, None)
        self.assertEqual(
            tf.commands,
            ['create','create','create','create', 'close', 'reopen'])

        self.assertTrue(isinstance(ta, FileWriter.FTObject))
        self.assertTrue(isinstance(ta, FileWriter.FTAttribute))
        self.assertEqual(ta.is_valid, True)
        self.assertEqual(ta.h5object, tf.commands)
        self.assertEqual(ta.parent, tf)
        self.assertEqual(ta.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(td, FileWriter.FTObject))
        self.assertTrue(isinstance(td, FileWriter.FTField))
        self.assertEqual(td.is_valid, True)
        self.assertEqual(td.h5object, tf.commands)
        self.assertEqual(td.parent, tf)
        self.assertEqual(td.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(tl, FileWriter.FTObject))
        self.assertTrue(isinstance(tl, FileWriter.FTLink))
        self.assertEqual(tl.is_valid, True)
        self.assertEqual(tl.h5object, tf.commands)
        self.assertEqual(tl.parent, tf)
        self.assertEqual(tl.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(tg, FileWriter.FTObject))
        self.assertTrue(isinstance(tg, FileWriter.FTGroup))
        self.assertEqual(tg.is_valid, True)
        self.assertEqual(tg.h5object, tf.commands)
        self.assertEqual(tg.parent, tf)
        self.assertEqual(
            tg.commands, ['create','create','create', 'close', 'reopen'])

        self.assertTrue(isinstance(td2, FileWriter.FTObject))
        self.assertTrue(isinstance(td2, FileWriter.FTField))
        self.assertEqual(td2.is_valid, True)
        self.assertEqual(td2.h5object, tg.commands)
        self.assertEqual(td2.parent, tg)
        self.assertEqual(td2.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(tm, FileWriter.FTObject))
        self.assertTrue(isinstance(tm, FileWriter.FTAttributeManager))
        self.assertEqual(tm.is_valid, True)
        self.assertEqual(tm.h5object, tg.commands)
        self.assertEqual(tm.parent, tg)
        self.assertEqual(tm.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(ta2, FileWriter.FTObject))
        self.assertTrue(isinstance(ta2, FileWriter.FTAttribute))
        self.assertEqual(ta2.is_valid, True)
        self.assertEqual(ta2.h5object, tg.commands)
        self.assertEqual(ta2.parent, tg)
        self.assertEqual(ta2.commands, ['close', 'reopen'])

    ## default createfile test
    # \brief It tests default settings
    def test_h5pyfile(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )

        overwrite = False

        try:
            FileWriter.writer = H5PYWriter
            fl = FileWriter.create_file(self._fname)
            self.assertTrue(
                isinstance(fl, FileWriter.FTFile))

            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, h5py.File))
            self.assertEqual(fl.parent, None)

            rt = fl.root()
            fl.flush()
            self.assertEqual(fl.h5object, rt.h5object)
            self.assertEqual(fl.is_valid, True)
            self.assertEqual(fl.h5object.name is not None, True)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.h5object.mode in ["r"], False)
            fl.close()
            self.assertEqual(fl.is_valid, False)
            self.assertEqual(fl.readonly, None)

            fl.reopen()
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, h5py.File))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.h5object.mode in ["r"], False)

            fl.close()

            fl.reopen(True)
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, h5py.File))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, True)
            self.assertEqual(fl.h5object.mode in ["r"], True)

            fl.close()

            self.myAssertRaise(
                Exception, fl.reopen, True, True)
            self.myAssertRaise(
                Exception, fl.reopen, False, True)


            fl = H5PYWriter.open_file(self._fname, readonly=True)
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
    def test_pnifile(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun )

        try:
            overwrite = False
            FileWriter.writer = PNIWriter
            fl = FileWriter.create_file(self._fname)
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
            det = ins.create_group("detector", "NXdetector")
            dt = entry.create_group("data", "NXdata")

            df0 = FileWriter.deflate_filter()
            df1 = FileWriter.deflate_filter()
            df1.rate = 2
            df2 = FileWriter.deflate_filter()
            df2.rate = 4
            df2.shuffle = 6

            strscalar = entry.create_field("strscalar", "string")
            floatscalar = entry.create_field("floatscalar", "float64")
            intscalar = entry.create_field("intscalar", "uint64")
            strspec = ins.create_field("strspec", "string", [10], [6])
            floatspec = ins.create_field("floatspec", "float32", [20], [16])
            intspec = ins.create_field("intspec", "int64", [30], [5])
            strimage = det.create_field("strimage", "string", [2,2], [2,1])
            floatimage = det.create_field(
                "floatimage", "float64", [20,10], dfilter=df0)
            intimage = det.create_field("intimage", "uint32", [0, 30], [1, 30])
            strvec = det.create_field("strvec", "string", [0,2,2], [1,2,2])
            floatvec = det.create_field(
                "floatvec", "float64", [1, 20,10], [1, 10, 10], dfilter=df1)
            intvec = det.create_field(
                "intvec", "uint32", [0, 2, 30], dfilter=df2)


            lkintimage = FileWriter.link(
                "/entry12345/instrument/detector/intimage", dt, "lkintimage")
            lkfloatvec = FileWriter.link(
                "/entry12345/instrument/detector/floatvec", dt, "lkfloatvec")
            lkintspec = FileWriter.link(
                "/entry12345/instrument/intspec", dt, "lkintspec")
            lkdet = FileWriter.link(
                "/entry12345/instrument/detector", dt, "lkdet")
            lkno = FileWriter.link(
                "/notype/unknown", dt, "lkno")


            attr0 = rt.attributes
            attr1 = entry.attributes

            print attr0.h5object
            self.assertTrue(isinstance(attr0, PNIWriter.PNIAttributeManager))
            self.assertTrue(
                isinstance(attr0.h5object, nx._nxh5.nxgroup_attributes))
            self.assertTrue(isinstance(attr1, PNIWriter.PNIAttributeManager))
            self.assertTrue(
                isinstance(attr1.h5object, nx._nxh5.nxgroup_attributes))

            print dir(rt)
            self.assertTrue(
                isinstance(rt, PNIWriter.PNIGroup))
            self.assertEqual(rt.name, "/")
            self.assertEqual(rt.path, "/")
            self.assertEqual(
                len(fl.h5object.root().attributes),
                len(rt.h5object.attributes))
            attr = rt.attributes
            self.assertEqual(attr["NX_class"][...], "NXroot")
            self.assertTrue(
                isinstance(attr, PNIWriter.PNIAttributeManager))
            self.assertEqual(
                fl.h5object.root().path,
                rt.h5object.path)
            self.assertEqual(rt.is_valid, True)
            self.assertEqual(rt.h5object.is_valid, True)
            self.assertEqual(rt.parent, fl)
            self.assertEqual(rt.size, 2)
            self.assertEqual(rt.exists("entry12345"), True)
            self.assertEqual(rt.exists("notype"), True)
            self.assertEqual(rt.exists("strument"), False)

            for rr in rt:
                print rr.name

            self.assertTrue(
                isinstance(entry, PNIWriter.PNIGroup))
            self.assertEqual(entry.name, "entry12345")
            self.assertEqual(entry.path, "/entry12345:NXentry")
            self.assertEqual(
                len(entry.h5object.attributes), 1)
            attr = entry.attributes
            self.assertEqual(attr["NX_class"][...], "NXentry")
            self.assertTrue(
                isinstance(attr, PNIWriter.PNIAttributeManager))
            self.assertEqual(entry.is_valid, True)
            self.assertEqual(entry.h5object.is_valid, True)
            self.assertEqual(entry.parent, rt)
            self.assertEqual(entry.size, 5)
            self.assertEqual(entry.exists("instrument"), True)
            self.assertEqual(entry.exists("data"), True)
            self.assertEqual(entry.exists("floatscalar"), True)
            self.assertEqual(entry.exists("intscalar"), True)
            self.assertEqual(entry.exists("strscalar"), True)
            self.assertEqual(entry.exists("strument"), False)


            self.assertTrue(
                isinstance(nt, PNIWriter.PNIGroup))
            self.assertEqual(nt.name, "notype")
            self.assertEqual(nt.path, "/notype")
            self.assertEqual(
                len(nt.h5object.attributes), 0)
            attr = nt.attributes
            self.assertTrue(
                isinstance(attr, PNIWriter.PNIAttributeManager))
            self.assertEqual(nt.is_valid, True)
            self.assertEqual(nt.h5object.is_valid, True)
            self.assertEqual(nt.parent, rt)
            self.assertEqual(nt.size, 0)
            self.assertEqual(nt.exists("strument"), False)


            self.assertTrue(
                isinstance(ins, PNIWriter.PNIGroup))
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(
                ins.path, "/entry12345:NXentry/instrument:NXinstrument")
            self.assertEqual(
                len(ins.h5object.attributes), 1)
            attr = ins.attributes
            self.assertEqual(attr["NX_class"][...], "NXinstrument")
            self.assertTrue(
                isinstance(attr, PNIWriter.PNIAttributeManager))
            self.assertEqual(ins.is_valid, True)
            self.assertEqual(ins.h5object.is_valid, True)
            self.assertEqual(ins.parent, entry)
            self.assertEqual(ins.size, 4)
            self.assertEqual(ins.exists("detector"), True)
            self.assertEqual(ins.exists("floatspec"), True)
            self.assertEqual(ins.exists("intspec"), True)
            self.assertEqual(ins.exists("strspec"), True)
            self.assertEqual(ins.exists("strument"), False)

            kids = set()
            for en in ins:
                kids.add(en.name)

            self.assertEqual(kids, set(["detector", "floatspec",
                                        "intspec", "strspec"]))

            ins_op = entry.open("instrument")
            self.assertTrue(
                isinstance(ins_op, PNIWriter.PNIGroup))
            self.assertEqual(ins_op.name, "instrument")
            self.assertEqual(
                ins_op.path, "/entry12345:NXentry/instrument:NXinstrument")
            self.assertEqual(
                len(ins_op.h5object.attributes), 1)
            attr = ins_op.attributes
            self.assertEqual(attr["NX_class"][...], "NXinstrument")
            self.assertTrue(
                isinstance(attr, PNIWriter.PNIAttributeManager))
            self.assertEqual(ins_op.is_valid, True)
            self.assertEqual(ins_op.h5object.is_valid, True)
            self.assertEqual(ins_op.parent, entry)
            self.assertEqual(ins_op.size, 4)
            self.assertEqual(ins_op.exists("detector"), True)
            self.assertEqual(ins_op.exists("floatspec"), True)
            self.assertEqual(ins_op.exists("intspec"), True)
            self.assertEqual(ins_op.exists("strspec"), True)
            self.assertEqual(ins_op.exists("strument"), False)

            kids = set()
            for en in ins_op:
                kids.add(en.name)

            self.assertEqual(kids, set(["detector", "floatspec",
                                        "intspec", "strspec"]))

            self.assertTrue(
                isinstance(det, PNIWriter.PNIGroup))
            self.assertEqual(det.name, "detector")
            self.assertEqual(
                det.path,
                "/entry12345:NXentry/instrument:NXinstrument/"
                "detector:NXdetector")
            self.assertEqual(
                len(det.h5object.attributes), 1)
            attr = det.attributes
            self.assertEqual(attr["NX_class"][...], "NXdetector")
            self.assertTrue(
                isinstance(attr, PNIWriter.PNIAttributeManager))
            self.assertEqual(det.is_valid, True)
            self.assertEqual(det.h5object.is_valid, True)
            self.assertEqual(det.parent, ins)
            self.assertEqual(det.size, 6)
            self.assertEqual(det.exists("strimage"), True)
            self.assertEqual(det.exists("intvec"), True)
            self.assertEqual(det.exists("floatimage"), True)
            self.assertEqual(det.exists("floatvec"), True)
            self.assertEqual(det.exists("intimage"), True)
            self.assertEqual(det.exists("strvec"), True)
            self.assertEqual(det.exists("strument"), False)

            kids = set()
            for en in det:
                kids.add(en.name)
            print kids

            self.assertEqual(
                kids,
                set(['strimage', 'intvec', 'floatimage',
                     'floatvec', 'intimage', 'strvec']))



            self.assertTrue(isinstance(strscalar, PNIWriter.PNIField))
            self.assertTrue(isinstance(strscalar.h5object, nx._nxh5.nxfield))
            self.assertEqual(strscalar.name, 'strscalar')
            self.assertEqual(strscalar.path, '/entry12345:NXentry/strscalar')
            self.assertEqual(strscalar.dtype, 'string')
            self.assertEqual(strscalar.shape, (1,))

            self.assertTrue(isinstance(floatscalar, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatscalar.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatscalar.name, 'floatscalar')
            self.assertEqual(floatscalar.path, '/entry12345:NXentry/floatscalar')
            self.assertEqual(floatscalar.dtype, 'float64')
            self.assertEqual(floatscalar.shape, (1,))

            self.assertTrue(isinstance(intscalar, PNIWriter.PNIField))
            self.assertTrue(isinstance(intscalar.h5object, nx._nxh5.nxfield))
            self.assertEqual(intscalar.name, 'intscalar')
            self.assertEqual(intscalar.path, '/entry12345:NXentry/intscalar')
            self.assertEqual(intscalar.dtype, 'uint64')
            self.assertEqual(intscalar.shape, (1,))

            self.assertTrue(isinstance(strspec, PNIWriter.PNIField))
            self.assertTrue(isinstance(strspec.h5object, nx._nxh5.nxfield))
            self.assertEqual(strspec.name, 'strspec')
            self.assertEqual(strspec.path, '/entry12345:NXentry/instrument:NXinstrument/strspec')
            self.assertEqual(strspec.dtype, 'string')
            self.assertEqual(strspec.shape, (10,))

            self.assertTrue(isinstance(floatspec, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatspec.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatspec.name, 'floatspec')
            self.assertEqual(floatspec.path, '/entry12345:NXentry/instrument:NXinstrument/floatspec')
            self.assertEqual(floatspec.dtype, 'float32')
            self.assertEqual(floatspec.shape, (20,))

            self.assertTrue(isinstance(intspec, PNIWriter.PNIField))
            self.assertTrue(isinstance(intspec.h5object, nx._nxh5.nxfield))
            self.assertEqual(intspec.name, 'intspec')
            self.assertEqual(intspec.path, '/entry12345:NXentry/instrument:NXinstrument/intspec')
            self.assertEqual(intspec.dtype, 'int64')
            self.assertEqual(intspec.shape, (30,))


            self.assertTrue(isinstance(strimage, PNIWriter.PNIField))
            self.assertTrue(isinstance(strimage.h5object, nx._nxh5.nxfield))
            self.assertEqual(strimage.name, 'strimage')
            self.assertEqual(strimage.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strimage')
            self.assertEqual(strimage.dtype, 'string')
            self.assertEqual(strimage.shape, (2, 2))

            self.assertTrue(isinstance(floatimage, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatimage.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatimage.name, 'floatimage')
            self.assertEqual(floatimage.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatimage')
            self.assertEqual(floatimage.dtype, 'float64')
            self.assertEqual(floatimage.shape, (20, 10))

            self.assertTrue(isinstance(intimage, PNIWriter.PNIField))
            self.assertTrue(isinstance(intimage.h5object, nx._nxh5.nxfield))
            self.assertEqual(intimage.name, 'intimage')
            self.assertEqual(intimage.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intimage')
            self.assertEqual(intimage.dtype, 'uint32')
            self.assertEqual(intimage.shape, (0, 30))





            self.assertTrue(isinstance(strvec, PNIWriter.PNIField))
            self.assertTrue(isinstance(strvec.h5object, nx._nxh5.nxfield))
            self.assertEqual(strvec.name, 'strvec')
            self.assertEqual(strvec.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strvec')
            self.assertEqual(strvec.dtype, 'string')
            self.assertEqual(strvec.shape, (0, 2, 2))

            self.assertTrue(isinstance(floatvec, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatvec.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatvec.name, 'floatvec')
            self.assertEqual(floatvec.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatvec')
            self.assertEqual(floatvec.dtype, 'float64')
            self.assertEqual(floatvec.shape, (1, 20, 10))

            self.assertTrue(isinstance(intvec, PNIWriter.PNIField))
            self.assertTrue(isinstance(intvec.h5object, nx._nxh5.nxfield))
            self.assertEqual(intvec.name, 'intvec')
            self.assertEqual(intvec.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intvec')
            self.assertEqual(intvec.dtype, 'uint32')
            self.assertEqual(intvec.shape, (0, 2, 30))


            strscalar_op= entry.open("strscalar")
            floatscalar_op = entry.open("floatscalar")
            intscalar_op = entry.open("intscalar")
            strspec_op = ins.open("strspec")
            floatspec_op = ins.open("floatspec")
            intspec_op = ins.open("intspec")
            strimage_op = det.open("strimage")
            floatimage_op = det.open("floatimage")
            intimage_op = det.open("intimage")
            strvec_op = det.open("strvec")
            floatvec_op = det.open("floatvec")
            intvec_op = det.open("intvec")


            self.assertTrue(isinstance(strscalar_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(strscalar_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(strscalar_op.name, 'strscalar')
            self.assertEqual(strscalar_op.path, '/entry12345:NXentry/strscalar')
            self.assertEqual(strscalar_op.dtype, 'string')
            self.assertEqual(strscalar_op.shape, (1,))

            self.assertTrue(isinstance(floatscalar_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatscalar_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatscalar_op.name, 'floatscalar')
            self.assertEqual(floatscalar_op.path, '/entry12345:NXentry/floatscalar')
            self.assertEqual(floatscalar_op.dtype, 'float64')
            self.assertEqual(floatscalar_op.shape, (1,))

            self.assertTrue(isinstance(intscalar_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(intscalar_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(intscalar_op.name, 'intscalar')
            self.assertEqual(intscalar_op.path, '/entry12345:NXentry/intscalar')
            self.assertEqual(intscalar_op.dtype, 'uint64')
            self.assertEqual(intscalar_op.shape, (1,))

            self.assertTrue(isinstance(strspec_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(strspec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(strspec_op.name, 'strspec')
            self.assertEqual(strspec_op.path, '/entry12345:NXentry/instrument:NXinstrument/strspec')
            self.assertEqual(strspec_op.dtype, 'string')
            self.assertEqual(strspec_op.shape, (10,))

            self.assertTrue(isinstance(floatspec_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatspec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatspec_op.name, 'floatspec')
            self.assertEqual(floatspec_op.path, '/entry12345:NXentry/instrument:NXinstrument/floatspec')
            self.assertEqual(floatspec_op.dtype, 'float32')
            self.assertEqual(floatspec_op.shape, (20,))

            self.assertTrue(isinstance(intspec_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(intspec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(intspec_op.name, 'intspec')
            self.assertEqual(intspec_op.path, '/entry12345:NXentry/instrument:NXinstrument/intspec')
            self.assertEqual(intspec_op.dtype, 'int64')
            self.assertEqual(intspec_op.shape, (30,))


            self.assertTrue(isinstance(strimage_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(strimage_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(strimage_op.name, 'strimage')
            self.assertEqual(strimage_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strimage')
            self.assertEqual(strimage_op.dtype, 'string')
            self.assertEqual(strimage_op.shape, (2, 2))

            self.assertTrue(isinstance(floatimage_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatimage_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatimage_op.name, 'floatimage')
            self.assertEqual(floatimage_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatimage')
            self.assertEqual(floatimage_op.dtype, 'float64')
            self.assertEqual(floatimage_op.shape, (20, 10))

            self.assertTrue(isinstance(intimage_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(intimage_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(intimage_op.name, 'intimage')
            self.assertEqual(intimage_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intimage')
            self.assertEqual(intimage_op.dtype, 'uint32')
            self.assertEqual(intimage_op.shape, (0, 30))



            self.assertTrue(isinstance(strvec_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(strvec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(strvec_op.name, 'strvec')
            self.assertEqual(strvec_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strvec')
            self.assertEqual(strvec_op.dtype, 'string')
            self.assertEqual(strvec_op.shape, (0, 2, 2))

            self.assertTrue(isinstance(floatvec_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(floatvec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(floatvec_op.name, 'floatvec')
            self.assertEqual(floatvec_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatvec')
            self.assertEqual(floatvec_op.dtype, 'float64')
            self.assertEqual(floatvec_op.shape, (1, 20, 10))

            self.assertTrue(isinstance(intvec_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(intvec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(intvec_op.name, 'intvec')
            self.assertEqual(intvec_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intvec')
            self.assertEqual(intvec_op.dtype, 'uint32')
            self.assertEqual(intvec_op.shape, (0, 2, 30))
            self.assertEqual(intvec_op.parent, det)



            self.assertTrue(isinstance(lkintimage, PNIWriter.PNILink))
            self.assertTrue(isinstance(lkintimage.h5object, nx._nxh5.nxlink))
            self.assertTrue(lkintimage.target_path.endswith(
                "%s://entry12345/instrument/detector/intimage" % self._fname))
            self.assertEqual(
                lkintimage.path,
                "/entry12345:NXentry/data:NXdata/lkintimage")

            self.assertTrue(isinstance(lkfloatvec, PNIWriter.PNILink))
            self.assertTrue(isinstance(lkfloatvec.h5object, nx._nxh5.nxlink))
            self.assertTrue(lkfloatvec.target_path.endswith(
                "%s://entry12345/instrument/detector/floatvec" % self._fname))
            self.assertEqual(
                lkfloatvec.path,
                "/entry12345:NXentry/data:NXdata/lkfloatvec")

            self.assertTrue(isinstance(lkintspec, PNIWriter.PNILink))
            self.assertTrue(isinstance(lkintspec.h5object, nx._nxh5.nxlink))
            self.assertTrue(lkintspec.target_path.endswith(
                "%s://entry12345/instrument/intspec" % self._fname))
            self.assertEqual(
                lkintspec.path,
                "/entry12345:NXentry/data:NXdata/lkintspec")

            self.assertTrue(isinstance(lkdet, PNIWriter.PNILink))
            self.assertTrue(isinstance(lkdet.h5object, nx._nxh5.nxlink))
            self.assertTrue(lkdet.target_path.endswith(
                "%s://entry12345/instrument/detector" % self._fname))
            self.assertEqual(
                lkdet.path,
                "/entry12345:NXentry/data:NXdata/lkdet")

            self.assertTrue(isinstance(lkno, PNIWriter.PNILink))
            self.assertTrue(isinstance(lkno.h5object, nx._nxh5.nxlink))
            self.assertTrue(lkno.target_path.endswith(
                "%s://notype/unknown" % self._fname))
            self.assertEqual(
                lkno.path,
                "/entry12345:NXentry/data:NXdata/lkno")



            lkintimage_op = dt.open("lkintimage")
            lkfloatvec_op = dt.open("lkfloatvec")
            lkintspec_op = dt.open("lkintspec")
            lkdet_op = dt.open("lkdet")
            lkno_op = dt.open("lkno")



            self.assertTrue(isinstance(lkintimage_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(lkintimage_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(lkintimage_op.name, 'lkintimage')
            self.assertEqual(
                lkintimage_op.path,
                '/entry12345:NXentry/data:NXdata/lkintimage')
            self.assertEqual(lkintimage_op.dtype, 'uint32')
            self.assertEqual(lkintimage_op.shape, (0, 30))


            self.assertTrue(isinstance(lkfloatvec_op, PNIWriter.PNIField))
            self.assertTrue(isinstance(lkfloatvec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(lkfloatvec_op.name, 'lkfloatvec')
            self.assertEqual(lkfloatvec_op.path,
                             '/entry12345:NXentry/data:NXdata/lkfloatvec')
            self.assertEqual(lkfloatvec_op.dtype, 'float64')
            self.assertEqual(lkfloatvec_op.shape, (1, 20, 10))


            self.assertTrue(
                isinstance(lkintspec_op, PNIWriter.PNIField))
            self.assertTrue(
                isinstance(lkintspec_op.h5object, nx._nxh5.nxfield))
            self.assertEqual(lkintspec_op.name, 'lkintspec')
            self.assertEqual(lkintspec_op.path,
                             '/entry12345:NXentry/data:NXdata/lkintspec')
            self.assertEqual(lkintspec_op.dtype, 'int64')
            self.assertEqual(lkintspec_op.shape, (30,))

            self.assertTrue(isinstance(lkno_op, PNIWriter.PNILink))
            self.assertTrue(isinstance(lkno_op.h5object, nx._nxh5.nxlink))
            self.assertTrue(lkno_op.target_path.endswith(
                "%s://notype/unknown" % self._fname))
            self.assertEqual(
                lkno_op.path,
                "/entry12345:NXentry/data:NXdata/lkno")


            entry.close()
            self.assertEqual(rt.is_valid, True)
            self.assertEqual(rt.h5object.is_valid, True)
            self.assertEqual(entry.is_valid, False)
            self.assertEqual(entry.h5object.is_valid, False)
            self.assertEqual(dt.is_valid, False)
            self.assertEqual(dt.h5object.is_valid, False)


            entry.reopen()
            self.assertEqual(rt.is_valid, True)
            self.assertEqual(rt.h5object.is_valid, True)
            self.assertEqual(entry.is_valid, True)
            self.assertEqual(entry.h5object.is_valid, True)
            self.assertEqual(dt.is_valid, True)
            self.assertEqual(dt.h5object.is_valid, True)

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

    ## default createfile test
    # \brief It tests default settings
    def test_h5pygroup(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)
        self._fname= '%s/%s%s.h5' % (os.getcwd(), self.__class__.__name__, fun)

        try:
            overwrite = False
            FileWriter.writer = H5PYWriter
            fl = FileWriter.create_file(self._fname)

            rt = fl.root()
            nt = rt.create_group("notype")
            entry = rt.create_group("entry12345", "NXentry")
            ins = entry.create_group("instrument", "NXinstrument")
            det = ins.create_group("detector", "NXdetector")
            dt = entry.create_group("data", "NXdata")

            df0 = FileWriter.deflate_filter()
            df1 = FileWriter.deflate_filter()
            df1.rate = 2
            df2 = FileWriter.deflate_filter()
            df2.rate = 4
            df2.shuffle = 6

            strscalar = entry.create_field("strscalar", "string")
            floatscalar = entry.create_field("floatscalar", "float64")
            intscalar = entry.create_field("intscalar", "uint64")
            strspec = ins.create_field("strspec", "string", [10], [6])
            floatspec = ins.create_field("floatspec", "float32", [20], [16])
            intspec = ins.create_field("intspec", "int64", [30], [5])
            strimage = det.create_field("strimage", "string", [2,2], [2,1])
            floatimage = det.create_field(
                "floatimage", "float64", [20,10], dfilter=df0)
            intimage = det.create_field("intimage", "uint32", [0, 30], [1, 30])
            strvec = det.create_field("strvec", "string", [0,2,2], [1,2,2])
            floatvec = det.create_field(
                "floatvec", "float64", [1, 20,10], [1, 10, 10], dfilter=df1)
            intvec = det.create_field(
                "intvec", "uint32", [0, 2, 30], dfilter=df2)


            lkintimage = FileWriter.link(
                "/entry12345/instrument/detector/intimage", dt, "lkintimage")
            lkfloatvec = FileWriter.link(
                "/entry12345/instrument/detector/floatvec", dt, "lkfloatvec")
            lkintspec = FileWriter.link(
                "/entry12345/instrument/intspec", dt, "lkintspec")
            lkdet = FileWriter.link(
                "/entry12345/instrument/detector", dt, "lkdet")
            lkno = FileWriter.link(
                "/notype/unknown", dt, "lkno")


            attr0 = rt.attributes
            attr1 = entry.attributes

            print attr0.h5object
            self.assertTrue(isinstance(attr0, H5PYWriter.H5PYAttributeManager))
            print dir(attr0.h5object)
            self.assertTrue(
                isinstance(attr0.h5object, h5py.AttributeManager))
            self.assertTrue(isinstance(attr1, H5PYWriter.H5PYAttributeManager))
            self.assertTrue(
                isinstance(attr1.h5object, h5py.AttributeManager))

            print dir(rt)
            self.assertTrue(
                isinstance(rt, H5PYWriter.H5PYGroup))
            self.assertEqual(rt.name, "/")
            self.assertEqual(rt.path, "/")
            attr = rt.attributes
            self.assertEqual(attr["NX_class"][...], "NXroot")
            self.assertTrue(
                isinstance(attr, H5PYWriter.H5PYAttributeManager))
            self.assertEqual(rt.is_valid, True)
            self.assertEqual(rt.parent, fl)
            self.assertEqual(rt.size, 2)
            self.assertEqual(rt.exists("entry12345"), True)
            self.assertEqual(rt.exists("notype"), True)
            self.assertEqual(rt.exists("strument"), False)

            for rr in rt:
                print rr.name

            self.assertTrue(
                isinstance(entry, H5PYWriter.H5PYGroup))
            self.assertEqual(entry.name, "entry12345")
            self.assertEqual(entry.path, "/entry12345:NXentry")
            self.assertEqual(
                len(entry.h5object.attrs), 1)
            attr = entry.attributes
            self.assertEqual(attr["NX_class"][...], "NXentry")
            self.assertTrue(
                isinstance(attr, H5PYWriter.H5PYAttributeManager))
            self.assertEqual(entry.is_valid, True)
            self.assertEqual(entry.parent, rt)
            self.assertEqual(entry.size, 5)
            self.assertEqual(entry.exists("instrument"), True)
            self.assertEqual(entry.exists("data"), True)
            self.assertEqual(entry.exists("floatscalar"), True)
            self.assertEqual(entry.exists("intscalar"), True)
            self.assertEqual(entry.exists("strscalar"), True)
            self.assertEqual(entry.exists("strument"), False)


            self.assertTrue(
                isinstance(nt, H5PYWriter.H5PYGroup))
            self.assertEqual(nt.name, "notype")
            self.assertEqual(nt.path, "/notype")
            print nt.h5object.attrs.keys()
            self.assertEqual(
                len(nt.h5object.attrs), 0)
            attr = nt.attributes
            self.assertTrue(
                isinstance(attr, H5PYWriter.H5PYAttributeManager))
            self.assertEqual(nt.is_valid, True)
            self.assertEqual(nt.parent, rt)
            self.assertEqual(nt.size, 0)
            self.assertEqual(nt.exists("strument"), False)


            self.assertTrue(
                isinstance(ins, H5PYWriter.H5PYGroup))
            self.assertEqual(ins.name, "instrument")
            self.assertEqual(
                ins.path, "/entry12345:NXentry/instrument:NXinstrument")
            self.assertEqual(
                len(ins.h5object.attrs), 1)
            attr = ins.attributes
            self.assertEqual(attr["NX_class"][...], "NXinstrument")
            self.assertTrue(
                isinstance(attr, H5PYWriter.H5PYAttributeManager))
            self.assertEqual(ins.is_valid, True)
            self.assertEqual(ins.parent, entry)
            self.assertEqual(ins.size, 4)
            self.assertEqual(ins.exists("detector"), True)
            self.assertEqual(ins.exists("floatspec"), True)
            self.assertEqual(ins.exists("intspec"), True)
            self.assertEqual(ins.exists("strspec"), True)
            self.assertEqual(ins.exists("strument"), False)

            kids = set()
            for en in ins:
                kids.add(en.name)

            self.assertEqual(kids, set(["detector", "floatspec",
                                        "intspec", "strspec"]))

            ins_op = entry.open("instrument")
            self.assertTrue(
                isinstance(ins_op, H5PYWriter.H5PYGroup))
            self.assertEqual(ins_op.name, "instrument")
            self.assertEqual(
                ins_op.path, "/entry12345:NXentry/instrument:NXinstrument")
            self.assertEqual(
                len(ins_op.h5object.attrs), 1)
            attr = ins_op.attributes
            self.assertEqual(attr["NX_class"][...], "NXinstrument")
            self.assertTrue(
                isinstance(attr, H5PYWriter.H5PYAttributeManager))
            self.assertEqual(ins_op.is_valid, True)
            self.assertEqual(ins_op.parent, entry)
            self.assertEqual(ins_op.size, 4)
            self.assertEqual(ins_op.exists("detector"), True)
            self.assertEqual(ins_op.exists("floatspec"), True)
            self.assertEqual(ins_op.exists("intspec"), True)
            self.assertEqual(ins_op.exists("strspec"), True)
            self.assertEqual(ins_op.exists("strument"), False)

            kids = set()
            for en in ins_op:
                kids.add(en.name)

            self.assertEqual(kids, set(["detector", "floatspec",
                                        "intspec", "strspec"]))

            self.assertTrue(
                isinstance(det, H5PYWriter.H5PYGroup))
            self.assertEqual(det.name, "detector")
            self.assertEqual(
                det.path,
                "/entry12345:NXentry/instrument:NXinstrument/"
                "detector:NXdetector")
            self.assertEqual(
                len(det.h5object.attrs), 1)
            attr = det.attributes
            self.assertEqual(attr["NX_class"][...], "NXdetector")
            self.assertTrue(
                isinstance(attr, H5PYWriter.H5PYAttributeManager))
            self.assertEqual(det.is_valid, True)
            self.assertEqual(det.parent, ins)
            self.assertEqual(det.size, 6)
            self.assertEqual(det.exists("strimage"), True)
            self.assertEqual(det.exists("intvec"), True)
            self.assertEqual(det.exists("floatimage"), True)
            self.assertEqual(det.exists("floatvec"), True)
            self.assertEqual(det.exists("intimage"), True)
            self.assertEqual(det.exists("strvec"), True)
            self.assertEqual(det.exists("strument"), False)

            kids = set()
            for en in det:
                kids.add(en.name)
            print kids

            self.assertEqual(
                kids,
                set(['strimage', 'intvec', 'floatimage',
                     'floatvec', 'intimage', 'strvec']))



            self.assertTrue(isinstance(strscalar, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strscalar.h5object, h5py.Dataset))
            self.assertEqual(strscalar.name, 'strscalar')
            self.assertEqual(strscalar.path, '/entry12345:NXentry/strscalar')
            self.assertEqual(strscalar.dtype, 'string')
            self.assertEqual(strscalar.shape, (1,))

            self.assertTrue(isinstance(floatscalar, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatscalar.h5object, h5py.Dataset))
            self.assertEqual(floatscalar.name, 'floatscalar')
            self.assertEqual(floatscalar.path, '/entry12345:NXentry/floatscalar')
            self.assertEqual(floatscalar.dtype, 'float64')
            self.assertEqual(floatscalar.shape, (1,))

            self.assertTrue(isinstance(intscalar, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intscalar.h5object, h5py.Dataset))
            self.assertEqual(intscalar.name, 'intscalar')
            self.assertEqual(intscalar.path, '/entry12345:NXentry/intscalar')
            self.assertEqual(intscalar.dtype, 'uint64')
            self.assertEqual(intscalar.shape, (1,))

            self.assertTrue(isinstance(strspec, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strspec.h5object, h5py.Dataset))
            self.assertEqual(strspec.name, 'strspec')
            self.assertEqual(strspec.path, '/entry12345:NXentry/instrument:NXinstrument/strspec')
            self.assertEqual(strspec.dtype, 'string')
            self.assertEqual(strspec.shape, (10,))

            self.assertTrue(isinstance(floatspec, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatspec.h5object, h5py.Dataset))
            self.assertEqual(floatspec.name, 'floatspec')
            self.assertEqual(floatspec.path, '/entry12345:NXentry/instrument:NXinstrument/floatspec')
            self.assertEqual(floatspec.dtype, 'float32')
            self.assertEqual(floatspec.shape, (20,))

            self.assertTrue(isinstance(intspec, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intspec.h5object, h5py.Dataset))
            self.assertEqual(intspec.name, 'intspec')
            self.assertEqual(intspec.path, '/entry12345:NXentry/instrument:NXinstrument/intspec')
            self.assertEqual(intspec.dtype, 'int64')
            self.assertEqual(intspec.shape, (30,))


            self.assertTrue(isinstance(strimage, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strimage.h5object, h5py.Dataset))
            self.assertEqual(strimage.name, 'strimage')
            self.assertEqual(strimage.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strimage')
            self.assertEqual(strimage.dtype, 'string')
            self.assertEqual(strimage.shape, (2, 2))

            self.assertTrue(isinstance(floatimage, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatimage.h5object, h5py.Dataset))
            self.assertEqual(floatimage.name, 'floatimage')
            self.assertEqual(floatimage.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatimage')
            self.assertEqual(floatimage.dtype, 'float64')
            self.assertEqual(floatimage.shape, (20, 10))

            self.assertTrue(isinstance(intimage, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intimage.h5object, h5py.Dataset))
            self.assertEqual(intimage.name, 'intimage')
            self.assertEqual(intimage.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intimage')
            self.assertEqual(intimage.dtype, 'uint32')
            self.assertEqual(intimage.shape, (0, 30))





            self.assertTrue(isinstance(strvec, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strvec.h5object, h5py.Dataset))
            self.assertEqual(strvec.name, 'strvec')
            self.assertEqual(strvec.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strvec')
            self.assertEqual(strvec.dtype, 'string')
            self.assertEqual(strvec.shape, (0, 2, 2))

            self.assertTrue(isinstance(floatvec, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatvec.h5object, h5py.Dataset))
            self.assertEqual(floatvec.name, 'floatvec')
            self.assertEqual(floatvec.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatvec')
            self.assertEqual(floatvec.dtype, 'float64')
            self.assertEqual(floatvec.shape, (1, 20, 10))

            self.assertTrue(isinstance(intvec, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intvec.h5object, h5py.Dataset))
            self.assertEqual(intvec.name, 'intvec')
            self.assertEqual(intvec.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intvec')
            self.assertEqual(intvec.dtype, 'uint32')
            self.assertEqual(intvec.shape, (0, 2, 30))


            strscalar_op= entry.open("strscalar")
            floatscalar_op = entry.open("floatscalar")
            intscalar_op = entry.open("intscalar")
            strspec_op = ins.open("strspec")
            floatspec_op = ins.open("floatspec")
            intspec_op = ins.open("intspec")
            strimage_op = det.open("strimage")
            floatimage_op = det.open("floatimage")
            intimage_op = det.open("intimage")
            strvec_op = det.open("strvec")
            floatvec_op = det.open("floatvec")
            intvec_op = det.open("intvec")


            self.assertTrue(isinstance(strscalar_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strscalar_op.h5object, h5py.Dataset))
            self.assertEqual(strscalar_op.name, 'strscalar')
            self.assertEqual(strscalar_op.path, '/entry12345:NXentry/strscalar')
            self.assertEqual(strscalar_op.dtype, 'string')
            self.assertEqual(strscalar_op.shape, (1,))

            self.assertTrue(isinstance(floatscalar_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatscalar_op.h5object, h5py.Dataset))
            self.assertEqual(floatscalar_op.name, 'floatscalar')
            self.assertEqual(floatscalar_op.path, '/entry12345:NXentry/floatscalar')
            self.assertEqual(floatscalar_op.dtype, 'float64')
            self.assertEqual(floatscalar_op.shape, (1,))

            self.assertTrue(isinstance(intscalar_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intscalar_op.h5object, h5py.Dataset))
            self.assertEqual(intscalar_op.name, 'intscalar')
            self.assertEqual(intscalar_op.path, '/entry12345:NXentry/intscalar')
            self.assertEqual(intscalar_op.dtype, 'uint64')
            self.assertEqual(intscalar_op.shape, (1,))

            self.assertTrue(isinstance(strspec_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strspec_op.h5object, h5py.Dataset))
            self.assertEqual(strspec_op.name, 'strspec')
            self.assertEqual(strspec_op.path, '/entry12345:NXentry/instrument:NXinstrument/strspec')
            self.assertEqual(strspec_op.dtype, 'string')
            self.assertEqual(strspec_op.shape, (10,))

            self.assertTrue(isinstance(floatspec_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatspec_op.h5object, h5py.Dataset))
            self.assertEqual(floatspec_op.name, 'floatspec')
            self.assertEqual(floatspec_op.path, '/entry12345:NXentry/instrument:NXinstrument/floatspec')
            self.assertEqual(floatspec_op.dtype, 'float32')
            self.assertEqual(floatspec_op.shape, (20,))

            self.assertTrue(isinstance(intspec_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intspec_op.h5object, h5py.Dataset))
            self.assertEqual(intspec_op.name, 'intspec')
            self.assertEqual(intspec_op.path, '/entry12345:NXentry/instrument:NXinstrument/intspec')
            self.assertEqual(intspec_op.dtype, 'int64')
            self.assertEqual(intspec_op.shape, (30,))


            self.assertTrue(isinstance(strimage_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strimage_op.h5object, h5py.Dataset))
            self.assertEqual(strimage_op.name, 'strimage')
            self.assertEqual(strimage_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strimage')
            self.assertEqual(strimage_op.dtype, 'string')
            self.assertEqual(strimage_op.shape, (2, 2))

            self.assertTrue(isinstance(floatimage_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatimage_op.h5object, h5py.Dataset))
            self.assertEqual(floatimage_op.name, 'floatimage')
            self.assertEqual(floatimage_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatimage')
            self.assertEqual(floatimage_op.dtype, 'float64')
            self.assertEqual(floatimage_op.shape, (20, 10))

            self.assertTrue(isinstance(intimage_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intimage_op.h5object, h5py.Dataset))
            self.assertEqual(intimage_op.name, 'intimage')
            self.assertEqual(intimage_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intimage')
            self.assertEqual(intimage_op.dtype, 'uint32')
            self.assertEqual(intimage_op.shape, (0, 30))



            self.assertTrue(isinstance(strvec_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(strvec_op.h5object, h5py.Dataset))
            self.assertEqual(strvec_op.name, 'strvec')
            self.assertEqual(strvec_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/strvec')
            self.assertEqual(strvec_op.dtype, 'string')
            self.assertEqual(strvec_op.shape, (0, 2, 2))

            self.assertTrue(isinstance(floatvec_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(floatvec_op.h5object, h5py.Dataset))
            self.assertEqual(floatvec_op.name, 'floatvec')
            self.assertEqual(floatvec_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/floatvec')
            self.assertEqual(floatvec_op.dtype, 'float64')
            self.assertEqual(floatvec_op.shape, (1, 20, 10))

            self.assertTrue(isinstance(intvec_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(intvec_op.h5object, h5py.Dataset))
            self.assertEqual(intvec_op.name, 'intvec')
            self.assertEqual(intvec_op.path, '/entry12345:NXentry/instrument:NXinstrument/detector:NXdetector/intvec')
            self.assertEqual(intvec_op.dtype, 'uint32')
            self.assertEqual(intvec_op.shape, (0, 2, 30))
            self.assertEqual(intvec_op.parent, det)



            self.assertTrue(isinstance(lkintimage, H5PYWriter.H5PYLink))
            self.assertTrue(isinstance(lkintimage.h5object, h5py.SoftLink))
            self.assertTrue(lkintimage.target_path.endswith(
                "%s://entry12345/instrument/detector/intimage" % self._fname))
            self.assertEqual(
                lkintimage.path,
                "/entry12345:NXentry/data:NXdata/lkintimage")

            self.assertTrue(isinstance(lkfloatvec, H5PYWriter.H5PYLink))
            self.assertTrue(isinstance(lkfloatvec.h5object, h5py.SoftLink))
            self.assertTrue(lkfloatvec.target_path.endswith(
                "%s://entry12345/instrument/detector/floatvec" % self._fname))
            self.assertEqual(
                lkfloatvec.path,
                "/entry12345:NXentry/data:NXdata/lkfloatvec")

            self.assertTrue(isinstance(lkintspec, H5PYWriter.H5PYLink))
            self.assertTrue(isinstance(lkintspec.h5object, h5py.SoftLink))
            self.assertTrue(lkintspec.target_path.endswith(
                "%s://entry12345/instrument/intspec" % self._fname))
            self.assertEqual(
                lkintspec.path,
                "/entry12345:NXentry/data:NXdata/lkintspec")

            self.assertTrue(isinstance(lkdet, H5PYWriter.H5PYLink))
            self.assertTrue(isinstance(lkdet.h5object, h5py.SoftLink))
            self.assertTrue(lkdet.target_path.endswith(
                "%s://entry12345/instrument/detector" % self._fname))
            self.assertEqual(
                lkdet.path,
                "/entry12345:NXentry/data:NXdata/lkdet")

            self.assertTrue(isinstance(lkno, H5PYWriter.H5PYLink))
            self.assertTrue(isinstance(lkno.h5object, h5py.SoftLink))
            self.assertTrue(lkno.target_path.endswith(
                "%s://notype/unknown" % self._fname))
            self.assertEqual(
                lkno.path,
                "/entry12345:NXentry/data:NXdata/lkno")



            lkintimage_op = dt.open("lkintimage")
            lkfloatvec_op = dt.open("lkfloatvec")
            lkintspec_op = dt.open("lkintspec")
            lkdet_op = dt.open("lkdet")
            lkno_op = dt.open("lkno")



            self.assertTrue(isinstance(lkintimage_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(lkintimage_op.h5object, h5py.Dataset))
            self.assertEqual(lkintimage_op.name, 'lkintimage')
            self.assertEqual(
                lkintimage_op.path,
                '/entry12345:NXentry/data:NXdata/lkintimage')
            self.assertEqual(lkintimage_op.dtype, 'uint32')
            self.assertEqual(lkintimage_op.shape, (0, 30))


            self.assertTrue(isinstance(lkfloatvec_op, H5PYWriter.H5PYField))
            self.assertTrue(isinstance(lkfloatvec_op.h5object, h5py.Dataset))
            self.assertEqual(lkfloatvec_op.name, 'lkfloatvec')
            self.assertEqual(lkfloatvec_op.path,
                             '/entry12345:NXentry/data:NXdata/lkfloatvec')
            self.assertEqual(lkfloatvec_op.dtype, 'float64')
            self.assertEqual(lkfloatvec_op.shape, (1, 20, 10))


            self.assertTrue(
                isinstance(lkintspec_op, H5PYWriter.H5PYField))
            self.assertTrue(
                isinstance(lkintspec_op.h5object, h5py.Dataset))
            self.assertEqual(lkintspec_op.name, 'lkintspec')
            self.assertEqual(lkintspec_op.path,
                             '/entry12345:NXentry/data:NXdata/lkintspec')
            self.assertEqual(lkintspec_op.dtype, 'int64')
            self.assertEqual(lkintspec_op.shape, (30,))

            self.assertTrue(isinstance(lkno_op, H5PYWriter.H5PYLink))
            self.assertTrue(isinstance(lkno_op.h5object, h5py.SoftLink))
            self.assertTrue(lkno_op.target_path.endswith(
                "%s://notype/unknown" % self._fname))
            self.assertEqual(
                lkno_op.path,
                "/entry12345:NXentry/data:NXdata/lkno")


            entry.close()
            self.assertEqual(rt.is_valid, True)
            self.assertEqual(entry.is_valid, False)
            self.assertEqual(dt.is_valid, False)


            entry.reopen()
            self.assertEqual(rt.is_valid, True)
            self.assertEqual(entry.is_valid, True)
            self.assertEqual(dt.is_valid, True)

            fl.reopen()
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, h5py.File))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, False)

            fl.close()

            fl.reopen(True)
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.h5object, h5py.File))
            self.assertEqual(fl.parent, None)
            self.assertEqual(fl.readonly, True)

            fl.close()

            self.myAssertRaise(
                Exception, fl.reopen, True, True)
            self.myAssertRaise(
                Exception, fl.reopen, False, True)


            fl = H5PYWriter.open_file(self._fname, readonly=True)
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
