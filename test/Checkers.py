#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
import random
import unittest
import binascii
import time

try:
    from pni.io.nx.h5 import open_file
except:
    from pni.nx.h5 import open_file


from nxswriter import Types

from math import exp


## checks for scalar attributes
class Checker(object):

    ## constructor
    # \param testCase TestCase instance
    def __init__(self, testCase):
        ## test case
        self._tc = testCase 

        try:
            ## random seed
            self.seed  = long(binascii.hexlify(os.urandom(16)), 16)
        except NotImplementedError:
            import time
            self.seed  = long(time.time() * 256) # use fractional seconds
#        self.seed = 113927724434234094860192629108901591122
        self.__rnd = random.Random(self.seed)


    ## checks field tree
    # \param f pninx file object    
    # \param fname file name
    # \param children number of detector children   
    # \returns detector group object    
    def checkFieldTree(self, f, fname, children):
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


    ## checks attribute tree
    # \param f pninx file object    
    # \param fname file name
    # \param gattributes number of group attributes
    # \param fattributes number of field attributes
    # \returns detector group object    
    def checkAttributeTree(self, f, fname, gattributes, fattributes):
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
        self._tc.assertEqual(ins.nchildren, 2)
        
            
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
        self._tc.assertEqual(det.nattrs, 1 + gattributes)
        self._tc.assertEqual(det.nchildren, 0)

        det = ins.open("detector")
        self._tc.assertTrue(det.valid)
        self._tc.assertEqual(det.name,"detector")
        self._tc.assertEqual(det.nattrs, 1 + gattributes)
        self._tc.assertEqual(det.nchildren, 0)


        field = ins.open("counter")
        self._tc.assertTrue(field.valid)
        self._tc.assertEqual(field.name,"counter")
        self._tc.assertEqual(field.nattrs, 1 + fattributes)
            
        at = det.attr("NX_class")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")
        self._tc.assertEqual(at.name,"NX_class")
        self._tc.assertEqual(at.value,"NXdetector")
            
        return det,field



    ## checks  scalar attributer
    # \param det detector group
    # \param name field name
    # \param dtype numpy type
    # \param values  original values
    # \param error data precision
    def checkScalarAttribute(self, det, name, dtype, values, error = 0):

        cnt = det.attr(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
#        print name, "SHAPE", cnt.shape,len(cnt.shape)
        self._tc.assertEqual(len(cnt.shape), 0)
        self._tc.assertEqual(cnt.shape, ())
        self._tc.assertEqual(cnt.dtype, dtype)
        # pninx is not supporting reading string areas 
        if not isinstance(values, str):
            value = cnt.value
            if self._isNumeric(value):
#                print "Val", name , values ,value
                self._tc.assertTrue(abs(values - value) <= error)
            else:
                self._tc.assertEqual(values,value)
        if self._isNumeric(cnt.value):
            if not self._isNumeric(values):
#                    print "BOOL: ", values[i] ,cnt[i]
                self._tc.assertEqual(Types.Converters.toBool(values),cnt.value)
            else:
                self._tc.assertTrue(abs(values - cnt.value) <= error)
        else:
            self._tc.assertEqual(values, cnt.value)
            

    ## checks  spectrum attribute
    # \param det detector group
    # \param name field name
    # \param dtype numpy type
    # \param values  original values
    # \param error data precision
    def checkSpectrumAttribute(self, det, name, dtype, values, error = 0):

        cnt = det.attr(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (len(values),))
        self._tc.assertEqual(cnt.dtype, dtype)
        # pninx is not supporting reading string areas 


        for i in range(len(values)):
#            print name, i, values[i],  cnt.value[i]
            if dtype != "string" and self._isNumeric(cnt.value[i]):
                if dtype == "bool":
                    self._tc.assertEqual(Types.Converters.toBool(values[i]),cnt.value[i])
                else:
#                    print "CMP",cnt.value[i] , values[i] ,cnt.value[i] - values[i] , error
                    self._tc.assertTrue(abs(cnt.value[i] - values[i] ) <= error)
            else:
                self._tc.assertEqual(values[i], cnt.value[i])
            
            


    ## checks  image attribute
    # \param det detector group
    # \param name field name
    # \param dtype numpy type
    # \param values  original values
    # \param error data precision
    def checkImageAttribute(self, det, name, dtype, values, error = 0):

        cnt = det.attr(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 2)
        self._tc.assertEqual(cnt.shape, (len(values),len(values[0])))
        self._tc.assertEqual(cnt.dtype, dtype)
        # pninx is not supporting reading string areas 


        
        for i in range(len(values)):
            for j in range(len(values[i])):
#                print i, j, cnt[i,j], values[i][j]
                if dtype != "string" and self._isNumeric(cnt.value[i,0]):
                    if dtype == "bool":
                        self._tc.assertEqual(Types.Converters.toBool(values[i][j]),cnt.value[i,j])
                    else:
                        self._tc.assertTrue(abs(cnt.value[i,j] -values[i][j]) <= error)
                else:
                    self._tc.assertEqual(values[i][j], cnt.value[i,j])
            








    ## checks if instance is numeric
    # \param checking instance 
    # \returns is instance is numeric
    def _isNumeric(self, instance):
        attrs = ['__pow__', '__mul__', '__div__','__add__', '__sub__']
        return all(hasattr(instance, attr) for attr in attrs)

    ## creates spectrum plot with random Gaussians
    # \param xlen data length 
    # \param nrGauss of Gaussians  
    # \returns list with the plot
    def nicePlot(self, xlen=2048, nrGauss=5):
        pr = [ [ self.__rnd.uniform(0.01,0.001), self.__rnd.uniform(0,xlen), self.__rnd.uniform(0.0,1.) ] \
                   for i in range(nrGauss) ]
        return [ sum([pr[j][2]*exp(-pr[j][0]*(i-pr[j][1])**2) for j in range(len(pr)) ]) \
                     for i in range(xlen)]


    ## creates spectrum plot with random Gaussians
    # \param xlen data x-length 
    # \param ylen data y-length 
    # \param nrGauss of Gaussians  
    # \returns list with the plot
    def nicePlot2D(self, xlen=1024, ylen=1024, nrGauss=5):
        pr = [ [ self.__rnd.uniform(0.1,0.01), self.__rnd.uniform(0.01,0.1), self.__rnd.uniform(0,ylen), self.__rnd.uniform(0,xlen), self.__rnd.uniform(0.0,1.) ] \
                   for i in range(nrGauss) ]
        return [[ sum([pr[j][4]*exp(-pr[j][0]*(i1-pr[j][2])**2-pr[j][1]*(i2-pr[j][3])**2) \
                           for j in range(len(pr)) ]) \
                      for i1 in range(ylen)] for i2 in range(xlen)]


    ## checks  scalar counter
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param attrs dictionary with string attributes    
    def checkScalarField(self, det, name, dtype, nxtype, values, error = 0, attrs = None):

        atts = {"type":nxtype,"units":"m","nexdatas_source":None}
        if attrs is not None:
            atts = attrs
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
#                print values[i].__repr__(),  value[i].__repr__()
#                print values[i].__repr__(),  value[i].__repr__(), value[i] - values[i] ,error
                if self._isNumeric(value[i]):
                    self._tc.assertTrue(abs(value[i] - values[i] ) <= error)
                else:
                    self._tc.assertEqual(values[i],value[i])
        for i in range(len(values)):
            if self._isNumeric(cnt[i]):
                if nxtype == "NX_BOOLEAN":
#                    print "BOOL: ", values[i] ,cnt[i]
                    self._tc.assertEqual(Types.Converters.toBool(values[i]),cnt[i])
                else:
                    self._tc.assertTrue(abs(values[i] - cnt[i]) <= error)
            else:
                self._tc.assertEqual(values[i],cnt[i])
            

        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name,a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])
           




    ## checks  scalar counter
    # \param det detector group
    # \param name field name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param attrs dictionary with string attributes    
    def checkSingleScalarField(self, det, name, dtype, nxtype, values, error = 0, attrs = None):

        atts = {"type":nxtype,"units":"m","nexdatas_source":None}
        if attrs is not None:
            atts = attrs
        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (1,))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, 1)        
        # pninx is not supporting reading string areas 
        if not isinstance(values, str):
            value = cnt.read()
            if self._isNumeric(value):
                self._tc.assertTrue(abs(values - value) <= error)
            else:
                self._tc.assertEqual(values,value)
        if self._isNumeric(cnt.read()):
            if not self._isNumeric(values):
