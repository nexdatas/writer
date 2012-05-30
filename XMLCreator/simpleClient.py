#!/usr/bin/env python
"""@package docstring
@file simpleClient.py
"""
import sys,os
import time

from PyTango import *

if __name__ == "__main__":

    if  len(sys.argv) <2:
        print "usage: simpleClient.py  <XMLfile>  <tangoServer>"
        
    else:
        xmlf=sys.argv[1]
        if os.path.exists(xmlf):


            device="p09/tdw/r228"
            if len(sys.argv)>3:
                device=sys.argv[2]
            
            dpx=DeviceProxy(device)
            print " Connected to: ", device
            xml = open(xmlf, 'r').read()
            dpx.TheXMLSettings=xml
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
            
                
            
            

