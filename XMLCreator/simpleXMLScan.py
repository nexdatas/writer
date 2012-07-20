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
## \package ndtstools tools for ndts
## \file simpleXMLScan.py
# test of XML file creator

from simpleXML import *

if __name__ == "__main__":
	df = XMLFile("scan.xml")
	
	en = NGroup(df.root, "entry1", "NXentry")

	## instrument
	ins = NGroup(en.elem, "instrument", "NXinstrument")
#	NXsource	
	dt = NGroup(ins.elem, "detector", "NXdetector")
	f = NField(dt.elem, "counter1", "NX_FLOAT")
	f.setUnits("m")
#	f.setText("0.2")
	sr = NDSource(f.elem, "STEP")
	sr.initClient("p09/counter/exp.01");


	f = NField(dt.elem, "counter2", "NX_FLOAT")
	f.setUnits("s")
#	f.setText("0.2")
	sr = NDSource(f.elem, "STEP")
	sr.initClient("p09/counter/exp.02");
	

	f = NField(dt.elem, "mca", "NX_FLOAT")
	f.setUnits("")
	d = NDimensions(f.elem, "1")
	d.dim("1", "2048")
	sr = NDSource(f.elem, "STEP")
	sr.initTango("p09/mca/exp.02", "attribute", "Data")
#	sr.initClient("p09/mca/exp.02");

        ##	NXdata
	da = NGroup(en.elem, "data", "NXdata")
	## link
	l = NLink(da.elem, "data", "/NXentry/NXinstrument/NXdetector/mca")
	l.addDoc("Link to mca in /NXentry/NXinstrument/NXdetector")
	l = NLink(da.elem, "counter1", "/NXentry/NXinstrument/NXdetector/counter1")
	l.addDoc("Link to counter1 in /NXentry/NXinstrument/NXdetector")
	l = NLink(da.elem, "counter2", "/NXentry/NXinstrument/NXdetector/counter2")
	l.addDoc("Link to counter2 in /NXentry/NXinstrument/NXdetector")



	df.dump()

 
