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
## \package ndts nexdatas
## \file H5Elements.py
# NeXus runnable elements
                                                                      
import pni.nx.h5 as nx

from numpy  import * 

from DataSource import *

from DataHolder import *


from Element import *

from FieldArray import *

from Types import *


## NeXuS runnable tag element
# tag element corresponding to one of H5 objects 
class FElement(Element):
    
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    # \param obj H5 file object
    def __init__(self,name,attrs,last,obj=None):
        Element.__init__(self,name,attrs,last)
        ## stored H5 file object 
        self.fObject=None
        if obj:
            self.fObject=obj
        ## data source    
        self.source=None

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        if self.source:
            self.source.getData()


## field H5 tag element
class EField(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        FElement.__init__(self,name,attrs,last)
        ## rank of the field
        self.rank="0"
        ## shape of the field
        self.lengths={}
        ## dictionary with attribures from sepatare attribute tags
        self.tpAttrs={}
        ## if field is stored in STEP mode
        self.extraD=False
        ## if field array is splitted into columns
        self.splitArray=False

    ## stores the tag content
    # \param name the tag name    
    def store(self,name):
        print "Storing field"

        self.extraD=False
        if self.source and self.source.isValid() and self.source.strategy == "STEP":
            self.extraD=True
            
        if "name" in self.tAttrs.keys():
            nm=self.tAttrs["name"]
            if "type" in self.tAttrs.keys():
                tp=NTP.mt[self.tAttrs["type"]]
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
                
        if len(shape)> 1 and tp.encode() == "string":
            self.splitArray=True

        if len(shape)>0:
            if self.splitArray:
                f=FieldArray(self.lastObject(),nm.encode(),tp.encode(),shape)
            else:
                f=self.lastObject().create_field(nm.encode(),tp.encode(),shape)
        else:
            f=self.lastObject().create_field(nm.encode(),tp.encode())


        for key in self.tAttrs.keys():
            if key not in ["name"]:
                (f.attr(key.encode(),"string")).value=self.tAttrs[key].strip().encode()

        for key in self.tpAttrs.keys():
            if key not in ["name"]:
                (f.attr(key.encode(),NTP.mt[self.tpAttrs[key][0]].encode())).value=self.tpAttrs[key][1].strip().encode()

        self.fObject=f

        if self.source:
            if  self.source.isValid() :
                return self.source.strategy
        else:
            print "invalid dataSource"

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        if self.source:
            dh=self.source.getData()
            if dh:
#                print "shape", self.fObject.shape, dh.shape
                if not self.extraD:
                    if str(dh.format).split('.')[-1] == "SCALAR":
                        self.fObject.write(dh.value)
                    if str(dh.format).split('.')[-1] == "SPECTRUM":
                        self.fObject.write(dh.array(self.fObject.dtype))
                    if str(dh.format).split('.')[-1] == "IMAGE":
                        self.fObject.write(dh.array(self.fObject.dtype))
                else:
#                    print "DH type", dh.type
#                    print "DH format ",str(dh.format).split('.')[-1]
                    if str(dh.format).split('.')[-1] == "SCALAR":
                        self.fObject.grow()
#                        self.fObject[-1]=dh.value
                        if NTP.nTypes[NTP.tTypes.index(str(dh.type))] == "NX_CHAR":
                            self.fObject[self.fObject.shape[0]-1]=str(dh.value)
                        else:
                            self.fObject[self.fObject.shape[0]-1]=dh.value
                    if str(dh.format).split('.')[-1] == "SPECTRUM":
                        self.fObject.grow()
                        if NTP.nTypes[NTP.tTypes.index(str(dh.type))] == "NX_CHAR":
                            print "fO SHAPE:" , self.fObject.shape
                            arr=numpy.array(list((str(el)) for el in dh.value),self.fObject.dtype)
                            print "ARRAY SHAPE: ", arr.shape, len(arr.shape) 
#                            print "ARRAY: ", arr
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
                        if str(dh.type) not in NTP.tTypes or NTP.nTypes[NTP.tTypes.index(str(dh.type))] == "NX_CHAR":
                            #                            print "fO SHAPE:" , self.fObject.shape
                            val=dh.value
                            larr=[ [ str(val[j][i]) for i in range(len(val[0])) ] for j in range(len(val)) ]
                            print self.fObject.dtype
                            arr= numpy.array(larr)
#                            arr= numpy.array(larr,self.fObject.dtype)
#                            arr=numpy.array(list((str(el)) for el in dh.value),self.fObject.dtype)
#                            print "ARRAY SHAPE: ", arr.shape, len(arr.shape) 
#                            print "ARRAY: ", arr
                            print "my shape:", self.fObject.shape
                            self.fObject[self.fObject.shape[0]-1,:,:]=arr
                        else:
#                            print "fO SHAPE:" , self.fObject.shape
                            arr=dh.array(self.fObject.dtype)
#                            print "ARRAY SHAPE: ", dh.array(self.fObject.dtype).shape,len(arr.shape) 
#                            print "ARRAY: ", arr
                            self.fObject[self.fObject.shape[0]-1,:,:]=arr



## group H5 tag element        
class EGroup(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        FElement.__init__(self,name,attrs,last)

        ## dictionary with attribures from sepatare attribute tags
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
                if key in NTP.dA.keys():
                    (g.attr(key.encode(),NTP.mt[NTP.dA[key]].encode())).value=attrs[key].encode()
                else:
                    (g.attr(key.encode(),"string")).value=attrs[key].encode()

    ## stores the tag content
    # \param name the tag name    
    def store(self,name):
        for key in self.tpAttrs.keys() :
            if key not in ["name","type"]:
                (self.fObject.attr(key.encode(),NTP.mt[self.tpAttrs[key][0]].encode())).value=self.tpAttrs[key][1].encode()


    ## fetches the type and the name of the current group            
    # \param groupTypes dictionary with the group type:name pairs            
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
        
        


## link H5 tag element        
class ELink(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        FElement.__init__(self,name,attrs,last)
        self.fObject=None

    ## converts types to Names using groupTypes dictionary
    # \param text original directory     
    # \param groupTypes dictionary with type:name group pairs
    # \returns directory defined by group namesS    
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

        
    ## creates the link the H5 file
    # \param groupTypes dictionary with type:name group pairs
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
          
                


## attribute tag element        
class EAttribute(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)


    ## stores the tag content
    # \param name the tag name    
    def store(self,name):
        print "Storing Attributes:", "".join(self.content)


        if "name" in self.tAttrs.keys(): 
            nm = self.tAttrs["name"]
            if "type" in self.tAttrs.keys() :
                tp = self.tAttrs["type"]
            else:        
                tp = "NX_CHAR"
                
            self.last.tpAttrs[nm]=(tp,("".join(self.content)).strip().encode())




## file H5 element        
class EFile(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    # \param obj H5 file object
    def __init__(self,name,attrs,last,obj):
        FElement.__init__(self,name,attrs,last,obj)



## doc tag element        
class EDoc(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)

    ## stores the tag content
    # \param name the tag name    
    def store(self,name):
        self.beforeLast().doc=self.beforeLast().doc + "".join(self.content)            
        print "Added doc\n", self.beforeLast().doc

## symbol tag element        
class ESymbol(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        ## dictionary with symbols
        self.symbols={}

    ## stores the tag content
    # \param name the tag name    
    def store(self,name):
        if "name" in self.tAttrs.keys():
            self.symbols[self.tAttrs["name"]]=self.last().doc


## record tag element        
class ERecord(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "type" in attrs.keys():
            self.beforeLast().source.type=attrs["type"]
        if "name" in attrs.keys():
            self.beforeLast().source.name=attrs["name"]


## device tag element        
class EDevice(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "name" in attrs.keys():
            self.beforeLast().source.device=attrs["name"]

## door tag element        
class EDoor(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "name" in attrs.keys():
            self.beforeLast().source.door=attrs["name"]


## query tag element        
class EQuery(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "format" in attrs.keys():
            self.beforeLast().source.format=attrs["format"]

    ## stores the tag content
    # \param name the tag name    
    def store(self,name):
        self.beforeLast().source.query= ("".join(self.content)).strip()        


## Database tag element        
class EDatabase(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "dbname" in attrs.keys():
            self.beforeLast().source.dbname=attrs["dbname"]
        if "dbtype" in attrs.keys():
            self.beforeLast().source.dbtype=attrs["dbtype"]
        if "user" in attrs.keys():
            self.beforeLast().source.user=attrs["user"]
        if "passwd" in attrs.keys():
            self.beforeLast().source.passwd=attrs["passwd"]
        if "mode" in attrs.keys():
            self.beforeLast().source.format=attrs["mode"]
        if "mycnf" in attrs.keys():
            self.beforeLast().source.mycnf=attrs["mycnf"]

    ## stores the tag content
    # \param name the tag name    
    def store(self,name):
        self.beforeLast().source.dsn= ("".join(self.content)).strip()        

 
## dimensions tag element        
class EDimensions(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "rank" in attrs.keys():
            self.last.rank=attrs["rank"]
            print "setting rank to ", self.last.rank

## dim tag element        
class EDim(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if ("index"  in attrs.keys()) and  ("value"  in attrs.keys()) :
            self.beforeLast().lengths[attrs["index"]]=attrs["value"]
            print "setting dim %s to %s " % (attrs["index"], attrs["value"])


