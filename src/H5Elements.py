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
"""@package docstring
@file H5Elements.py
"""
                                                                      
import pni.nx.h5 as nx

from numpy  import * 

from DataSource import *

from DataHolder import *


from Element import *



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



# A map of NEXUS : pninx types 
mt={"NX_FLOAT32":"float32","NX_FLOAT64":"float64","NX_FLOAT":"float64","NX_NUMBER":"float64","NX_INT":"int64","NX_INT64":"int64","NX_INT32":"int32","NX_UINT64":"uint64","NX_UINT32":"uint32","NX_DATE_TIME":"string","NX_CHAR":"string","NX_BOOLEAN":"int32"}

# A map of tag attribute types 
dA={"signal":"NX_INT","axis":"NX_INT","primary":"NX_INT32","offset":"NX_INT","stride":"NX_INT","vector":"NX_FLOATVECTOR",
       "file_time":"NX_DATE_TIME","file_update_time":"NX_DATE_TIME","restricted":"NX_INT","ignoreExtraGroups":"NX_BOOLEAN",
    "ignoreExtraFields":"NX_BOOLEAN","ignoreExtraAttributes":"NX_BOOLEAN","minOccus":"NX_INT","maxOccus":"NX_INT"
    }



class FElement(Element):
    """A tag element corresponding to one of H5 objects """

    def __init__(self,name,attrs,last,obj=None):
        """ Constructor """
        Element.__init__(self,name,attrs,last)
        ## Stored tag object 
        if obj:
            self.fObject=obj
        self.source=None


    def run(self):
        if self.source:
            self.source.getData()



class EField(FElement):        
    def __init__(self,name,attrs,last):
        FElement.__init__(self,name,attrs,last)
        self.rank="0"
        self.lengths={}
        self.tpAttrs={}
        self.extraD=False


    def store(self,name):
        print "Storing field"

        self.extraD=False
        if self.source and self.source.isValid() and self.source.strategy == "STEP":
            self.extraD=True
            
        if "name" in self.tAttrs.keys():
            nm=self.tAttrs["name"]
            if "type" in self.tAttrs.keys():
                tp=mt[self.tAttrs["type"]]
            else:
                tp="string"
        else:
            raise " Field without a name !!!"


        shape=[]
        if self.extraD:
            shape.append(0)
        if int(self.rank)>1  or (int(self.rank)>0 and int(self.lengths["1"].encode())>=1):
            for i in range(int(self.rank)):
                si=str(i+1)
                if si in self.lengths.keys():
                    if int(self.lengths[si]) >0:
                        shape.append(int(self.lengths[si]))
                else:
                    raise "Wrongly defined shape"
        
#        print "shape:", shape


        if len(shape)>0:
#            if tp.encode() =='string':
#                shape.append(None)
                
            f=self.lastObject().create_field(nm.encode(),tp.encode(),shape)
        else:
            f=self.lastObject().create_field(nm.encode(),tp.encode())


        for key in self.tAttrs.keys():
            if key not in ["name"]:
                (f.attr(key.encode(),"string")).value=self.tAttrs[key].strip().encode()


        for key in self.tpAttrs.keys():
            if key not in ["name"]:
                (f.attr(key.encode(),mt[self.tpAttrs[key][0]].encode())).value=self.tpAttrs[key][1].strip().encode()

        self.fObject=f

        if self.source:
            if  self.source.isValid() :
                return self.source.strategy
        else:
            print "invalid dataSource"

    def run(self):
        if self.source:
            dh=self.source.getData()
            if dh:
#                print "shape", self.fObject.shape, dh.shape
                if not self.extraD:
                    if str(dh.format).split('.')[-1] == "SCALAR":
                        self.fObject.write(dh.value)
                    if str(dh.format).split('.')[-1] == "SPECTRUM":
                        self.fObject.write(dh.value)
                        pass
                    if str(dh.format).split('.')[-1] == "IMAGE":
                        pass
                else:
