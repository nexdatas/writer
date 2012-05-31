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

from PyTango import *
import sys, os, time
import xml.etree.ElementTree as ET
import xml.dom.minidom

tTypes=["DevVoid",
        "DevBoolean",
        "DevShort",
        "DevLong",
        "DevFloat",
        "DevDouble",
        "DevUShort",
        "DevULong",
        "DevString",
        "DevVarCharArray",
        "DevVarShortArray",
        "DevVarLongArray",
        "DevVarFloatArray",
        "DevVarDoubleArray",
        "DevVarUShortArray",
        "DevVarULongArray",
        "DevVarStringArray",
        "DevVarLongStringArray",
        "DevVarDoubleStringArray",
        "DevState",
        "ConstDevString",
        "DevVarBooleanArray",
        "DevUChar",
        "DevLong64",
        "DevULong64",
        "DevVarLong64Array",
        "DevVarULong64Array",
        "DevInt",
        "DevEncoded"]

nTypes=["NX_CHAR",
        "NX_BOOLEAN",
        "NX_INT32",
        "NX_INT32",
        "NX_FLOAT32",
        "NX_FLOAT64",
        "NX_UINT32",
        "NX_UINT32",
	"NX_CHAR",
        "NX_CHAR"
        "NX_INT32",
        "NX_INT64",
        "NX_FLOAT32",
        "NX_FLOAT64",
        "NX_UINT32",
        "NX_UINT64",
	"NX_CHAR",
        "NX_CHAR",
        "NX_CHAR",
        "NX_CHAR",
        "NX_CHAR",
        "NX_BOOLEAN",
        "NX_CHAR",
        "NX_INT64",
        "NX_UINT64",
        "NX_INT64",
        "NX_UINT64",
        "NX_INT",
        "NX_CHAR"]




class NTag:
	def __init__(self,parent,gTag,gName="",gType=""):
		self.parent=parent
		self.gName=gName
		self.gType=gType
		self.elem=ET.SubElement(parent,gTag)
		if gName != "" :
			self.elem.attrib["name"]=gName
		if gType != "" :
			self.elem.attrib["type"]=gType

	def addTagAttr(self,name, value):
		self.elem.attrib[name]=value

	def setText(self,gText):
		self.elem.text=gText

	def addText(self,gText):
		self.elem.text= self.elem.text + gText


	
class NAttr(NTag):
	def __init__(self,parent,gName,gType=""):
		NTag.__init__(self,parent,"attribute",gName,gType)
	def setDataSource(self):
			pass


class NGroup(NTag):
	def __init__(self,parent,gName,gType=""):
		NTag.__init__(self,parent,"group",gName,gType)
		self.doc=[]
		self.gAttr={}

	def addDoc(self,gDoc):
		self.doc.append(ET.SubElement(self.elem,"doc"))
		self.doc[-1].text=gDoc


	def addAttr(self,aName,aType,aContent=""):
		print aName, aType, aContent
		at=NAttr(self.elem,aName,aType)
		self.gAttr[aName]=at
		if aContent != "":
			at.setText(aContent)
			pass


class NLink(NTag):
	def __init__(self,parent,gName,gTarget):
		NTag.__init__(self,parent,"link",gName)
		self.addTagAttr("target",gTarget)
		self.doc=[]

	def addDoc(self,gDoc):
		self.doc.append(ET.SubElement(self.elem,"doc"))
		self.doc[-1].text=gDoc


class NDimensions(NTag):
	def __init__(self,parent,gRank):
		NTag.__init__(self,parent,"dimensions")
		self.addTagAttr("rank",gRank)
		self.dims={}
		
	def dim(self,gIndex,gValue):
		self.dims[gIndex]=NDim(self.elem,gIndex,gValue)
			
		
class NDim(NTag):
	def __init__(self,parent,gIndex,gValue):
		NTag.__init__(self,parent,"dim")
		self.addTagAttr("index",gIndex)
		self.addTagAttr("value",gValue)
		
		

class NField(NTag):
	def __init__(self,parent,gName,gType=""):
		NTag.__init__(self,parent,"field",gName,gType)
		self.doc=[]
		self.attr={}
		
	def setUnits(self,gUnits):
		self.addTagAttr("units",gUnits)

	def setDataSource(self):
		pass

	def addDoc(self,gDoc):
		self.doc.append(ET.SubElement(self.elem,"doc"))
		self.doc[-1].text=gDoc

	def addAttr(self,aName,aType,aContent=""):
		self.attr[aName]=NAttr(self.elem,aName,aType)
 		if aContent != '':
			self.attr[aName].setText(aContent)



class NDSource(NTag):
	def __init__(self,parent,gStrategy,gHost,gPort):
		NTag.__init__(self,parent,"datasource")
		self.elem.attrib["strategy"]=gStrategy
		self.elem.attrib["hostname"]=gHost
		self.elem.attrib["port"]=gPort
		
	def initDBase(self,gDBname,gQuery):
		self.elem.attrib["type"]="DB"
		self.elem.attrib["dbname"]=gDBname
		self.elem.attrib["query"]=gQuery

	def initTango(self,gDevice,gDType,gDName):
		self.elem.attrib["type"]="TANGO"
		self.elem.attrib["device"]=gDevice
		da=NTag(self.elem,"record")
		da.addTagAttr("type", gDType)
		da.addTagAttr("name", gDName)

	def initClient(self,gDName):
		da=NTag(self.elem,"record")
		da.addTagAttr("name", gDName)
		

	def initSardana(self,gDoor,gDName):
		self.elem.attrib["type"]="SARDANA"
		self.elem.attrib["door"]=gDoor
		da=NTag(self.elem,"record")
		da.addTagAttr("name", gDName)




