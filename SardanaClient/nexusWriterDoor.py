#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package ndts SardanaClient
## \file nexusWriterDoor.py
# nexus Door
#



import PyTango
import time, sys, os
import taurus.core.tango.sardana.macroserver
import pprint
import json

PYQT = True
try:
    from PyQt4.QtCore import QObject, SIGNAL, QString
except:
    PYQT = False

## pretty print
pp = pprint.PrettyPrinter()
## tango database
db = PyTango.Database()

taurus.core.tango.sardana.macroserver.registerExtensions()
    




## Nexus Writer Door     
class nexusDoor(taurus.core.tango.sardana.macroserver.BaseDoor):


    ## constructor
    # \param name door name
    # \param kw dictionary with other arguments
    def __init__(self, name, **kw):
        print "nexusDoor.__init__()", name
        self.call__init__(taurus.core.tango.sardana.macroserver.BaseDoor, name, **kw)

        ## Nexus scan directory
        self.scandir = ""
        ## Nexus file name
        self.filename = ""
        ## serial number
        self.serialno = 0

        ## start position
        self.start = 0 
        ## stop position
        self.stop = 100
        ## number of points
        self.np = 100


        ## device aliases
        self.deviceAliases = {}
        ## cut device aliases
        self.cutDeviceAliases = {}
        ## dictionary with names to replace
        self.toReplace = {}
        ## configuration server
        self.cnfServer = None
        ## Nexus writer
        self.nexusWriter=None
        
        ## writing status
        self.writing = False

        ## signal emitter
        if PYQT:
            self.emitter = QObject()
        else:
            self.emitter = None
    


        env = self.getEnvironment()
        if not env.has_key('NexusWriterDevice'):
            ## Nexus writer device name
            self.device = 'haso228k.desy.de:10000/p09/tdw/r228'
            self.setEnvironment('NexusWriterDevice', self.device)
        else:
            ## Nexus writer device name
            self.device = self.getEnvironment('NexusWriterDevice') 

        if not env.has_key('ScanFinished'):
            self.setEnvironment('ScanFinished', 'True')

        env = self.getEnvironment()
           
        if not env.has_key('ConfigurationServerDevice'):
            ## configuration server device name
            self.cnfdevice = 'haso228k.desy.de:10000/p09/mcs/r228'
            self.setEnvironment('ConfigurationServerDevice', self.cnfdevice) 
        else:
            ## configuration server device name
            self.cnfdevice = self.getEnvironment('ConfigurationServerDevice')
            



    ## provides a device alias
    # \param name device name       
    # \return device alias 
    def get_alias(self, name):
        # if name does not contain a "/" it's probably an alias
        if name.find("/") == -1:
            return name

        # haso107klx:10000/expchan/hasysis3820ctrl/1
        if name.find(':') >= 0:
            lst = name.split("/")
            name = "/".join(lst[1:])
        return db.get_alias(name)


    ## creates a file name from dataRecord variables
    # \param dataRecord Sardana data record
    def prepareFileName(self, dataRecord):

        if type(dataRecord[1]['data'][ 'scanfile']).__name__ == 'list':
            scanfile = dataRecord[1]['data'][ 'scanfile'][0]
        else:
            scanfile = dataRecord[1]['data'][ 'scanfile']
        self.scandir = dataRecord[1]['data'][ 'scandir']
        self.serialno = dataRecord[1]['data'][ 'serialno']
        self.filename = "%s_%05d.%s" % (scanfile.rpartition('.')[0], self.serialno, "h5")
