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
## \package ndtstools tools for ndts
## \file simpleXML.py
# creator of XML files

from PyTango import *
import sys, os, time
import xml.etree.ElementTree as ET
import xml.dom.minidom

## Tango types
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

## Nexus types
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



## tag wrapper
class NTag:
	## constructor
	# \param gTag tag name
	# \param parent parent ET tag element
	# \param gName name attribute
	# \param gType type attribute
	def __init__(self,parent,gTag,gName="",gType=""):
		## parent tag
		self.parent=parent
		## name attribute
		self.gName=gName
		## type attribute
		self.gType=gType
		## tag element from ET
		self.elem=ET.SubElement(parent,gTag)
		if gName != "" :
			self.elem.attrib["name"]=gName
		if gType != "" :
			self.elem.attrib["type"]=gType

        ## adds tag attribute
	# \param name attribute name		
	# \param value attribute value		
	def addTagAttr(self,name, value):
		self.elem.attrib[name]=value

        ## sets tag content
	# \param gText tag content
	def setText(self,gText):
		self.elem.text=gText

        ## adds tag content
	# \param gText tag content
	def addText(self,gText):
		self.elem.text= self.elem.text + gText


## Attribute tag wrapper	
class NAttr(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param gName name attribute
	# \param gType type attribute
	def __init__(self,parent,gName,gType=""):
		NTag.__init__(self,parent,"attribute",gName,gType)
	## sets DataSource: not implemented	
	def setDataSource(self):
			pass

## Group tag wrapper
class NGroup(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param gName name attribute
	# \param gType type attribute
	def __init__(self,parent,gName,gType=""):
		NTag.__init__(self,parent,"group",gName,gType)
		## list of doc tag contents
		self.doc=[]
		## container with attribute tag wrappers
		self.gAttr={}

        ## adds doc tag content
	# \param gDoc doc tag content	
	def addDoc(self,gDoc):
		self.doc.append(ET.SubElement(self.elem,"doc"))
		self.doc[-1].text=gDoc


        ## adds attribute tag
	# \param aName name attribute
	# \param aType type attribute
	# \param aContent content of the attribute tag
	def addAttr(self,aName,aType,aContent=""):
		print aName, aType, aContent
		at=NAttr(self.elem,aName,aType)
		self.gAttr[aName]=at
		if aContent != "":
			at.setText(aContent)
			pass


## Link tag wrapper
class NLink(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param gName name attribute
	# \param gTarget target attribute
	def __init__(self,parent,gName,gTarget):
		NTag.__init__(self,parent,"link",gName)
		self.addTagAttr("target",gTarget)
		## list of doc tag contents
		self.doc=[]

        ## adds doc tag content
	# \param gDoc doc tag content	
	def addDoc(self,gDoc):
		self.doc.append(ET.SubElement(self.elem,"doc"))
		self.doc[-1].text=gDoc


## Dimensions tag wrapper
class NDimensions(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param gRank  rank attribute
	def __init__(self,parent,gRank):
		NTag.__init__(self,parent,"dimensions")
		self.addTagAttr("rank",gRank)
		## container with dim tag wrapper
		self.dims={}
	## adds dim tag 
	# \param gIndex index attribute	
	# \param gValue value attribute
	def dim(self,gIndex,gValue):
		self.dims[gIndex]=NDim(self.elem,gIndex,gValue)
			
		
## Dim tag wrapper
class NDim(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param gIndex index attribute	
	# \param gValue value attribute
	def __init__(self,parent,gIndex,gValue):
		NTag.__init__(self,parent,"dim")
		self.addTagAttr("index",gIndex)
		self.addTagAttr("value",gValue)
		
		

## Field tag wrapper
class NField(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param gName name attribute
	# \param gType type attribute
	def __init__(self,parent,gName,gType=""):
		NTag.__init__(self,parent,"field",gName,gType)
		## list of doc tag contents
		self.doc=[]
		## container with attribute tag wrappers
		self.attr={}
		
	## sets the field unit
	# \param gUnits the field unit	
	def setUnits(self,gUnits):
		self.addTagAttr("units",gUnits)

	## sets DataSource: not implemented	
	def setDataSource(self):
		pass

        ## adds doc tag content
	# \param gDoc doc tag content	
	def addDoc(self,gDoc):
		self.doc.append(ET.SubElement(self.elem,"doc"))
		self.doc[-1].text=gDoc

        ## adds attribute tag
	# \param aName name attribute
	# \param aType type attribute
	# \param aContent content of the attribute tag
	def addAttr(self,aName,aType,aContent=""):
		self.attr[aName]=NAttr(self.elem,aName,aType)
 		if aContent != '':
			self.attr[aName].setText(aContent)



## Source tag wrapper
class NDSource(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param gStrategy strategy of data writing, i.e. INIT, STEP, FINAL
	# \param gHost host name
	# \param gPort port
	def __init__(self,parent,gStrategy,gHost,gPort=None):
		NTag.__init__(self,parent,"datasource")
		self.elem.attrib["strategy"]=gStrategy
		self.elem.attrib["hostname"]=gHost
		if gPort:
			self.elem.attrib["port"]=gPort

	## sets parameters of DataBase		
	# \param gDBname name of used DataBase
	# \param gQuery database query
	# \param gFormat format of the query output, i.e. SCALAR, SPECTRUM, IMAGE
	# \param gMycnf mysql config file
	# \param gUser database user name
	# \param gPasswd database user password
	def initDBase(self,gDBname,gQuery, gFormat=None, gMycnf=None, gUser=None, gPasswd=None):
		self.elem.attrib["type"]="DB"
		da=NTag(self.elem,"query")
		da.elem.attrib["dbname"]=gDBname
		if gFormat:
			da.elem.attrib["format"]=gFormat
		if gUser:
			da.elem.attrib["user"]=gUser
		if gPasswd:
			da.elem.attrib["passwd"]=gPasswd
		if gMycnf:
			da.elem.attrib["mycnf"]=gMycnf
		da.elem.text=gQuery

        ## sets paramters for Tango device
	# \param gDevice device name
	# \param gDType type of the data object, i.e. attribute, property, command	
	# \param gDName name of the data object
	def initTango(self,gDevice,gDType,gDName):
		self.elem.attrib["type"]="TANGO"
		dv=NTag(self.elem,"device")
		dv.elem.attrib["name"]=gDevice
		da=NTag(self.elem,"record")
		da.addTagAttr("type", gDType)
		da.addTagAttr("name", gDName)

        ## sets paramters for Client data
	# \param gDName name of the data object
	def initClient(self,gDName):
		self.elem.attrib["type"]="CLIENT"
		da=NTag(self.elem,"record")
		da.addTagAttr("name", gDName)
		

        ## sets paramters for Sardana data
	# \param gDoor sardana door
	# \param gDName name of the data object
	def initSardana(self,gDoor,gDName):
		self.elem.attrib["type"]="SARDANA"
		do=NTag(self.elem,"door")
		do.elem.attrib["name"]=gDoor
		da=NTag(self.elem,"record")
		da.addTagAttr("name", gDName)




## Tango device tag creator
class DevNGroup(NGroup):
	## constructor
	# \param parent parent ET tag element
	# \param devName tango device name
	# \param gName name attribute
	# \param gType type attribute
	def __init__(self,parent,devName,gName,gType=""):
		NGroup.__init__(self,parent,gName,gType)
		## device proxy
		self.proxy=DeviceProxy(devName)
		## list of device properties
		self.prop=self.proxy.get_property_list('*')
		## fields of the device
		self.fields={}
		print "PROP",self.prop
		for pr in self.prop:
			self.addAttr(pr,"NX_CHAR",str(self.proxy.get_property(pr)[pr][0]))

                ## device attirbutes			
		self.attr=self.proxy.get_attribute_list()
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
			if str(cf.data_format).split('.')[-1] == "SPECTRUM":
				da=self.proxy.read_attribute(at)
				d=NDimensions(self.fields[at].elem,"1")
				d.dim("1",str(da.dim_x))
			if str(cf.data_format).split('.')[-1] == "IMAGE":
				da=self.proxy.read_attribute(at)
				d=NDimensions(self.fields[at].elem,"2")
				d.dim("1",str(da.dim_x))
				d.dim("2",str(da.dim_y))
				
			if cf.unit != 'No unit':
				self.fields[at].setUnits(cf.unit)
			self.fields[at].setUnits(cf.unit)
			      
			if cf.description != 'No description':
				self.fields[at].addDoc(cf.description)
			self.addAttr('URL',"NX_CHAR","tango://"+devName)
			
			sr=NDSource(self.fields[at].elem,"STEP","haso228k.desy.de","10000")
			sr.initTango(devName,"attribute",at)
				
#		print self.proxy.attribute_list_query()
			
			
## XML file object
class XMLFile:
	## constructor
	# \param fname XML file name
	def __init__(self,fname):
		## XML file name
		self.fname=fname
		## ET root instance
		self.root=ET.Element("definition")
		
	## prints pretty XML making use of minidom
	# \param etNode node from ET	
	# \returns pretty XML string 	
	def prettyPrintET(self,etNode):
		mxml = xml.dom.minidom.parseString(ET.tostring(etNode))
		return mxml.toprettyxml()


	## dumps XML structure into the XML file
	# \brief It opens XML file, calls prettyPrintET  and closes the XML file
	def dump(self):
		myfile = open(self.fname, "w")
		myfile.write(self.prettyPrintET(self.root))
		myfile.close()

	
 
		


if __name__ == "__main__":
	## handler to XML file
	df=XMLFile("test.xml")
	## entry
	en = NGroup(df.root,"entry","NXentry")
	## instrument
	ins = NGroup(en.elem,"instrument","NXinstrument")
	##	NXsource
	src = NGroup(ins.elem,"source","NXsource")
	## field
	f = NField(src.elem,"distance","NX_FLOAT")
	f.setUnits("m")
	f.setText("100.")
	f = NField(src.elem,"db_devices","NX_CHAR")
	## dimensions
	d=NDimensions(f.elem,"2")
	d.dim("1","151")
	d.dim("2","2")
	## source
	sr=NDSource(f.elem,"STEP","haso228k.desy.de")
	sr.initDBase("tango","SELECT name,pid FROM device","IMAGE")
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
	sr.initTango("p09/motor/exp.01","attribute","Position")
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

	##       NXcrystal	
	cr = NGroup(ins.elem,"crystal","NXcrystal")
	f = NField(cr.elem,"distance","NX_FLOAT")
	f.setUnits("A")
	f.addDoc("Optimum diffracted wavelength")
	d=NDimensions(f.elem,"1")
	d.dim("1","10")

        ##       NXdetector	
	de = NGroup(ins.elem,"detector","NXdetector")
	f = NField(de.elem,"azimuthal_angle","NX_FLOAT")
	f = NField(de.elem,"beam_center_x","NX_FLOAT")
	f = NField(de.elem,"beam_center_y","NX_FLOAT")
#	f = NField(de.elem,"data","NX_FLOAT")
	f = NField(de.elem,"data","NX_UINT32")
	d=NDimensions(f.elem,"2")
#	d.dim("1","100")
#	d.dim("2","100")
	d.dim("1","2")
	d.dim("2","2")
#	sr=NDSource(f.elem,"STEP","haso228k.desy.de","10000")
	sr=NDSource(f.elem,"FINAL","haso228k.desy.de","10000")
#	sr=NDSource(f.elem,"INIT","haso228k.desy.de","10000")
	sr.initTango("p09/tst/exp.01","attribute","MyImageAttribute")
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
	sr=NDSource(f.elem,"FINAL","haso228k.desy.de","10000")
	sr.initTango("p09/motor/exp.01","attribute","Position")


        ##	NXdata
	da = NGroup(en.elem,"data","NXdata")
	## link
	l= NLink(da.elem,"polar_angle", "/NXentry/NXinstrument/NXdetector/polar_angle")
	l.addDoc("Link to polar angle in /NXentry/NXinstrument/NXdetector")
	l= NLink(da.elem,"data","/NXentry/NXinstrument/NXdetector/data")
	l.addDoc("Link to data in /NXentry/NXinstrument/NXdetector")


	df.dump()

 
