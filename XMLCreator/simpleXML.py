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
## \file simpleXML.py
# creator of XML files

import PyTango 
import sys, os, time
import xml.etree.ElementTree as ET
import xml.dom.minidom



## tag wrapper
class NTag(object):
	## constructor
	# \param tagName tag name
	# \param parent parent ET tag element
	# \param nameAttr value of name attribute
	# \param typeAttr value of type attribute
	def __init__(self, parent, tagName, nameAttr="", typeAttr=""):
		## parent tag
		self._parent = parent
		## tag element from ET
		self.elem = ET.SubElement(parent, tagName)
		if nameAttr != "" :
			self.elem.attrib["name"] = nameAttr
		if typeAttr !=  "" :
			self.elem.attrib["type"] = typeAttr

        ## adds tag attribute
	# \param name attribute name		
	# \param value attribute value		
	def addTagAttr(self, name, value):
		self.elem.attrib[name] = value

        ## sets tag content
	# \param text tag content
	def setText(self, text):
		self.elem.text = text


        ## adds tag content
	# \param text tag content
	def addText(self, text):
		self.elem.text = self.elem.text + text


## Attribute tag wrapper	
class NAttr(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param nameAttr name attribute
	# \param typeAttr type attribute
	def __init__(self, parent, nameAttr, typeAttr=""):
		NTag.__init__(self, parent, "attribute", nameAttr, typeAttr)

## Group tag wrapper
class NGroup(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param nameAttr name attribute
	# \param typeAttr type attribute
	def __init__(self, parent, nameAttr, typeAttr=""):
		NTag.__init__(self, parent, "group", nameAttr, typeAttr)
		## list of doc tag contents
		self._doc = []
		## container with attribute tag wrappers
		self._gAttr = {}

        ## adds doc tag content
	# \param doc doc tag content	
	def addDoc(self, doc):
		self._doc.append(ET.SubElement(self.elem, "doc"))
		self._doc[-1].text = doc


        ## adds attribute tag
	# \param attrName name attribute
	# \param attrType type attribute
	# \param attrValue content of the attribute tag
	def addAttr(self, attrName, attrType, attrValue=""):
		print attrName, attrType, attrValue
		at = NAttr(self.elem, attrName, attrType)
		self._gAttr[attrName] = at
		if attrValue != "":
			at.setText(attrValue)
			pass


## Link tag wrapper
class NLink(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param nameAttr name attribute
	# \param gTarget target attribute
	def __init__(self, parent, nameAttr, gTarget):
		NTag.__init__(self, parent, "link", nameAttr)
		self.addTagAttr("target", gTarget)
		## list of doc tag contents
		self._doc = []

        ## adds doc tag content
	# \param doc doc tag content	
	def addDoc(self, doc):
		self._doc.append(ET.SubElement(self.elem, "doc"))
		self._doc[-1].text = doc


## Dimensions tag wrapper
class NDimensions(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param rankAttr  rank attribute
	def __init__(self, parent, rankAttr):
		NTag.__init__(self, parent, "dimensions")
		self.addTagAttr("rank", rankAttr)
		## container with dim tag wrapper
		self.dims = {}
	## adds dim tag 
	# \param indexAttr index attribute	
	# \param valueAttr value attribute
	def dim(self, indexAttr, valueAttr):
		self.dims[indexAttr] = NDim(self.elem, indexAttr, valueAttr)
			
		
## Dim tag wrapper
class NDim(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param indexAttr index attribute	
	# \param valueAttr value attribute
	def __init__(self, parent, indexAttr, valueAttr):
		NTag.__init__(self, parent, "dim")
		self.addTagAttr("index", indexAttr)
		self.addTagAttr("value", valueAttr)
		
		

## Field tag wrapper
class NField(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param nameAttr name attribute
	# \param typeAttr type attribute
	def __init__(self, parent, nameAttr, typeAttr=""):
		NTag.__init__(self, parent, "field", nameAttr, typeAttr)
		## list of doc tag contents
		self._doc = []
		## container with attribute tag wrappers
		self._attr = {}
		
	## sets the field unit
	# \param unitsAttr the field unit	
	def setUnits(self, unitsAttr):
		self.addTagAttr("units", unitsAttr)

        ## adds doc tag content
	# \param doc doc tag content	
	def addDoc(self, doc):
		self._doc.append(ET.SubElement(self.elem, "doc"))
		self._doc[-1].text = doc

        ## adds attribute tag
	# \param attrName name attribute
	# \param attrType type attribute
	# \param attrValue content of the attribute tag
	def addAttr(self, attrName, attrType, attrValue=""):
		self._attr[attrName] = NAttr(self.elem, attrName, attrType)
 		if attrValue != '':
			self._attr[attrName].setText(attrValue)



## Source tag wrapper
class NDSource(NTag):
	## constructor
	# \param parent parent ET tag element
	# \param strategy strategy of data writing, i.e. INIT, STEP, FINAL
	def __init__(self, parent, strategy):
		NTag.__init__(self, parent, "datasource")
		self.elem.attrib["strategy"] = strategy

	## sets parameters of DataBase		
	# \param dbname name of used DataBase
	# \param query database query
	# \param dbtype type of the database, i.e. MYSQL, PGSQL, ORACLE
	# \param format format of the query output, i.e. SCALAR, SPECTRUM, IMAGE
	# \param mycnf MYSQL config file
	# \param user database user name
	# \param passwd database user password
	# \param dsn DSN string to initialize ORACLE and PGSQL databases
	# \param mode mode for ORACLE databases, i.e. SYSDBA or SYSOPER		
	# \param host name of the host
	# \param port port number
	def initDBase(self, dbtype, query, dbname=None,  format=None,  mycnf=None,  user=None,  
		      passwd=None,  dsn=None,  mode=None, host=None, port=None):
		self.elem.attrib["type"] = "DB"
		da = NTag(self.elem, "database")
		da.elem.attrib["dbtype"] = dbtype


		if host:
			da.elem.attrib["hostname"] = host
		if port:
			da.elem.attrib["port"] = port

		if dbname:
			da.elem.attrib["dbname"] = dbname
		if user:
			da.elem.attrib["user"] = user
		if passwd:
			da.elem.attrib["passwd"] = passwd
		if mycnf:
			da.elem.attrib["mycnf"] = mycnf
		if mode:
			da.elem.attrib["mode"] = mode
		if dsn:
			da.elem.text = dsn
		

		da = NTag(self.elem, "query")
		if format:
			da.elem.attrib["format"] = format
		da.elem.text = query

        ## sets paramters for Tango device
	# \param device device name
	# \param memberType type of the data object, i.e. attribute,  property, command	
	# \param recordName name of the data object
	# \param host host name
	# \param port port
	def initTango(self, device, memberType, recordName, host=None, port=None):
		self.elem.attrib["type"] = "TANGO"
		dv = NTag(self.elem, "device")
		dv.elem.attrib["name"] = device

		if host:
			dv.elem.attrib["hostname"] = host
		if port:
			dv.elem.attrib["port"] = port

		da = NTag(self.elem, "record")
		da.addTagAttr("type", memberType)
		da.addTagAttr("name", recordName)

        ## sets paramters for Client data
	# \param recordName name of the data object
	def initClient(self, recordName):
		self.elem.attrib["type"] = "CLIENT"
		da = NTag(self.elem, "record")
		da.addTagAttr("name", recordName)
		

        ## sets paramters for Sardana data
	# \param door sardana door
	# \param recordName name of the data object
	# \param host host name
	# \param port port
	def initSardana(self, door, recordName, host=None, port=None):
		self.elem.attrib["type"] = "SARDANA"
		do = NTag(self.elem, "door")
		do.elem.attrib["name"] = door
		if host:
			do.elem.attrib["hostname"] = host
		if port:
			do.elem.attrib["port"] = port
		da = NTag(self.elem, "record")
		da.addTagAttr("name", recordName)




## Tango device tag creator
class NDeviceGroup(NGroup):
	
        ## Tango types
	tTypes = ["DevVoid",
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
	
        ## NeXuS types corresponding to the Tango types
	nTypes = ["NX_CHAR",
		  "NX_BOOLEAN",
		  "NX_INT32",
		  "NX_INT32",
		  "NX_FLOAT32",
		  "NX_FLOAT64",
		  "NX_UINT32",
		  "NX_UINT32",
		  "NX_CHAR",
		  "NX_CHAR",
		  "NX_INT32",
		  "NX_INT32",
		  "NX_FLOAT32",
		  "NX_FLOAT64",
		  "NX_UINT32",
		  "NX_UINT32",
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
		  "NX_INT32",
		  "NX_CHAR"]
	
	## constructor
	# \param parent parent ET tag element
	# \param deviceName tango device name
	# \param nameAttr name attribute
	# \param typeAttr type attribute
	# \param commands if we call the commands
	# \param blackAttrs list of excluded attributes
	def __init__(self, parent, deviceName, nameAttr, typeAttr="", commands=True, blackAttrs=[]):
		NGroup.__init__(self, parent, nameAttr, typeAttr)
		## device proxy
		self._proxy = PyTango.DeviceProxy(deviceName)
		## fields of the device
		self._fields = {}
		## blacklist for Attributes
		self._blackAttrs = blackAttrs
		## the device name
		self._deviceName = deviceName

		self._fetchProperties()	
		self._fetchAttributes()	
		if commands:		
			self._fetchCommands()
	

	## fetches properties	
	# \brief It collects the device properties
	def _fetchProperties(self):	
		prop = self._proxy.get_property_list('*')
		print "PROP", prop
		for pr in prop:
			self.addAttr(pr, "NX_CHAR", str(self._proxy.get_property(pr)[pr][0]))
			if pr not in self._fields:
				self._fields[pr] = NField(self.elem, pr, "NX_CHAR")
				sr = NDSource(self._fields[pr].elem, "STEP")
				sr.initTango(self._deviceName, "property", pr, host="haso228k.desy.de", port="10000")

	## fetches Attributes
	# \brief collects the device attributes
	def _fetchAttributes(self):	

                ## device attirbutes			
		attr = self._proxy.get_attribute_list()
		for at in attr:
			
			print at
			cf = self._proxy.attribute_query(at)
			print "QUERY"
			print cf
			print cf.name
			print cf.data_format
			print cf.standard_unit
			print cf.display_unit
			print cf.unit
			print self.tTypes[cf.data_type]
			print self.nTypes[cf.data_type]
			print cf.data_type
			
			
			if at not in self._fields and  at not in self._blackAttrs:
				self._fields[at] = NField(self.elem, at, self.nTypes[cf.data_type])
				if str(cf.data_format).split('.')[-1] == "SPECTRUM":
					da = self._proxy.read_attribute(at)
					d = NDimensions(self._fields[at].elem, "1")
					d.dim("1", str(da.dim_x))
				if str(cf.data_format).split('.')[-1] == "IMAGE":
					da = self._proxy.read_attribute(at)
					d = NDimensions(self._fields[at].elem, "2")
					d.dim("1", str(da.dim_x))
					d.dim("2", str(da.dim_y))
				
				if cf.unit != 'No unit':
					self._fields[at].setUnits(cf.unit)
					self._fields[at].setUnits(cf.unit)
			      
				if cf.description != 'No description':
					self._fields[at].addDoc(cf.description)
				self.addAttr('URL', "NX_CHAR", "tango://"+self._deviceName)
			
				sr = NDSource(self._fields[at].elem, "STEP")
				sr.initTango(self._deviceName, "attribute", at, host="haso228k.desy.de", port="10000")

#		print self._proxy.attribute_list_query()

	## fetches commands
	# \brief It collects results of the device commands
	def _fetchCommands(self):	
                ## list of the device commands
		cmd = self._proxy.command_list_query()
		print "COMMANDS", cmd
		for cd in cmd:
			if str(cd.in_type).split(".")[-1] == "DevVoid" \
				    and str(cd.out_type).split(".")[-1] != "DevVoid" \
				    and str(cd.out_type).split(".")[-1] in self.tTypes \
				    and cd.cmd_name not in self._fields:
				self._fields[cd.cmd_name] = \
				    NField(self.elem, cd.cmd_name, \
						   self.nTypes[self.tTypes.index(str(cd.out_type).split(".")[-1])])
				sr = NDSource(self._fields[cd.cmd_name].elem, "STEP")
				sr.initTango(self._deviceName, "command", cd.cmd_name,\
						     host="haso228k.desy.de", port="10000")
				
						
				
			
			
## XML file object
class XMLFile(object):
	## constructor
	# \param fname XML file name
	def __init__(self, fname):
		## XML file name
		self.fname = fname
		## ET root instance
		self.root = ET.Element("definition")
		
	## prints pretty XML making use of minidom
	# \param etNode node from ET	
	# \returns pretty XML string 	
	def prettyPrintET(self, etNode):
		mxml = xml.dom.minidom.parseString(ET.tostring(etNode))
		return mxml.toprettyxml(indent="  ")


	## dumps XML structure into the XML file
	# \brief It opens XML file, calls prettyPrintET  and closes the XML file
	def dump(self):
		myfile = open(self.fname, "w")
		myfile.write(self.prettyPrintET(self.root))
		myfile.close()

	
 
		


if __name__ == "__main__":
	## handler to XML file
	df = XMLFile("test.xml")
	## entry
	en = NGroup(df.root, "entry1", "NXentry")
	## instrument
	ins = NGroup(en.elem, "instrument", "NXinstrument")
	##	NXsource
	src = NGroup(ins.elem, "source", "NXsource")
	## field
	f = NField(src.elem, "distance", "NX_FLOAT")
	f.setUnits("m")
	f.setText("100.")


	f = NField(src.elem, "single_mysql_record_string", "NX_CHAR")
	## dimensions
	d = NDimensions(f.elem, "1")
	d.dim("1", "1")
	## source
	sr = NDSource(f.elem, "STEP")
	sr.initDBase("MYSQL", "SELECT pid FROM device limit 1", "tango", "SPECTRUM", host="haso228k.desy.de")

	f = NField(src.elem, "single_mysql_record_int", "NX_INT")
	## dimensions
	d = NDimensions(f.elem, "1")
	d.dim("1", "1")
	## source
	sr = NDSource(f.elem, "STEP")
	sr.initDBase("MYSQL", "SELECT pid FROM device limit 1", "tango", "SPECTRUM", host="haso228k.desy.de")


	f = NField(src.elem, "mysql_record", "NX_CHAR")
	## dimensions
	d = NDimensions(f.elem, "2")
	d.dim("1", "151")
	d.dim("2", "2")
	## source
	sr = NDSource(f.elem, "STEP")
	sr.initDBase("MYSQL", "SELECT name, pid FROM device limit 151", "tango", "IMAGE", host="haso228k.desy.de")


	f = NField(src.elem, "pgsql_record", "NX_CHAR")
	## dimensions
	d = NDimensions(f.elem, "2")
	d.dim("1", "3")
	d.dim("2", "5")
	## source
	sr = NDSource(f.elem, "STEP")
	sr.initDBase("PGSQL", "SELECT * FROM weather limit 3", "mydb", "IMAGE")

 
	f = NField(src.elem, "oracle_record", "NX_CHAR")
	## dimensions
	d = NDimensions(f.elem, "1")
	d.dim("1", "19")
	## source
	sr = NDSource(f.elem, "STEP")
	sr.initDBase("ORACLE", "select * from (select * from telefonbuch) where ROWNUM <= 19", user='read', passwd='****', format="SPECTRUM", dsn='(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST=dbsrv01.desy.de)(PORT=1521))(LOAD_BALANCE=yes)(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=desy_db.desy.de)(FAILOVER_MODE=(TYPE=NONE)(METHOD=BASIC)(RETRIES=180)(DELAY=5))))', host="haso228k.desy.de")
	f = NField(src.elem, "type", "NX_CHAR")
	f.setText("Synchrotron X-ray Source")
	f = NField(src.elem, "name", "NX_CHAR")
	f.setText("PETRA-III")
	f.addAttr("short_name", "NX_CHAR", "P3")
	f = NField(src.elem, "probe", "NX_CHAR")
	f.setText("x-ray")
	f = NField(src.elem, "power", "NX_FLOAT")
	f.setUnits("W")
	f.setText("1")
	sr = NDSource(f.elem, "INIT")
	sr.initTango("p09/motor/exp.01", "attribute", "Position", host="haso228k.desy.de", port="10000")
	f = NField(src.elem, "emittance_x", "NX_FLOAT")
	f.setUnits("nm rad")
	f.setText("0.2")
	sr = NDSource(f.elem, "STEP")
	sr.initClient("emitannce_x");
	f = NField(src.elem, "emittance_y", "NX_FLOAT")
	f.setUnits("nm rad")
	f.setText("0.2")
	sr = NDSource(f.elem, "STEP")
	sr.initSardana("door1", "emitannce_y", host="haso228k.desy.de", port="10000");
	f = NField(src.elem, "sigma_x", "NX_FLOAT")
	f.setUnits("nm")
	f.setText("0.1")
	f = NField(src.elem, "sigma_y", "NX_FLOAT")
	f.setUnits("nm")
	f.setText("0.1")
	f = NField(src.elem, "flux", "NX_FLOAT")
	f.setUnits("s-1 cm-2")
	f.setText("0.1")
	f = NField(src.elem, "energy", "NX_FLOAT")
	f.setUnits("GeV")
	f.setText("0.1")
	f = NField(src.elem, "current", "NX_FLOAT")
	f.setUnits("A")
	f.setText("10")
	f = NField(src.elem, "voltage", "NX_FLOAT")
	f.setUnits("V")
	f.setText("10")
	f = NField(src.elem, "period", "NX_FLOAT")
	f.setUnits("microseconds")
	f.setText("1")
	f = NField(src.elem, "target_material", "NX_CHAR")
	f.setText("C")

	##       NXcrystal	
	cr = NGroup(ins.elem, "crystal", "NXcrystal")
	f = NField(cr.elem, "distance", "NX_FLOAT")
	f.setUnits("A")
	f.addDoc("Optimum diffracted wavelength")
	d = NDimensions(f.elem, "1")
	d.dim("1", "10")

        ##       NXdetector	
	de = NGroup(ins.elem, "detector", "NXdetector")
	f = NField(de.elem, "azimuthal_angle", "NX_FLOAT")
	f.setText("0.1")
	f = NField(de.elem, "beam_center_x", "NX_FLOAT")
	f.setText("0.0001")
	f = NField(de.elem, "beam_center_y", "NX_FLOAT")
	f.setText("-0.00012")
#	f = NField(de.elem, "data", "NX_FLOAT")
	f = NField(de.elem, "data", "NX_UINT32")
	d = NDimensions(f.elem, "2")
#	d.dim("1", "100")
#	d.dim("2", "100")
	d.dim("1", "2")
	d.dim("2", "2")
#	sr = NDSource(f.elem, "STEP")
	sr = NDSource(f.elem, "FINAL")
#	sr = NDSource(f.elem, "INIT")
	sr.initTango("p09/tst/exp.01", "attribute", "MyImageAttribute", host="haso228k.desy.de", port="10000")
	f = NField(de.elem, "distance", "NX_FLOAT")
	f.setText("10.00012")
	f = NField(de.elem, "polar_angle", "NX_FLOAT")
	f.addDoc(""" Optional rotation angle for the case when the powder diagram has been obtained
	  through an omega-2theta scan like from a traditional single detector powder
	  diffractometer""")
	d = NDimensions(f.elem, "1")
	d.dim("1", "100")
	f = NField(de.elem, "rotation_angle", "NX_FLOAT")
	f.setText("0.0")
	f = NField(de.elem, "x_pixel_size", "NX_FLOAT")
	f.setText("0.01")
	f = NField(de.elem, "y_pixel_size", "NX_FLOAT")
	f.setText("0.01")
	sr = NDSource(f.elem, "FINAL")
	sr.initTango("p09/motor/exp.01", "attribute", "Position", host="haso228k.desy.de", port="10000")


        ##	NXdata
	da = NGroup(en.elem, "data", "NXdata")
	## link
	l = NLink(da.elem, "polar_angle", "/NXentry/NXinstrument/NXdetector/polar_angle")
	l.addDoc("Link to polar angle in /NXentry/NXinstrument/NXdetector")
	l = NLink(da.elem, "data", "/NXentry/NXinstrument/NXdetector/data")
	l.addDoc("Link to data in /NXentry/NXinstrument/NXdetector")


	df.dump()

 