#                    print "BOOL: ", values[i] ,cnt[i]
                self._tc.assertEqual(Types.Converters.toBool(values),cnt.read())
            else:
                self._tc.assertTrue(abs(values - cnt.read()) <= error)
        else:
            self._tc.assertEqual(values, cnt.read())
            


        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])
        

        





    ## checks post scalar counter
    # \param det detector group
    # \param name field name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param attrs dictionary with string attributes    
    def checkPostScalarField(self, det, name, dtype, nxtype, values, error = 0, attrs = None):

        atts = {"type":nxtype,"units":"m","postrun":None}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (1,))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, 1)        
            



        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])

        



    ## checks XML scalar counter
    # \param det detector group
    # \param name field name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param attrs dictionary with string attributes    
    def checkXMLScalarField(self, det, name, dtype, nxtype, values, error = 0, attrs = None):

        atts = {"type":nxtype,"units":"m"}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (1,))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, 1)        
            


        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])

        
        if not isinstance(values, str):
            value = cnt.read()
            if self._isNumeric(value):
                self._tc.assertTrue(abs(values - value) <= error)
            else:
                self._tc.assertEqual(values,value)
        if self._isNumeric(cnt.read()):
            if not self._isNumeric(values):
#                    print "BOOL: ", values[i] ,cnt[i]
                self._tc.assertEqual(Types.Converters.toBool(values),cnt.read())
            else:
                self._tc.assertTrue(abs(values - cnt.read()) <= error)
        else:
            self._tc.assertEqual(values, cnt.read())
            

        





    ## checks  spectrum field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param grows growing dimension
    # \param attrs dictionary with string attributes    
    def checkSpectrumField(self, det, name, dtype, nxtype, values, error = 0, grows = 0, attrs = None):
        atts = {"type":nxtype,"units":"","nexdatas_source":None}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        if grows > 1:
