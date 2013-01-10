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
## \file ServerSetUp.py
# class with server settings
#
import unittest
import os
import sys
import subprocess

import PyTango
import time
from pni.nx.h5 import open_file
from  xml.sax import SAXParseException


## test fixture
class ServerSetUp(object):

    ## constructor
    # \brief defines server parameters
    def __init__(self):
        ## information about tango writer
        self.new_device_info_writer = PyTango.DbDevInfo()
        self.new_device_info_writer._class = "TangoDataServer"
        self.new_device_info_writer.server = "TangoDataServer/TDWTEST"
        self.new_device_info_writer.name = "testp09/testtdw/testr228"

        self._psub = None



    ## test starter
    # \brief Common set up of Tango Server
    def setUp(self):
        print "\nsetting up..."
        db = PyTango.Database()
        db.add_device(self.new_device_info_writer)
        db.add_server(self.new_device_info_writer.server, self.new_device_info_writer)
        
        if os.path.isfile("../TDS"):
            self._psub = subprocess.Popen(
                "cd ..; ./TDS TDWTEST &",stdout =  subprocess.PIPE, 
                stderr =  subprocess.PIPE,  shell= True)
        else:
            self._psub = subprocess.Popen(
                "TDS TDWTEST &",stdout =  subprocess.PIPE, 
                stderr =  subprocess.PIPE , shell= True)
        print "waiting for server",
        
        found = False
        cnt = 0
        while not found and cnt < 1000:
            try:
                print "\b.",
                dp = PyTango.DeviceProxy(self.new_device_info_writer.name)
                time.sleep(0.01)
                if dp.state() == PyTango.DevState.ON:
                    found = True
            except:    
                found = False
            cnt +=1
        print ""

    ## test closer
    # \brief Common tear down oif Tango Server
    def tearDown(self): 
        print "tearing down ..."
        db = PyTango.Database()
        db.delete_server(self.new_device_info_writer.server)
        
        output = ""
        pipe = subprocess.Popen(
            "ps -ef | grep 'TangoDataServer.py TDWTEST'", stdout=subprocess.PIPE , shell= True).stdout

        res = pipe.read().split("\n")
        for r in res:
            sr = r.split()
            if len(sr)>2:
                 subprocess.call("kill -9 %s" % sr[1],stderr=subprocess.PIPE , shell= True)

        

