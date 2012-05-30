#!/usr/bin/env python
"""@package docstring
@file H5Elements.py
"""
                                                                      
import pni.nx.h5 as nx

from numpy  import * 

from DataSource import *


from Element import *


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

        if ("type" in attrs.keys()) and ("name" in attrs.keys()):
            print attrs["name"],    mt[attrs["type"]]
            f=self.lastObject().create_field(attrs["name"].encode(),mt[attrs["type"]].encode())
        elif "name" in attrs.keys():
            f=self.lastObject().create_field(attrs["name"].encode(),"string".encode())
        else:
            print "No name !!!"
            for key in attrs.keys():
                if key not in ["name"]:
                    (f.attr(key.encode(),"string")).value=attrs[key].encode()
        self.fObject=f

    def store(self,name):
        print "Storing field"
        if self.source :
            if  self.source.isValid() :
                return self.source.strategy
        else:
            print "invalid dataSource"



        
class EGroup(FElement):        
    def __init__(self,name,attrs,last):
        FElement.__init__(self,name,attrs,last)

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
          
                


class EAttribute(FElement):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)

        if "name" in attrs.keys():
            nm= attrs["name"]
            if "type" in attrs.keys():
                tp=attrs["type"]
            else:
                tp="NX_CHAR"
            at=self.lastObject().attr(nm.encode(),mt[tp].encode())
            self.fObject=at

    def store(self,name):
        print "Storing Attributes:", "".join(self.content)
        if "name" in self.tAttrs.keys(): 
            if  self.tAttrs["name"] == "URL":
                self.fObject.value=("".join(self.content)).encode()
            elif "type" in self.tAttrs.keys() and   "type" in self.tAttrs.keys():
                if self.tAttrs["type"]== "NX_CHAR":
                    self.fObject.value=("".join(self.content)).encode()
            else:        
                self.fObject.value=("".join(self.content)).encode()





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
            self.last.type=attrs["type"]
        if "name" in attrs.keys():
            self.last.name=attrs["name"]

class EDimensions(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if "rank" in attrs.keys():
            self.last.rank=attrs["rank"]


class EDim(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)
        if ("index"  in attrs.keys()) and  ("value"  in attrs.keys()) :
            self.beforeLast().lengths[attrs["index"]]=attrs["value"]

class ERecord(Element):        
    def __init__(self,name,attrs,last):
        Element.__init__(self,name,attrs,last)

