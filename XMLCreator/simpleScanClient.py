#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
# \package  ndtstools tools for ndts
# \file simpleClient.py

import sys,os
import time

import random

from math import exp

from PyTango import *

if __name__ == "__main__":

    if  len(sys.argv) <2:
        print "usage: simpleClient.py  <XMLfile>  <H5file>  <tangoServer>"
        
    else:
        xmlf=sys.argv[1]
        if os.path.exists(xmlf):


            if len(sys.argv)>2:
                
                fname=sys.argv[2]
                print fname
            else:
                sp=xmlf.split(".")
                print sp
                if sp[-1] == 'xml' :
                    fname=''.join(sp[0:-1])
                else:
                    fname=xmlf
                fname = fname.strip() + ".h5"
            print "storing in ", fname 
    
            device="p09/tdw/r228"
            if len(sys.argv)>3:
                device=sys.argv[3]
            
            dpx=DeviceProxy(device)
            print " Connected to: ", device
    
            xml = open(xmlf, 'r').read()


            dpx.FileName=fname

            print "opening the H5 file"
            dpx.OpenFile()

            dpx.TheXMLSettings=xml

            print "opening the entry"
            dpx.OpenEntry()

            print "recording the H5 file"
            pr=[[1./random.randrange(100,1000),random.randrange(0.,2048.0),random.randrange(0.,2000)/2000.] for i in range(5)]
            mca=str([sum([pr[j][2]*exp(-pr[j][0]*(i-pr[j][1])**2) for j in range(len(pr)) ]) \
                         for i in range(2048)])
            dpx.record('{"data": {"p09/counter/exp.01":0.1,"p09/counter/exp.02":1.1,"p09/mca/exp.02":'\
                           + mca+ '  },   "type": "record_data"}')
            
            print "sleeping for 1s"
            time.sleep(1)
            print "recording the H5 file"
            pr=[[1./random.randrange(100,1000),random.randrange(0.,2048.0),random.randrange(0.,2000)/2000.] for i in range(5)]
            mca=str([sum([pr[j][2]*exp(-pr[j][0]*(i-pr[j][1])**2) for j in range(len(pr)) ]) \
                         for i in range(2048)])
            dpx.record('{"data": {"p09/counter/exp.01":0.2,"p09/counter/exp.02":1.3,"p09/mca/exp.02":'\
                           + mca+ '  },   "type": "record_data"}')

            print "sleeping for 1s"
            time.sleep(1)
            print "recording the H5 file"
            pr=[[1./random.randrange(100,1000),random.randrange(0.,2048.0),random.randrange(0.,2000)/2000.] for i in range(5)]
            mca=str([sum([pr[j][2]*exp(-pr[j][0]*(i-pr[j][1])**2) for j in range(len(pr)) ]) \
                         for i in range(2048)])
            
            dpx.record('{"data": {"p09/counter/exp.01":0.3,"p09/counter/exp.02":1.4,"p09/mca/exp.02":'\
                           + mca+ '  },   "type": "record_data"}')

            print "closing the  entry"
            dpx.closeEntry()
            print "closing the H5 file"
            dpx.closeFile()
            
                
            
            

