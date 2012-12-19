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
## \file Checkers.py
# checkers for unittests
#
import os
from pni.nx.h5 import open_file
import unittest
from ndts import Types




## checks for scalar attributes
class ScalarChecker(object):

    ## constructor
    # \param methodName name of the test method
    def __init__(self, testCase):
        ## test case
        self._tc = testCase 


    ## checks scalar tree
    # \param f pninx file object    
    # \param fname file name
    # \returns detector group object    
    def _checkScalarTree(self, f, fname, children):
        self._tc.assertEqual("%s/%s" % ( os.getcwd(), f.name), fname)
        self._tc.assertEqual(6, f.nattrs)
        self._tc.assertEqual( f.attr("file_name").value, fname)
        self._tc.assertTrue(f.attr("NX_class").value,"NXroot")
        self._tc.assertEqual(f.nchildren, 2)
            
        en = f.open("entry1")
        self._tc.assertTrue(en.valid)
        self._tc.assertEqual(en.name,"entry1")
        self._tc.assertEqual(en.nattrs,1)
        self._tc.assertEqual(en.nchildren, 1)

        at = en.attr("NX_class")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")
        self._tc.assertEqual(at.name,"NX_class")
        self._tc.assertEqual(at.value,"NXentry")

        ins = en.open("instrument")
        self._tc.assertTrue(ins.valid)
        self._tc.assertEqual(ins.name,"instrument")
        self._tc.assertEqual(ins.nattrs,1)
        self._tc.assertEqual(ins.nchildren, 1)
        
            
        at = ins.attr("NX_class")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")
        self._tc.assertEqual(at.name,"NX_class")
        self._tc.assertEqual(at.value,"NXinstrument")

        det = ins.open("detector")
        self._tc.assertTrue(det.valid)
        self._tc.assertEqual(det.name,"detector")
        self._tc.assertEqual(det.nattrs,1)
        self._tc.assertEqual(det.nchildren, children)
            
        at = det.attr("NX_class")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")
        self._tc.assertEqual(at.name,"NX_class")
        self._tc.assertEqual(at.value,"NXdetector")
            
        return det


    ## checks if instance is numeric
    # \param checking instance 
    # \returns is instance is numeric
    def _isNumeric(self, instance):
        attrs = ['__pow__', '__mul__', '__div__','__add__', '__sub__']
        return all(hasattr(instance, attr) for attr in attrs)

    ## checks  scalar counter
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param unsigned flag if value is integer
    def _checkScalarCounter(self, det, name, dtype, nxtype, values, error = 0):

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (len(values),))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(values))        
        # pninx is not supporting reading string areas 
        if not isinstance(values[0], str):
            value = cnt.read()
            for i in range(len(value)):
                #            print values[i].__repr__(),  value[i].__repr__(), values[i] - value[i]
                if self._isNumeric(value[i]):
                    self._tc.assertTrue(abs(values[i] - value[i]) <= error)
                else:
                    self._tc.assertEqual(values[i],value[i])
        for i in range(len(values)):
            if self._isNumeric(cnt[i]):
                if not self._isNumeric(values[i]):
#                    print "BOOL: ", values[i] ,cnt[i]
                    self._tc.assertEqual(Types.Converters.toBool(values[i]),cnt[i])
                else:
                    self._tc.assertTrue(abs(values[i] - cnt[i]) <= error)
            else:
                self._tc.assertEqual(values[i],cnt[i])
            


        self._tc.assertEqual(cnt.nattrs,3)

        at = cnt.attr("type")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")
        self._tc.assertEqual(at.name,"type")
        self._tc.assertEqual(at.value,nxtype)
        

        at = cnt.attr("units")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")
        self._tc.assertEqual(at.name,"units")
        self._tc.assertEqual(at.value,"m")
        
        at = cnt.attr("nexdatas_source")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")
        