#                    print "DH type", dh.type
#                    print "DH format ",str(dh.format).split('.')[-1]
                    if str(dh.format).split('.')[-1] == "SCALAR":
                        self.fObject.grow()
#                        self.fObject[-1]=dh.value
                        if nTypes[tTypes.index(str(dh.type))] == "NX_CHAR":
                            self.fObject[self.fObject.shape[0]-1]=str(dh.value)
                        else:
                            self.fObject[self.fObject.shape[0]-1]=dh.value
                    if str(dh.format).split('.')[-1] == "SPECTRUM":
                        self.fObject.grow()
                        if nTypes[tTypes.index(str(dh.type))] == "NX_CHAR":
                            print "fO SHAPE:" , self.fObject.shape
                            arr=numpy.array(list((str(el)) for el in dh.value),self.fObject.dtype)
                            print "ARRAY SHAPE: ", arr.shape, len(arr.shape) 
                            print "ARRAY: ", arr
                            if len(arr.shape) == 1 and arr.shape[0] == 1:
                                self.fObject[self.fObject.shape[0]-1,:]=arr[0]
                            else:
                                self.fObject[self.fObject.shape[0]-1,:]=arr
                        else:
#                            print "fO SHAPE:" , self.fObject.shape
                            arr=dh.array(self.fObject.dtype)
#                            print "ARRAY SHAPE: ", dh.array(self.fObject.dtype).shape,len(arr.shape) 
#                            print "ARRAY: ", arr
                            if len(arr.shape) == 1 and arr.shape[0] == 1:
                                self.fObject[self.fObject.shape[0]-1,:]=arr[0]
                            else:                                
                                self.fObject[self.fObject.shape[0]-1,:]=arr
                    if str(dh.format).split('.')[-1] == "IMAGE":
                        self.fObject.grow()
                        if nTypes[tTypes.index(str(dh.type))] == "NX_CHAR":
#                            print "fO SHAPE:" , self.fObject.shape
                            val=dh.value
                            arr= numpy.array([ [ str(val[j][i]) for i in range(len(val[0])) ] 
                                               for j in range(len(val)) ],self.fObject.dtype)
#                            arr=numpy.array(list((str(el)) for el in dh.value),self.fObject.dtype)
#                            print "ARRAY SHAPE: ", arr.shape, len(arr.shape) 
#                            print "ARRAY: ", arr
                            self.fObject[self.fObject.shape[0]-1,:,:]=arr
                        else:
#                            print "fO SHAPE:" , self.fObject.shape
                            arr=dh.array(self.fObject.dtype)
#                            print "ARRAY SHAPE: ", dh.array(self.fObject.dtype).shape,len(arr.shape) 
#                            print "ARRAY: ", arr
                            self.fObject[self.fObject.shape[0]-1,:,:]=arr



        
class EGroup(FElement):        
    def __init__(self,name,attrs,last):
        FElement.__init__(self,name,attrs,last)

        self.tpAttrs={}

        if ("type" in attrs.keys()) and ("name" in attrs.keys()):
            print "type", type(self.lastObject())
            g=self.lastObject().create_group(attrs["name"].encode(),attrs["type"].encode())
        elif "type" in attrs.keys():
            g=self.lastObject().create_group(attrs["type"][2:].encode(),attrs["type"].encode())
        else:
            raise "The group type not defined !!!"
        self.fObject=g
        for key in attrs.keys() :
            if key not in ["name","type"]:
                if key in dA.keys():
                    (g.attr(key.encode(),mt[dA[key]].encode())).value=attrs[key].encode()
                else:
                    (g.attr(key.encode(),"string")).value=attrs[key].encode()

    def store(self,name):
        for key in self.tpAttrs.keys() :
            if key not in ["name","type"]:
                (self.fObject.attr(key.encode(),mt[self.tpAttrs[key][0]].encode())).value=self.tpAttrs[key][1].encode()



    def fetchName(self,groupTypes):
        print "fetching"
        if ("type" in self.tAttrs.keys()) and ("name" in self.tAttrs.keys()):
            groupTypes[self.tAttrs["type"]]=self.tAttrs["name"]
            print "typeGroup", groupTypes[self.tAttrs["type"]]
        elif "type" in self.tAttrs.keys():
            groupTypes[self.tAttrs["type"]]=self.tAttrs["type"][2:]
            print "typeGroup", groupTypes[self.tAttrs["type"]]
        else:
            raise "The group type not defined !!!"
        
        