#            lvalues = zip(*values)
            lvalues = map(lambda *row: list(row), *values)
        else:
            lvalues = values
        self._tc.assertEqual(len(cnt.shape), 2)
        self._tc.assertEqual(cnt.shape, (len(lvalues),len(lvalues[0])))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(lvalues)*len(lvalues[0]))        
        # pninx is not supporting reading string areas 


#        print "VAL", lvalues
#        print "VAL2", cnt.read()

        for i in range(len(lvalues)):
            for j in range(len(lvalues[i])):
#                print i, j, cnt[i,j], lvalues[i][j]
                if self._isNumeric(cnt[i,0]):
                    if nxtype == "NX_BOOLEAN":
                        self._tc.assertEqual(Types.Converters.toBool(lvalues[i][j]),cnt[i,j])
                    else:
                        self._tc.assertTrue(abs(cnt[i,j] - lvalues[i][j] ) <= error)
                else:
                    self._tc.assertEqual(lvalues[i][j], cnt[i,j])
            


        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])





    ## checks single spectrum field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values original values
    # \param error data precision
    # \param grows growing dimension
    # \param attrs dictionary with string attributes    
    def checkSingleSpectrumField(self, det, name, dtype, nxtype, values, error = 0, grows = 0, attrs=None):

        atts = {"type":nxtype,"units":"", "nexdatas_source":None}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name, name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (len(values),))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(values))        
        # pninx is not supporting reading string areas 



        
        for i in range(len(values)):
