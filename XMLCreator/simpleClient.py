#!/usr/bin/env python
"""@package docstring
@file simpleClient.py
"""
import sys,os
import time

from PyTango import *

if __name__ == "__main__":

    if  len(sys.argv) <2:
        print "usage: simpleClient.py  <XMLfile>  <H5file>  <tangoServer>"
        
    else:
        xmlf=sys.argv[1]
        if os.path.exists(xmlf):


            if len(sys.argv)>3:
                fname=sys.argv[2]
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
            if len(sys.argv)>4:
                device=sys.argv[3]
            
            dpx=DeviceProxy(device)
            print " Connected to: ", device
            xml = open(xmlf, 'r').read()
            dpx.TheXMLSettings=xml
            dpx.FileName=fname

            print "opening H5 file"
            dpx.open()

            print "recording H5 file"
            dpx.record()
            
            print "sleeping for 1s"
            time.sleep(1)
            print "recording H5 file"
            dpx.record()
            print "sleeping for 1s"
            time.sleep(1)
            print "recording H5 file"
            dpx.record()
            print "closing H5 file"
            dpx.close()
            
                
            
            