class ELink(FElement):        
    def __init__(self,name,attrs,last):
        FElement.__init__(self,name,attrs,last)
        self.fObject=None

    def typesToNames(self,text,groupTypes):
        """  converts NXclass types to names in a path string"""
        sp= text.split("/")
        print "TTN:", sp 
        res="/"
        for gr in sp[:-1]:
            sgr=gr.split(":")
            print sgr
            if len(sgr)>1 :
                res="/".join([res,sgr[1]])
            else:
                if sgr[0] in groupTypes:
                    res="/".join([res,groupTypes[sgr[0]]])
                else:
                    print "sgr " ,sgr[0]
                    raise "No sgr[0] in  groupTypes " 
        res=res+"/"+sp[-1]
        print "TTN:", res 

        return res

        
    def createLink(self,groupTypes):
        if ("name" in self.tAttrs.keys()) and ("target" in self.tAttrs.keys()):
            print "linking ",self.lastObject() ,self.tAttrs["name"].encode()
            l=(self.lastObject()).link((self.typesToNames(self.tAttrs["target"],groupTypes)).encode(),
                                       self.tAttrs["name"].encode())
            print self.typesToNames(self.tAttrs["target"],groupTypes)
        else:
            raise "No name or type!!!"
        self.fObject=l
        for key in self.tAttrs.keys():
            print "Attrs:", key.encode(), self.tAttrs[key].encode()
          
                


class EAttribute(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)


    def store(self,name):
        print "Storing Attributes:", "".join(self.content)


        if "name" in self.tAttrs.keys(): 
            nm = self.tAttrs["name"]
            if "type" in self.tAttrs.keys() :
                tp = self.tAttrs["type"]
            else:        
                tp = "NX_CHAR"
                
            self.last.tpAttrs[nm]=(tp,("".join(self.content)).strip().encode())




class EFile(FElement):        
    def __init__(self,name,attrs,last,obj):
        FElement.__init__(self,name,attrs,last,obj)



class EDoc(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)

    def store(self,name):
        self.last.doc=self.last.doc + "".join(self.content)            
        print "Added doc\n", self.last.doc

class ESymbol(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)

    def store(self,name):
# @TODO
        if "name" in self.tAttrs.keys():
            self.symbols[self.tAttrs["name"]]=self.last().doc


class ERecord(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "type" in attrs.keys():
            self.beforeLast().source.type=attrs["type"]
        if "name" in attrs.keys():
            self.beforeLast().source.name=attrs["name"]


class EDevice(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "name" in attrs.keys():
            self.beforeLast().source.device=attrs["name"]

class EDoor(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "name" in attrs.keys():
            self.beforeLast().source.door=attrs["name"]


class EQuery(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "dbname" in attrs.keys():
            self.beforeLast().source.type=attrs["dbname"]
    def store(self,name):
        self.beforeLast().source.query= ("".join(self.content)).strip()        

 
class EDimensions(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "rank" in attrs.keys():
            self.last.rank=attrs["rank"]
            print "setting rank to ", self.last.rank

class EDim(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if ("index"  in attrs.keys()) and  ("value"  in attrs.keys()) :
            self.beforeLast().lengths[attrs["index"]]=attrs["value"]
            print "setting dim %s to %s " % (attrs["index"], attrs["value"])