class DevNGroup(NGroup):
	def __init__(self,parent,devName,gName,gType=""):
		NGroup.__init__(self,parent,gName,gType)
		self.proxy=DeviceProxy(devName)
		self.prop=self.proxy.get_property_list('*')
		self.fields={}
		print "PROP",self.prop
		for pr in self.prop:
			self.addAttr(pr,"NX_CHAR",str(self.proxy.get_property(pr)[pr][0]))
			
		self.attr=self.proxy.get_attribute_list()
		self.fields={}
		for at in self.attr:
			print at
			cf=self.proxy.attribute_query(at)
			print "QUERY"
			print cf
			print cf.name
			print cf.data_format
			print cf.standard_unit
			print cf.display_unit
			print cf.unit
			print tTypes[cf.data_type]
			print nTypes[cf.data_type]
			print cf.data_type

			self.fields[at]=NField(self.elem,at,nTypes[cf.data_type])
			if cf.unit != 'No unit':
				self.fields[at].setUnits(cf.unit)
			self.fields[at].setUnits(cf.unit)
			      
			if cf.description != 'No description':
				self.fields[at].addDoc(cf.description)
			self.addAttr('URL',"NX_CHAR","tango://"+devName)
			
			sr=NDSource(self.fields[at].elem,"STEP","haso228k.desy.de","10000")
			sr.initTango(devName,"attribute",at)
				
#		print self.proxy.attribute_list_query()
			
			

class XMLDevice:
	def __init__(self,fname):
		self.fname=fname
		self.root=ET.Element("definition")
		
	def prettyPrintET(self,etNode):
		mxml = xml.dom.minidom.parseString(ET.tostring(etNode))
		return mxml.toprettyxml()


	def dump(self):
		
		myfile = open(self.fname, "w")
		myfile.write(self.prettyPrintET(self.root))
		myfile.close()
		pass

	
 
		


if __name__ == "__main__":
	df=XMLDevice("test.xml")
	en = NGroup(df.root,"entry","NXentry")
	ins = NGroup(en.elem,"instrument","NXinstrument")
#	NXsource
	src = NGroup(ins.elem,"source","NXsource")
	f = NField(src.elem,"distance","NX_FLOAT")
	f.setUnits("m")
	f.setText("100.")
	sr=NDSource(f.elem,"STEP","door.desy.de","12345")
	sr.initDBase("door_db",'SELECT proposal_name FROM proposals WHERE date = TODAY AND beamline = "P03"')
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
	sr=NDSource(f.elem,"INIT","haso228k.desy.de","10000")
	sr.initTango("p09/motor/exp.01","attribute","power")
	f = NField(src.elem,"emittance_x","NX_FLOAT")
	f.setUnits("nm rad")
	f.setText("0.2")
	sr=NDSource(f.elem,"STEP","haso228k.desy.de","10000")
	sr.initClient("emitannce_x");
	f = NField(src.elem,"emittance_y","NX_FLOAT")
	f.setUnits("nm rad")
	f.setText("0.2")
	sr=NDSource(f.elem,"STEP","haso228k.desy.de","10000")
	sr.initSardana("door1","emitannce_y");
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

#       NXcrystal	
	cr = NGroup(ins.elem,"crystal","NXcrystal")
	f = NField(cr.elem,"distance","NX_FLOAT")
	f.setUnits("A")
	f.addDoc("Optimum diffracted wavelength")
	d=NDimensions(f.elem,"1")
	d.dim("1","10")

#       NXdetector	
	de = NGroup(ins.elem,"detector","NXdetector")
	f = NField(de.elem,"azimuthal_angle","NX_FLOAT")
	f = NField(de.elem,"beam_center_x","NX_FLOAT")
	f = NField(de.elem,"beam_center_y","NX_FLOAT")
	f = NField(de.elem,"data","NX_FLOAT")
	d=NDimensions(f.elem,"2")
	d.dim("1","100")
	d.dim("2","100")
	f = NField(de.elem,"distance","NX_FLOAT")
	f = NField(de.elem,"polar_angle","NX_FLOAT")
	f.addDoc(""" Optional rotation angle for the case when the powder diagram has been obtained
	  through an omega-2theta scan like from a traditional single detector powder
	  diffractometer""")
	d=NDimensions(f.elem,"1")
	d.dim("1","100")
	f = NField(de.elem,"rotation_angle","NX_FLOAT")
	f = NField(de.elem,"x_pixel_size","NX_FLOAT")
	f = NField(de.elem,"y_pixel_size","NX_FLOAT")


#	NXdata
	da = NGroup(en.elem,"data","NXdata")
	l= NLink(da.elem,"polar_angle", "/NXentry/NXinstrument/NXdetector/polar_angle")
	l.addDoc("Link to polar angle in /NXentry/NXinstrument/NXdetector")
	l= NLink(da.elem,"data","/NXentry/NXinstrument/NXdetector/data")
	l.addDoc("Link to data in /NXentry/NXinstrument/NXdetector")


	df.dump()

 
