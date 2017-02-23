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
        self.children.append(weakref.ref(g))
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
        self.children.append(weakref.ref(g))
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

    ## default createfile test
    # \brief It tests default settings
    def test_ftobject(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        fto = FileWriter.FTObject(None)
        self.assertEqual(fto._h5object, None)
        self.assertEqual(fto.getobject(), None)
        self.assertEqual(fto._tparent, None)
        self.assertEqual(fto.getparent(), None)
        self.assertEqual(fto.is_valid, True)
        self.assertEqual(fto.children, [])
        fto2 = FileWriter.FTObject(fto)
        self.assertEqual(fto2._h5object, fto)
        self.assertEqual(fto2.getobject(), fto)
        self.assertEqual(fto2._tparent, None)
        self.assertEqual(fto2.getparent(), None)
        self.assertEqual(fto2.children, [])
        self.assertEqual(fto.is_valid, True)
        fto3 = FileWriter.FTObject(fto2, fto)
        self.assertEqual(fto3._h5object, fto2)
        self.assertEqual(fto3.getobject(), fto2)
        self.assertEqual(fto3._tparent, fto)
        self.assertEqual(fto3.getparent(), fto)
        self.assertEqual(fto3.children, [])
        self.assertEqual(fto.is_valid, True)

    ## default createfile test
    # \brief It tests default settings
    def test_ftcloser(self):
        fun = sys._getframe().f_code.co_name
        print "Run: %s.%s() " % (self.__class__.__name__, fun)

        fto = FTCloser(None)
        self.assertEqual(fto._h5object, None)
        self.assertEqual(fto.getobject(), None)
        self.assertEqual(fto._tparent, None)
        self.assertEqual(fto.getparent(), None)
        self.assertEqual(fto.children, [])
        self.assertEqual(fto.is_valid, True)
        fto2 = fto.create()
        self.assertEqual(fto2._h5object, fto.commands)
        self.assertEqual(fto2.getobject(), fto.commands)
        self.assertEqual(fto2._tparent, fto)
        self.assertEqual(fto2.getparent(), fto)
        self.assertEqual(fto2.children, [])
        self.assertEqual(fto.is_valid, True)
        fto3 = fto2.create()
        self.assertEqual(fto3._h5object, fto2.commands)
        self.assertEqual(fto3.getobject(), fto2.commands)
        self.assertEqual(fto3._tparent, fto2)
        self.assertEqual(fto3.getparent(), fto2)
        self.assertEqual(fto3.children, [])
        self.assertEqual(fto.is_valid, True)
        fto4 = fto2.create()
        self.assertEqual(fto4._h5object, fto2.commands)
        self.assertEqual(fto4.getobject(), fto2.commands)
        self.assertEqual(fto4._tparent, fto2)
        self.assertEqual(fto4.getparent(), fto2)
        self.assertEqual(fto4.children, [])
        self.assertEqual(fto.is_valid, True)

        self.assertEqual(len(fto.children), 1)
        self.assertEqual(fto.children[0](), fto2)
        self.assertEqual(len(fto2.children), 2)
        self.assertEqual(fto2.children[0](), fto3)
        self.assertEqual(fto2.children[1](), fto4)
        self.assertEqual(len(fto3.children), 0)
        self.assertEqual(len(fto4.children), 0)
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
        self.assertEqual(fto.getobject(), None)
        self.assertEqual(fto.getparent(), None)
        self.assertEqual(fto.children, [])
        self.assertEqual(fto.is_valid, True)

        tf = TFile(fto, "myfile.txt")
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.getobject(), fto)
        self.assertEqual(tf.getparent(), None)
        self.assertEqual(tf.children, [])
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.name, "myfile.txt")
        self.assertTrue(hasattr(tf.root, "__call__"))
        self.assertTrue(hasattr(tf.flush, "__call__"))
        self.assertTrue(hasattr(tf, "readonly"))
        self.assertTrue(hasattr(tf.reopen, "__call__"))

        ta = tf.create(TAttribute)
        self.assertEqual(ta._h5object, tf.commands)
        self.assertEqual(ta.getobject(), tf.commands)
        self.assertEqual(ta._tparent, tf)
        self.assertEqual(ta.getparent(), tf)
        self.assertEqual(ta.children, [])
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
        self.assertEqual(tg.getobject(), tf.commands)
        self.assertEqual(tg._tparent, tf)
        self.assertEqual(tg.getparent(), tf)
        self.assertEqual(tg.children, [])
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
        self.assertEqual(td.getobject(), tf.commands)
        self.assertEqual(td._tparent, tf)
        self.assertEqual(td.getparent(), tf)
        self.assertEqual(td.children, [])
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
        self.assertEqual(td2.getobject(), tg.commands)
        self.assertEqual(td2._tparent, tg)
        self.assertEqual(td2.getparent(), tg)
        self.assertEqual(td2.children, [])
        self.assertEqual(td2.is_valid, True)

        tl = tf.create(TLink)
        self.assertEqual(tl._h5object, tf.commands)
        self.assertEqual(tl.getobject(), tf.commands)
        self.assertEqual(tl._tparent, tf)
        self.assertEqual(tl.getparent(), tf)
        self.assertEqual(tl.children, [])
        self.assertEqual(tl.is_valid, True)

        tm = tg.create(TAttributeManager)
        self.assertEqual(tm._h5object, tg.commands)
        self.assertEqual(tm.getobject(), tg.commands)
        self.assertEqual(tm._tparent, tg)
        self.assertEqual(tm.getparent(), tg)
        self.assertEqual(tm.children, [])
        self.assertEqual(tm.is_valid, True)

        ta2 = tg.create(TAttribute)
        self.assertEqual(ta2._h5object, tg.commands)
        self.assertEqual(ta2.getobject(), tg.commands)
        self.assertEqual(ta2._tparent, tg)
        self.assertEqual(ta2.getparent(), tg)
        self.assertEqual(ta2.children, [])
        self.assertEqual(ta2.is_valid, True)

        self.assertTrue(isinstance(tf, FileWriter.FTObject))
        self.assertTrue(isinstance(tf, FileWriter.FTFile))
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.getobject(), fto)
        self.assertEqual(tf.getparent(), None)
        self.assertEqual(len(tf.children), 4)
        self.assertEqual(tf.children[0](), ta)
        self.assertEqual(tf.children[1](), tg)
        self.assertEqual(tf.children[2](), td)
        self.assertEqual(tf.children[3](), tl)
        self.assertEqual(tf.commands, ['create','create','create','create'])

        self.assertTrue(isinstance(ta, FileWriter.FTObject))
        self.assertTrue(isinstance(ta, FileWriter.FTAttribute))
        self.assertEqual(ta.is_valid, True)
        self.assertEqual(ta.getobject(), tf.commands)
        self.assertEqual(ta.getparent(), tf)
        self.assertEqual(len(ta.children), 0)
        self.assertEqual(ta.commands, [])

        self.assertTrue(isinstance(td, FileWriter.FTObject))
        self.assertTrue(isinstance(td, FileWriter.FTField))
        self.assertEqual(td.is_valid, True)
        self.assertEqual(td.getobject(), tf.commands)
        self.assertEqual(td.getparent(), tf)
        self.assertEqual(len(td.children), 0)
        self.assertEqual(td.commands, [])

        self.assertTrue(isinstance(tl, FileWriter.FTObject))
        self.assertTrue(isinstance(tl, FileWriter.FTLink))
        self.assertEqual(tl.is_valid, True)
        self.assertEqual(tl.getobject(), tf.commands)
        self.assertEqual(tl.getparent(), tf)
        self.assertEqual(len(tl.children), 0)
        self.assertEqual(tl.commands, [])

        self.assertTrue(isinstance(tg, FileWriter.FTObject))
        self.assertTrue(isinstance(tg, FileWriter.FTGroup))
        self.assertEqual(tg.is_valid, True)
        self.assertEqual(tg.getobject(), tf.commands)
        self.assertEqual(tg.getparent(), tf)
        self.assertEqual(len(tg.children), 3)
        self.assertEqual(tg.children[0](), td2)
        self.assertEqual(tg.children[1](), tm)
        self.assertEqual(tg.children[2](), ta2)
        self.assertEqual(tg.commands, ['create','create','create'])

        self.assertTrue(isinstance(td2, FileWriter.FTObject))
        self.assertTrue(isinstance(td2, FileWriter.FTField))
        self.assertEqual(td2.is_valid, True)
        self.assertEqual(td2.getobject(), tg.commands)
        self.assertEqual(td2.getparent(), tg)
        self.assertEqual(len(td2.children), 0)
        self.assertEqual(td2.commands, [])

        self.assertTrue(isinstance(tm, FileWriter.FTObject))
        self.assertTrue(isinstance(tm, FileWriter.FTAttributeManager))
        self.assertEqual(tm.is_valid, True)
        self.assertEqual(tm.getobject(), tg.commands)
        self.assertEqual(tm.getparent(), tg)
        self.assertEqual(len(tm.children), 0)
        self.assertEqual(tm.commands, [])

        self.assertTrue(isinstance(ta2, FileWriter.FTObject))
        self.assertTrue(isinstance(ta2, FileWriter.FTAttribute))
        self.assertEqual(ta2.is_valid, True)
        self.assertEqual(ta2.getobject(), tg.commands)
        self.assertEqual(ta2.getparent(), tg)
        self.assertEqual(len(ta2.children), 0)
        self.assertEqual(ta2.commands, [])

        tf.close()

        self.assertTrue(isinstance(tf, FileWriter.FTObject))
        self.assertTrue(isinstance(tf, FileWriter.FTFile))
        self.assertEqual(tf.is_valid, False)
        self.assertEqual(tf.getobject(), fto)
        self.assertEqual(tf.getparent(), None)
        self.assertEqual(len(tf.children), 4)
        self.assertEqual(tf.children[0](), ta)
        self.assertEqual(tf.children[1](), tg)
        self.assertEqual(tf.children[2](), td)
        self.assertEqual(tf.children[3](), tl)
        self.assertEqual(
            tf.commands,
            ['create','create','create','create', 'close'])

        self.assertTrue(isinstance(ta, FileWriter.FTObject))
        self.assertTrue(isinstance(ta, FileWriter.FTAttribute))
        self.assertEqual(ta.is_valid, False)
        self.assertEqual(ta.getobject(), tf.commands)
        self.assertEqual(ta.getparent(), tf)
        self.assertEqual(len(ta.children), 0)
        self.assertEqual(ta.commands, ['close'])

        self.assertTrue(isinstance(td, FileWriter.FTObject))
        self.assertTrue(isinstance(td, FileWriter.FTField))
        self.assertEqual(td.is_valid, False)
        self.assertEqual(td.getobject(), tf.commands)
        self.assertEqual(td.getparent(), tf)
        self.assertEqual(len(td.children), 0)
        self.assertEqual(td.commands, ['close'])

        self.assertTrue(isinstance(tl, FileWriter.FTObject))
        self.assertTrue(isinstance(tl, FileWriter.FTLink))
        self.assertEqual(tl.is_valid, False)
        self.assertEqual(tl.getobject(), tf.commands)
        self.assertEqual(tl.getparent(), tf)
        self.assertEqual(len(tl.children), 0)
        self.assertEqual(tl.commands, ['close'])

        self.assertTrue(isinstance(tg, FileWriter.FTObject))
        self.assertTrue(isinstance(tg, FileWriter.FTGroup))
        self.assertEqual(tg.is_valid, False)
        self.assertEqual(tg.getobject(), tf.commands)
        self.assertEqual(tg.getparent(), tf)
        self.assertEqual(len(tg.children), 3)
        self.assertEqual(tg.children[0](), td2)
        self.assertEqual(tg.children[1](), tm)
        self.assertEqual(tg.children[2](), ta2)
        self.assertEqual(
            tg.commands, ['create','create','create', 'close'])

        self.assertTrue(isinstance(td2, FileWriter.FTObject))
        self.assertTrue(isinstance(td2, FileWriter.FTField))
        self.assertEqual(td2.is_valid, False)
        self.assertEqual(td2.getobject(), tg.commands)
        self.assertEqual(td2.getparent(), tg)
        self.assertEqual(len(td2.children), 0)
        self.assertEqual(td2.commands, ['close'])

        self.assertTrue(isinstance(tm, FileWriter.FTObject))
        self.assertTrue(isinstance(tm, FileWriter.FTAttributeManager))
        self.assertEqual(tm.is_valid, False)
        self.assertEqual(tm.getobject(), tg.commands)
        self.assertEqual(tm.getparent(), tg)
        self.assertEqual(len(tm.children), 0)
        self.assertEqual(tm.commands, ['close'])

        self.assertTrue(isinstance(ta2, FileWriter.FTObject))
        self.assertTrue(isinstance(ta2, FileWriter.FTAttribute))
        self.assertEqual(ta2.is_valid, False)
        self.assertEqual(ta2.getobject(), tg.commands)
        self.assertEqual(ta2.getparent(), tg)
        self.assertEqual(len(ta2.children), 0)
        self.assertEqual(ta2.commands, ['close'])

        tf.reopen()
        
        self.assertTrue(isinstance(tf, FileWriter.FTObject))
        self.assertTrue(isinstance(tf, FileWriter.FTFile))
        self.assertEqual(tf.is_valid, True)
        self.assertEqual(tf.getobject(), fto)
        self.assertEqual(tf.getparent(), None)
        self.assertEqual(len(tf.children), 4)
        self.assertEqual(tf.children[0](), ta)
        self.assertEqual(tf.children[1](), tg)
        self.assertEqual(tf.children[2](), td)
        self.assertEqual(tf.children[3](), tl)
        self.assertEqual(
            tf.commands,
            ['create','create','create','create', 'close', 'reopen'])

        self.assertTrue(isinstance(ta, FileWriter.FTObject))
        self.assertTrue(isinstance(ta, FileWriter.FTAttribute))
        self.assertEqual(ta.is_valid, True)
        self.assertEqual(ta.getobject(), tf.commands)
        self.assertEqual(ta.getparent(), tf)
        self.assertEqual(len(ta.children), 0)
        self.assertEqual(ta.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(td, FileWriter.FTObject))
        self.assertTrue(isinstance(td, FileWriter.FTField))
        self.assertEqual(td.is_valid, True)
        self.assertEqual(td.getobject(), tf.commands)
        self.assertEqual(td.getparent(), tf)
        self.assertEqual(len(td.children), 0)
        self.assertEqual(td.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(tl, FileWriter.FTObject))
        self.assertTrue(isinstance(tl, FileWriter.FTLink))
        self.assertEqual(tl.is_valid, True)
        self.assertEqual(tl.getobject(), tf.commands)
        self.assertEqual(tl.getparent(), tf)
        self.assertEqual(len(tl.children), 0)
        self.assertEqual(tl.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(tg, FileWriter.FTObject))
        self.assertTrue(isinstance(tg, FileWriter.FTGroup))
        self.assertEqual(tg.is_valid, True)
        self.assertEqual(tg.getobject(), tf.commands)
        self.assertEqual(tg.getparent(), tf)
        self.assertEqual(len(tg.children), 3)
        self.assertEqual(tg.children[0](), td2)
        self.assertEqual(tg.children[1](), tm)
        self.assertEqual(tg.children[2](), ta2)
        self.assertEqual(
            tg.commands, ['create','create','create', 'close', 'reopen'])

        self.assertTrue(isinstance(td2, FileWriter.FTObject))
        self.assertTrue(isinstance(td2, FileWriter.FTField))
        self.assertEqual(td2.is_valid, True)
        self.assertEqual(td2.getobject(), tg.commands)
        self.assertEqual(td2.getparent(), tg)
        self.assertEqual(len(td2.children), 0)
        self.assertEqual(td2.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(tm, FileWriter.FTObject))
        self.assertTrue(isinstance(tm, FileWriter.FTAttributeManager))
        self.assertEqual(tm.is_valid, True)
        self.assertEqual(tm.getobject(), tg.commands)
        self.assertEqual(tm.getparent(), tg)
        self.assertEqual(len(tm.children), 0)
        self.assertEqual(tm.commands, ['close', 'reopen'])

        self.assertTrue(isinstance(ta2, FileWriter.FTObject))
        self.assertTrue(isinstance(ta2, FileWriter.FTAttribute))
        self.assertEqual(ta2.is_valid, True)
        self.assertEqual(ta2.getobject(), tg.commands)
        self.assertEqual(ta2.getparent(), tg)
        self.assertEqual(len(ta2.children), 0)
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
                isinstance(fl.getobject(), h5py.File))
            self.assertEqual(fl.getparent(), None)
            self.assertEqual(fl.children, [])

            rt = fl.root()
            fl.flush()
            self.assertEqual(fl.getobject(), rt.getobject())
            self.assertEqual(len(fl.children), 1)
            self.assertEqual(fl.children[0](), rt)
            self.assertEqual(fl.is_valid, True)
            self.assertEqual(fl.getobject().name is not None, True)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.getobject().mode in ["r"], False)
            fl.close()
            self.assertEqual(fl.is_valid, False)
            self.assertEqual(fl.readonly, None)

            fl.reopen()
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.getobject(), h5py.File))
            self.assertEqual(fl.getparent(), None)
            self.assertEqual(len(fl.children), 1)
            self.assertEqual(fl.children[0](), rt)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.getobject().mode in ["r"], False)

            fl.close()

            fl.reopen(True)
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.getobject(), h5py.File))
            self.assertEqual(fl.getparent(), None)
            self.assertEqual(len(fl.children), 1)
            self.assertEqual(fl.children[0](), rt)
            self.assertEqual(fl.readonly, True)
            self.assertEqual(fl.getobject().mode in ["r"], True)

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
                isinstance(fl.getobject(), nx._nxh5.nxfile))
            self.assertEqual(fl.getparent(), None)
            self.assertEqual(fl.children, [])

            rt = fl.root()
            fl.flush()
            self.assertEqual(
                fl.getobject().root().filename,
                rt.getobject().filename)
            self.assertEqual(
                fl.getobject().root().name,
                rt.getobject().name)
            self.assertEqual(
                fl.getobject().root().path,
                rt.getobject().path)
            self.assertEqual(
                len(fl.getobject().root().attributes),
                len(rt.getobject().attributes))
            self.assertEqual(len(fl.children), 1)
            self.assertEqual(fl.children[0](), rt)
            self.assertEqual(fl.is_valid, True)
            self.assertEqual(fl.getobject().is_valid, True)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.getobject().readonly, False)
            fl.close()
            self.assertEqual(fl.is_valid, False)
            self.assertEqual(fl.getobject().is_valid, False)

            fl.reopen()
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.getobject(), nx._nxh5.nxfile))
            self.assertEqual(fl.getparent(), None)
            self.assertEqual(len(fl.children), 1)
            self.assertEqual(fl.children[0](), rt)
            self.assertEqual(fl.readonly, False)
            self.assertEqual(fl.getobject().readonly, False)

            fl.close()

            fl.reopen(True)
            self.assertEqual(fl.name, self._fname)
            self.assertEqual(fl.path, None)
            self.assertTrue(
                isinstance(fl.getobject(), nx._nxh5.nxfile))
            self.assertEqual(fl.getparent(), None)
            self.assertEqual(len(fl.children), 1)
            self.assertEqual(fl.children[0](), rt)
            self.assertEqual(fl.readonly, True)
            self.assertEqual(fl.getobject().readonly, True)

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

if __name__ == '__main__':
    unittest.main()
