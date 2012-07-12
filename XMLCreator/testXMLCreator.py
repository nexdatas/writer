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

from simpleXML import *

if __name__ == "__main__":
	df=XMLFile("MNI.xml")
	
	en = NGroup(df.root,"entry2","NXentry")

	ins = NGroup(en.elem,"instrument","NXinstrument")
#	NXsource
	src = NGroup(ins.elem,"source","NXsource")
	f = NField(src.elem,"distance","NX_FLOAT")
	f.setUnits("m")
	f.setText("100.")
	f = NField(src.elem,"db_devices","NX_CHAR")
	d=NDimensions(f.elem,"2")
	d.dim("1","151")
	d.dim("2","2")
	sr=NDSource(f.elem,"STEP")
	sr.initDBase("MYSQL","SELECT name,pid FROM device","tango","IMAGE",gHost="haso228k.desy.de")
	f = NField(src.elem,"type","NX_CHAR")
	f.setText("Synchrotron X-ray Source")
	f = NField(src.elem,"name","NX_CHAR")
	f.setText("PETRA-III")
	f.addAttr("short_name","NX_CHAR","P3")
	f = NField(src.elem,"probe","NX_CHAR")
	f.setText("x-ray")
	f = NField(src.elem,"power","NX_FLOAT")
	f.setUnits("W")
	f.setText("1")
	sr=NDSource(f.elem,"INIT")
	sr.initTango("p09/motor/exp.01","attribute","power",gHost="haso228k.desy.de",gPort="10000")
	f = NField(src.elem,"emittance_x","NX_FLOAT")
	f.setUnits("nm rad")
	f.setText("0.2")
	sr=NDSource(f.elem,"STEP")
	sr.initClient("emitannce_x");
	f = NField(src.elem,"emittance_y","NX_FLOAT")
	f.setUnits("nm rad")
	f.setText("0.2")
	sr=NDSource(f.elem,"STEP")
	sr.initSardana("door1","emitannce_y",gHost="haso228k.desy.de",gPort="10000");
	f = NField(src.elem,"sigma_x","NX_FLOAT")
	f.setUnits("nm")
	f.setText("0.1")
	f = NField(src.elem,"sigma_y","NX_FLOAT")
	f.setUnits("nm")
	f.setText("0.1")
	f = NField(src.elem,"flux","NX_FLOAT")
	f.setUnits("s-1 cm-2")
	f.setText("0.1")
	f = NField(src.elem,"energy","NX_FLOAT")
	f.setUnits("GeV")
	f.setText("0.1")
	f = NField(src.elem,"current","NX_FLOAT")
	f.setUnits("A")
	f.setText("10")
	f = NField(src.elem,"voltage","NX_FLOAT")
	f.setUnits("V")
	f.setText("10")
	f = NField(src.elem,"period","NX_FLOAT")
	f.setUnits("microseconds")
	f.setText("1")
	f = NField(src.elem,"target_material","NX_CHAR")
	f.setText("C")
# any source/facility related messages/events
# that occurred during the experiment
	g = NGroup(src.elem,"notes","NXnote")
# For storage rings, description of the bunch
# pattern. This is useful to describe irregular
# bunch patterns.
# See table: NXsource: NXsource/bunch_pattern:NXdata
	g = NGroup(src.elem,"bunch_pattern","NXdata")
	f = NField(src.elem,"number_of_bunches","NX_INT")
	f.setText("1")
	f = NField(src.elem,"bunch_length","NX_FLOAT")
	f.setUnits("s")
	f.setText("1")
	f = NField(src.elem,"bunch_distantce","NX_FLOAT")
	f.setUnits("s")
	f.setText("1")
	f = NField(src.elem,"bunch_width","NX_FLOAT")
	f.setUnits("s")
	f.setText("2")
# source pulse shape
	g = NGroup(src.elem,"pulse_shape","NXdata")
	f = NField(src.elem,"mode","NX_CHAR")
	f.setText("Single Bunch")
	f = NField(src.elem,"top_up","NX_BOOLEAN")
	f.setText("true")
	
	
	src.setText("My source")
#	mot1 = DevNGroup(ins.elem,"p09/motor/exp.01","motor1","NXpositioner", commands=False)
	mot1 = DevNGroup(ins.elem,"p09/motor/exp.01","motor1","NXpositioner", commands=False,\
				 blackAttrs=["PositionEncoder","PositionEncoderRaw"])
	mot2 = DevNGroup(ins.elem,"p09/motor/exp.02","motor2","NXpositioner", commands=False,\
				 blackAttrs=["PositionEncoder","PositionEncoderRaw"])
	mca = DevNGroup(ins.elem,"p09/mca/exp.02","mca2","NXdetector")
	cnt = DevNGroup(ins.elem,"p09/counter/exp.02","counter","NXmonitor")
	dac = DevNGroup(ins.elem,"p09/dac/exp.02","dac","NXsensor")
	adc = DevNGroup(ins.elem,"p09/adc/exp.02","adc","NXsensor")
	vfc = DevNGroup(ins.elem,"p09/vfc/exp.02","vfcadc","NXsensor")
	dgg2 = DevNGroup(ins.elem,"p09/dgg2/exp.01","dgg2","NXmonitor")
	tst = NGroup(en.elem,"tst","NXinstrument")
	mot1.setText("My motor1")
	mot2.setText("My motor1")

	KKK = DevNGroup(tst.elem,"p09/tst/exp.01","Tst","NXmonitor")
	
	df.dump()

 
