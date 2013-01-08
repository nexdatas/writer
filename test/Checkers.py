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
import random
from pni.nx.h5 import open_file
import unittest
from ndts import Types


from math import exp


## checks for scalar attributes
class Checker(object):

    ## constructor
    # \param testCase TestCase instance
    def __init__(self, testCase):
        ## test case
        self._tc = testCase 


    ## checks scalar tree
    # \param f pninx file object    
    # \param fname file name
    # \param children number of detector children   
    # \returns detector group object    
    def checkScalarTree(self, f, fname, children):
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

    ## creates spectrum plot with random Gaussians
    # \param xlen data length 
    # \param nrGauss of Gaussians  
    # \returns list with the plot
    def nicePlot(self, xlen=2048, nrGauss=5):
        pr = [ [ random.uniform(0.01,0.001), random.uniform(0,xlen), random.uniform(0.0,1.) ] \
                   for i in range(nrGauss) ]
        return [ sum([pr[j][2]*exp(-pr[j][0]*(i-pr[j][1])**2) for j in range(len(pr)) ]) \
                     for i in range(xlen)]


    ## creates spectrum plot with random Gaussians
    # \param xlen data x-length 
    # \param ylen data y-length 
    # \param nrGauss of Gaussians  
    # \returns list with the plot
    def nicePlot2D(self, xlen=1024, ylen=1024, nrGauss=5):
        pr = [ [ random.uniform(0.1,0.01), random.uniform(0.01,0.1), random.uniform(0,ylen), random.uniform(0,xlen), random.uniform(0.0,1.) ] \
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
    def checkScalarCounter(self, det, name, dtype, nxtype, values, error = 0):

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
        


    ## checks  spectrum field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param grows growing dimension
    def checkSpectrumField(self, det, name, dtype, nxtype, values, error = 0, grows = 0):

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



        
        for i in range(len(lvalues)):
            for j in range(len(lvalues[i])):
#                print i, j, cnt[i,j], lvalues[i][j]
                if self._isNumeric(cnt[i,0]):
                    if nxtype == "NX_BOOLEAN":
                        self._tc.assertEqual(Types.Converters.toBool(values[i][j]),cnt[i,j])
                    else:
                        self._tc.assertTrue(abs(lvalues[i][j] - cnt[i,j]) <= error)
                else:
                    self._tc.assertEqual(lvalues[i][j], cnt[i,j])
            


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
        self._tc.assertEqual(at.value,"")
        
        at = cnt.attr("nexdatas_source")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")


    ## checks  spectrum field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    def checkStringSpectrumField(self, det, name, dtype, nxtype, values):


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

            
            self._tc.assertEqual(cnt.nattrs,3)


            at = cnt.attr("units")
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name,"units")
            self._tc.assertEqual(at.value,"")

            at = cnt.attr("type")
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")
            self._tc.assertEqual(at.name,"type")
            self._tc.assertEqual(at.value,nxtype)
        

        
            at = cnt.attr("nexdatas_source")
            self._tc.assertTrue(at.valid)
            self._tc.assertTrue(hasattr(at.shape,"__iter__"))
            self._tc.assertEqual(len(at.shape),0)
            self._tc.assertEqual(at.dtype,"string")

        
        for i in range(len(values)):
            for j in range(len(values[i])):
#                print i, j, cnt[i,j], lvalues[i][j]
                self._tc.assertEqual(values[i][j], cnts[j][i])
            


        


    ## checks  image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    # \param error data precision
    # \param grows growing dimension
    def checkImageField(self, det, name, dtype, nxtype, values, error = 0, grows = 0):

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



        
        for i in range(len(lvalues)):
            for j in range(len(lvalues[i])):
                for k in range(len(lvalues[i][j])):
#                print i, j, cnt[i,j], lvalues[i][j]
                    if self._isNumeric(cnt[i,0,0]):
                        if nxtype == "NX_BOOLEAN":
                            self._tc.assertEqual(Types.Converters.toBool(values[i][j][k]),cnt[i,j,k])
                        else:
                            self._tc.assertTrue(abs(lvalues[i][j][k] - cnt[i,j,k]) <= error)
                    else:
                        self._tc.assertEqual(lvalues[i][j][k], cnt[i,j,k])
            


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
        self._tc.assertEqual(at.value,"")
        
        at = cnt.attr("nexdatas_source")
        self._tc.assertTrue(at.valid)
        self._tc.assertTrue(hasattr(at.shape,"__iter__"))
        self._tc.assertEqual(len(at.shape),0)
        self._tc.assertEqual(at.dtype,"string")



    ## checks  string image field
    # \param det detector group
    # \param name counter name
    # \param dtype numpy type
    # \param nxtype nexus type
    # \param values  original values
    def checkStringImageField(self, det, name, dtype, nxtype, values):


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


                self._tc.assertEqual(cnt.nattrs,3)


                at = cnt.attr("units")
                self._tc.assertTrue(at.valid)
                self._tc.assertTrue(hasattr(at.shape,"__iter__"))
                self._tc.assertEqual(len(at.shape),0)
                self._tc.assertEqual(at.dtype,"string")
                self._tc.assertEqual(at.name,"units")
                self._tc.assertEqual(at.value,"")
                
                at = cnt.attr("type")
                self._tc.assertTrue(at.valid)
                self._tc.assertTrue(hasattr(at.shape,"__iter__"))
                self._tc.assertEqual(len(at.shape),0)
                self._tc.assertEqual(at.dtype,"string")
                self._tc.assertEqual(at.name,"type")
                self._tc.assertEqual(at.value,nxtype)
                

        
                at = cnt.attr("nexdatas_source")
                self._tc.assertTrue(at.valid)
                self._tc.assertTrue(hasattr(at.shape,"__iter__"))
                self._tc.assertEqual(len(at.shape),0)
                self._tc.assertEqual(at.dtype,"string")
        

        
        for i in range(len(values)):
            for j in range(len(values[i])):
                for k in range(len(values[i][j])):
#                print i, j, cnt[i,j], lvalues[i][j]
                    self._tc.assertEqual(values[i][j][k], cnts[j][k][i])
            