#                print i, j, cnt[i,j], lvalues[i][j]
            if self._isNumeric(cnt[i]):
                if nxtype == "NX_BOOLEAN":
                    self._tc.assertEqual(Types.Converters.toBool(values[i]),cnt[i])
                else:
                    self._tc.assertTrue(abs(values[i] - cnt[i]) <= error)
            else:
                self._tc.assertEqual(values[i], cnt[i])
            

        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])





    ## checks single spectrum field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values original values
    # \param error data precision
    # \param grows growing dimension
    # \param attrs dictionary with string attributes    
    def checkXMLSpectrumField(self, det, name, dtype, nxtype, values, error = 0, grows = 0, attrs = None):

        atts = {"type":nxtype,"units":""}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name, name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (len(values),))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(values))        
        # pninx is not supporting reading string areas 



        
        for i in range(len(values)):
#                print i, j, cnt[i,j], lvalues[i][j]
            if self._isNumeric(cnt[i]):
                if nxtype == "NX_BOOLEAN":
                    self._tc.assertEqual(Types.Converters.toBool(values[i]),cnt[i])
                else:
                    self._tc.assertTrue(abs(values[i] - cnt[i]) <= error)
            else:
                self._tc.assertEqual(values[i], cnt[i])
            


        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])


    ## checks  spectrum field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param attrs dictionary with string attributes    
    def checkStringSpectrumField(self, det, name, dtype, nxtype, values, attrs = None):

        atts = {"type":nxtype,"units":"", "nexdatas_source":None}
        if attrs is not None:
            atts = attrs

        cnts = [ det.open(name +"_"+str(sz) ) for sz in range(len(values[0]))] 

        for sz in range(len(values[0])) :
            self._tc.assertEqual(cnts[sz].name,name +"_"+str(sz))
            

        for cnt in cnts:
            self._tc.assertTrue(cnt.valid)
            self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
            self._tc.assertEqual(len(cnt.shape), 1)
            self._tc.assertEqual(cnt.shape, (len(values),))
            self._tc.assertEqual(cnt.dtype, dtype)
            self._tc.assertEqual(cnt.size, len(values))        

            self._tc.assertEqual(cnt.nattrs,len(atts))
            for a in atts:
                at = cnt.attr(a)
                self._tc.assertTrue(at.valid)
                self._tc.assertTrue(hasattr(at.shape,"__iter__"))
                self._tc.assertEqual(len(at.shape),0)
                self._tc.assertEqual(at.dtype,"string")
                self._tc.assertEqual(at.name, a)
                if atts[a] is not None:
                    self._tc.assertEqual(at.value,atts[a])

            

        
#        print "VAL", values
        for i in range(len(values)):
            for j in range(len(values[i])):
#                print "CNT", cnt[j]
#                print i, j, cnts[j][i],"   "  , values[i][j]
                self._tc.assertEqual(values[i][j], cnts[j][i])
#                self._tc.assertEqual(values[i][j], cnts[j][i])
            


    ## checks  single string spectrum field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param attrs dictionary with string attributes    
    def checkSingleStringSpectrumField(self, det, name, dtype, nxtype, values, attrs = None):

        atts = {"type":nxtype,"units":"", "nexdatas_source":None}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name) 

        self._tc.assertEqual(cnt.name,name )
            

        self._tc.assertTrue(cnt.valid)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 1)
        self._tc.assertEqual(cnt.shape, (len(values),))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(values))        
        
            
        
        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])

        for i in range(len(values)):
#            print "i",i ,values[i], cnt[i]
            self._tc.assertEqual(values[i], cnt[i])
            


        


    ## checks  image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param grows growing dimension
    # \param attrs dictionary with string attributes    
    def checkImageField(self, det, name, dtype, nxtype, values, error = 0, grows = 0 ,attrs = None):

        atts = {"type":nxtype,"units":"","nexdatas_source":None}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        if grows == 3:
            lvalues = map(lambda *image: map(lambda *row: list(row), *image), *values)
        elif grows == 2:
            lvalues = map(lambda *row: list(row), *values)
        else:
            lvalues = values
        self._tc.assertEqual(len(cnt.shape), 3)
        self._tc.assertEqual(cnt.shape, (len(lvalues),len(lvalues[0]),len(lvalues[0][0])))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(lvalues)*len(lvalues[0])*len(lvalues[0][0]))        
        # pninx is not supporting reading string areas 