#        startTime = dataRecord[1]['data']['starttime']
#        title = dataRecord[1]['data']['title']
                
    ## finds scan limits
    # \param dataRecord Sardana data record
    def findScanLimits(self, dataRecord):

        # get the scan limits from the title
        cmd = dataRecord[1]['data']['title'].split()
        self.start, self.stop, self.np = 0, 100, 100

        # ascan exp_dmy01 0 1 10 0.2
        if cmd[0] == 'ascan':
            self.start = float(cmd[2])
            self.stop = float(cmd[3])
            self.np = int(cmd[4])

        # a2scan exp_dmy01 0 1 exp_dmy02 2 3 10 0.2
        elif  cmd[0] == 'a2scan':
            self.start = float(cmd[2])
            self.stop = float(cmd[3])
            self.np = int(cmd[7])

        # a3scan exp_dmy01 0 1 exp_dmy02 2 3 exp_dmy03 3 4 10 0.2
        elif  cmd[0] == 'a3scan':
            self.start = float(cmd[2])
            self.stop = float(cmd[3])
            self.np = int(cmd[10])
        else:
            raise Exception("nexusDoor.findScanLimits",
                             "cmd not recognized %s" % (dataRecord[1]['data']['title']))
        return


    ## creates Nexus configuration
    # \param dataRecord Sardana data record
    # \returns Nexus configuration string 
    def createNexusConfiguration(self, dataRecord):
        self.deviceAliases = {}
        self.toReplace = {}
        for elm in dataRecord[1]['data'][ 'counters']:
            alias = self.get_alias(str(elm))
            self.deviceAliases[alias] = elm
        for elm in dataRecord[1]['data']['column_desc']:
            desc = dataRecord[1]['data']['column_desc']
            if "name" in elm.keys():
                alias = self.get_alias(str(elm["name"]))
                self.deviceAliases[alias] = elm["name"] 

        
        self.cutDeviceAliases = {}
        for alias in self.deviceAliases.keys():
            if alias.startswith("sca_exp_mca"):
                self.cutDeviceAliases[alias] = "_".join(alias.split("_")[:3])
                self.toReplace[alias] = "_".join(alias.split("_")[:3])
            else:
                self.cutDeviceAliases[alias] = alias



        dsFound = {}
        cpReq = {}
        self.cnfServer = PyTango.DeviceProxy(self.cnfdevice)

        if PYQT:
            self.emitter.emit(SIGNAL("updateCServer(QString)"), QString(self.cnfdevice))

        if self.cnfServer.State() == PyTango.DevState.ON:
            self.cnfServer.Open()
            
        cmps = self.cnfServer.AvailableComponents()
        for cp in cmps:
            dss = self.cnfServer.ComponentDataSources(cp)
            for ds in dss:
                if ds in self.cutDeviceAliases.values():

                    print ds, "found in ", cp
                    if ds not in dsFound.keys():
                        dsFound[ds]=[]
                    dsFound[ds].append(cp)    
                    if cp not in cpReq.keys():
                        cpReq[cp]=[]
                    cpReq[cp].append(ds)    

        for ds in self.cutDeviceAliases.values():
            if ds not in dsFound.keys():
                print "Warning:", ds, "not found!"
         
        self.cnfServer.CreateConfiguration(cpReq.keys())
        cnfxml = self.cnfServer.XMLString
        self.cnfServer.Close()
        return cnfxml

    ## inits Nexus Writer
    # \param xml Nexus configuration string 
    def initNexusWriter(self, xml):

        self.nexusWriter=PyTango.DeviceProxy(self.device)

        if PYQT:
            self.emitter.emit(SIGNAL("updateNWriter(QString)"), QString(self.device))

        self.nexusWriter.Init()
        print " Connected to: ", self.device
        
        fname= "%s/%s" % (self.scandir, self.filename)
        print "FILE:", fname
        self.nexusWriter.FileName=fname.encode()

        if PYQT:
            self.emitter.emit(SIGNAL("updateFile(QString)"), QString(fname))
        
        print "opening the H5 file"
        self.nexusWriter.OpenFile()
        
        self.nexusWriter.TheXMLSettings=xml

        self.nexusWriter.TheJSONRecord='{}'
        print "opening the entry"
        self.nexusWriter.OpenEntry()



    ## prepares a new scan and performs the INIT mode writing
    # \param dataRecord Sardana data record
    def prepareNewScan(self, dataRecord):

        self.indexScan = 0
        self.prepareFileName(dataRecord)
        self.findScanLimits( dataRecord)
        if PYQT:
            self.emitter.emit(SIGNAL("updateNP(int,int)"), self.indexScan, self.np)

        try:
            xml = self.createNexusConfiguration(dataRecord)
            self.initNexusWriter(xml)
        except:
            self.writing = False
            raise Exception,"Configuration cannot be performed. Abort writing"
        

    ## performs the FINAL mode writing and closes the Nexus file
    # \param dataRecord Sardana data record
    def closeScan(self, dataRecord):
        # close the H5 file
        # optional JSON attribute
        self.nexusWriter.TheJSONRecord='{}'
        print "closing the entry"
        self.nexusWriter.CloseEntry()
        print "closing the H5 file"
        self.nexusWriter.CloseFile()


    ## replaces alias but cut aliases according to self.toReplaces
    # \param text with aliases
    # \returns text with cut aliases    
    def replaceAliases(self, text):
        res = text
        if self.toReplace:
            for el in self.toReplace.keys():
                res = res.replace(el, self.toReplace[el])
        return res


    ## records Data
    # \param s door s parameter
    # \param t door t parameter
    # \param v door v parameter
    # \returns dataRecord on STEP mode
    def recordDataReceived(self, s, t, v):
        try:
            dataRecord = taurus.core.tango.sardana.macroserver.BaseDoor.recordDataReceived(self, s, t, v)
        except:
            self.writing = False
            raise Exception,"Problems in fetching dataRecord"

        if dataRecord == None:
            return
        print ">>> recordDataReceived "
        pp.pprint(dataRecord)

        # new scan 
        
        if "type" in dataRecord[1] and dataRecord[1]['type'] == "data_desc":
            finished = False if self.getEnvironment('ScanFinished').upper() == "FALSE" else True

            if finished:
                self.setEnvironment('ScanFinished', 'False')
                self.writing = True
                print "Writing NeXus: INIT"
                self.prepareNewScan(dataRecord)
            return dataRecord


        # end of the scan
        if "type" in dataRecord[1] and dataRecord[1]['type'] == "record_end":
            if self.writing:
                print "Writing NeXus: FINAL"
                self.closeScan(dataRecord)
                env = self.getEnvironment()
                self.setEnvironment('ScanFinished', 'True')

            return dataRecord

        # record step
        if "type" in dataRecord[1] and dataRecord[1]['type'] == "record_data":
            if self.writing:
                jsonString = self.replaceAliases(json.dumps(dataRecord[1]))
                print "Writing NeXus: STEP"
                self.nexusWriter.record(jsonString)
                

                self.indexScan += 1
                if PYQT:
                    self.emitter.emit(SIGNAL("updateNP(int,int)"), self.indexScan, self.np)

            return dataRecord

        return dataRecord