#        print "LV", lvalues
#        print "CNT",cnt.read()
        
        for i in range(len(lvalues)):
            for j in range(len(lvalues[i])):
                for k in range(len(lvalues[i][j])):
#                print i, j, cnt[i,j], lvalues[i][j]
                    if self._isNumeric(cnt[i,0,0]):
                        if nxtype == "NX_BOOLEAN":
                            self._tc.assertEqual(Types.Converters.toBool(lvalues[i][j][k]),cnt[i,j,k])
                        else:
                            self._tc.assertTrue(abs(lvalues[i][j][k] - cnt[i,j,k]) <= error)
                    else:
                        self._tc.assertEqual(lvalues[i][j][k], cnt[i,j,k])
            

        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])




    ## checks single image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param grows growing dimension
    # \param attrs dictionary with string attributes    
    def checkSingleImageField(self, det, name, dtype, nxtype, values, error = 0, grows = 0, attrs = None):

        atts = {"type":nxtype,"units":"","nexdatas_source":None}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 2)
        self._tc.assertEqual(cnt.shape, (len(values),len(values[0])))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(values)*len(values[0]))        
        # pninx is not supporting reading string areas 



        
        for i in range(len(values)):
            for j in range(len(values[i])):
#                print i, j, cnt[i,j], values[i][j]
                if self._isNumeric(cnt[i,0]):
                    if nxtype == "NX_BOOLEAN":
                        self._tc.assertEqual(Types.Converters.toBool(values[i][j]),cnt[i,j])
                    else:
#                        print "CK",cnt[i,j],  values[i][j],cnt[i,j] - values[i][j]
                        self._tc.assertTrue(abs(cnt[i,j] - values[i][j] ) <= error)
                else:
                    self._tc.assertEqual(values[i][j], cnt[i,j])
            


        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])



    ## checks xml image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param grows growing dimension
    # \param attrs dictionary with string attributes    
    def checkXMLImageField(self, det, name, dtype, nxtype, values, error = 0, grows = 0 ,attrs = None):

        atts = {"type":nxtype,"units":""}
        if attrs is not None:
            atts = attrs

        cnt = det.open(name)
        self._tc.assertTrue(cnt.valid)
        self._tc.assertEqual(cnt.name,name)
        self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
        self._tc.assertEqual(len(cnt.shape), 2)
        self._tc.assertEqual(cnt.shape, (len(values),len(values[0])))
        self._tc.assertEqual(cnt.dtype, dtype)
        self._tc.assertEqual(cnt.size, len(values)*len(values[0]))        
        # pninx is not supporting reading string areas 



        
        for i in range(len(values)):
            for j in range(len(values[i])):
#                print i, j, cnt[i,j], values[i][j]
                if self._isNumeric(cnt[i,0]):
                    if nxtype == "NX_BOOLEAN":
                        self._tc.assertEqual(Types.Converters.toBool(values[i][j]),cnt[i,j])
                    else:
                        self._tc.assertTrue(abs(values[i][j] - cnt[i,j]) <= error)
                else:
                    self._tc.assertEqual(values[i][j], cnt[i,j])
            


        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])

        
    ## checks  string image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param attrs dictionary with string attributes    
    def checkStringImageField(self, det, name, dtype, nxtype, values, attrs = None):

        atts = {"type":nxtype,"units":"","nexdatas_source":None}
        if attrs is not None:
            atts = attrs
        
        cnts = [[ det.open(name +"_"+str(s1) +"_"+str(s2) ) for s2 in range(len(values[0][0]))] for s1 in range(len(values[0])) ]

        for s1 in range(len(values[0])) :
            for s2 in range(len(values[0][0])) :
                self._tc.assertEqual(cnts[s1][s2].name, name + "_" + str(s1)+ "_" + str(s2))
            

        for icnt in cnts:
            for cnt in icnt:
                self._tc.assertTrue(cnt.valid)
                self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
                self._tc.assertEqual(len(cnt.shape), 1)
                self._tc.assertEqual(cnt.shape, (len(values),))
                self._tc.assertEqual(cnt.dtype, dtype)
                self._tc.assertEqual(cnt.size, len(values))        


                self._tc.assertEqual(cnt.nattrs,len(atts))
                for a in atts:
                    at = cnt.attr(a)
                    self._tc.assertTrue(at.valid)
                    self._tc.assertTrue(hasattr(at.shape,"__iter__"))
                    self._tc.assertEqual(len(at.shape),0)
                    self._tc.assertEqual(at.dtype,"string")
                    self._tc.assertEqual(at.name, a)
                    if atts[a] is not None:
                        self._tc.assertEqual(at.value,atts[a])



        
        for i in range(len(values)):
            for j in range(len(values[i])):
                for k in range(len(values[i][j])):
#                print i, j, cnt[i,j], lvalues[i][j]
                    self._tc.assertEqual(values[i][j][k], cnts[j][k][i])
            
    ## checks single string image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param attrs dictionary with string attributes    
    def checkSingleStringImageField(self, det, name, dtype, nxtype, values, attrs= None):

        atts = {"type":nxtype,"units":"","nexdatas_source":None}
        if attrs is not None:
            atts = attrs


        cnts = [ det.open(name +"_"+str(s1) )  for s1 in range(len(values[0])) ]

        for s1 in range(len(values[0])) :
            self._tc.assertEqual(cnts[s1].name, name + "_" + str(s1))
            

        for cnt in cnts:
            self._tc.assertTrue(cnt.valid)
            self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
            self._tc.assertEqual(len(cnt.shape), 1)
            self._tc.assertEqual(cnt.shape, (len(values),))
            self._tc.assertEqual(cnt.dtype, dtype)
            self._tc.assertEqual(cnt.size, len(values))        


            self._tc.assertEqual(cnt.nattrs,len(atts))
            for a in atts:
                at = cnt.attr(a)
                self._tc.assertTrue(at.valid)
                self._tc.assertTrue(hasattr(at.shape,"__iter__"))
                self._tc.assertEqual(len(at.shape),0)
                self._tc.assertEqual(at.dtype,"string")
                self._tc.assertEqual(at.name, a)
                if atts[a] is not None:
                    self._tc.assertEqual(at.value,atts[a])
                    

        
        for i in range(len(values)):
            for j in range(len(values[i])):
#                print i, j, cnt[i,j], lvalues[i][j]
                self._tc.assertEqual(values[i][j], cnts[j][i])
            



    ## checks XML string image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param attrs dictionary with string attributes    
    def checkXMLStringImageField(self, det, name, dtype, nxtype, values, attrs = None):

        atts = {"type":nxtype,"units":""}
        if attrs is not None:
            atts = attrs


        cnts = [ det.open(name +"_"+str(s1) )  for s1 in range(len(values[0])) ]

        for s1 in range(len(values[0])) :
            self._tc.assertEqual(cnts[s1].name, name + "_" + str(s1))
            

        for cnt in cnts:
            self._tc.assertTrue(cnt.valid)
            self._tc.assertTrue(hasattr(cnt.shape, "__iter__"))
            self._tc.assertEqual(len(cnt.shape), 1)
            self._tc.assertEqual(cnt.shape, (len(values),))
            self._tc.assertEqual(cnt.dtype, dtype)
            self._tc.assertEqual(cnt.size, len(values))        


        self._tc.assertEqual(cnt.nattrs,len(atts))
        for a in atts:
            at = cnt.attr(a)
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name, a)
            if atts[a] is not None:
                self._tc.assertEqual(at.value,atts[a])

        

        
        for i in range(len(values)):
            for j in range(len(values[i])):
#                print i, j, cnt[i,j], lvalues[i][j]
                self._tc.assertEqual(values[i][j], cnts[j][i])
            


