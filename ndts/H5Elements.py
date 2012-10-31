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
## \package ndts nexdatas
## \file H5Elements.py
# NeXus runnable elements

import sys                                                                       
import pni.nx.h5 as nx

import numpy 

#from DataSource import DataSource

from DataHolder import DataHolder

from Element import Element

from FieldArray import FieldArray

from Types import NTP


## exception for syntax in XML settings
class XMLSettingSyntaxError(Exception): pass

## exception for fetching data from data source
class DataSourceError(Exception): pass




## NeXuS runnable tag element
# tag element corresponding to one of H5 objects 
class FElement(Element):
    
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    # \param h5object H5 file object
    def __init__(self, name, attrs, last, h5object=None):
        Element.__init__(self, name, attrs, last)
        ## stored H5 file object 
        self.h5Object = h5object
        ## data source    
        self.source = None
        ## notification of error in the run method
        self.error = None

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        if self.source:
            self.source.getData()
            


## query tag element        
class EStrategy(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)

        if "mode" in attrs.keys():
            self._last.strategy = attrs["mode"]
        if "trigger" in attrs.keys():
            self._last.trigger = attrs["trigger"]
            print "TRIGGER" , attrs["trigger"]


    ## stores the tag content
    # \param name the tag name    
    def store(self, name):
        self._last.postrun = ("".join(self.content)).strip()        


## field H5 tag element
class EField(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        FElement.__init__(self, name, attrs, last)
        ## rank of the field
        self.rank = "0"
        ## shape of the field
        self.lengths = {}
        ## dictionary with attribures from sepatare attribute tags
        self.tagAttributes = {}
        ## if field is stored in STEP mode
        self._extraD = False
        ## if field array is splitted into columns
        self._splitArray = False
        ## strategy, i.e. INIT, STEP, FINAL, POSTRUN
        self.strategy = None
        ## trigger for asynchronous writting
        self.trigger = None
        ## label for postprocessing data
        self.postrun = ""

    ## stores the tag content
    # \param name the tag name    
    def store(self, name):
            

        self._extraD = False
        if self.source and self.source.isValid() and self.strategy == "STEP":
            self._extraD = True
            

        if "name" in self._tagAttrs.keys():
            nm = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys():
                tp = NTP.nTnp[self._tagAttrs["type"]]
            else:
                tp = "string"
        else:
            raise XMLSettingSyntaxError, " Field without a name"


        shape = []
        if self._extraD:
            shape.append(0)
        if  int(self.rank) > 0:
            try:
                for i in range(int(self.rank)):
                    si = str(i+1)
                    if si in self.lengths.keys():
                        if int(self.lengths[si]) > 0:
                            shape.append(int(self.lengths[si]))
                    else:
                        raise XMLSettingSyntaxError, "Dimensions not defined"
            except:
                if self.source and self.source.isValid():
#                    try:
                    dsShape = self.source.getData().shape                    
#                    except:
#                        raise DataSourceError, "Problem with fetching the data shape"
                    shape = []
                    if self._extraD:
                        shape.append(0)
                    if dsShape:    
                        for s in dsShape:
                            if s:
                                shape.append(s)
                    else:
                        raise XMLSettingSyntaxError, "Wrongly defined shape"


        if len(shape) > 1 and tp.encode() == "string":
            self._splitArray = True
          

        if shape:
            if self._splitArray:
                f = FieldArray(self._lastObject(), nm.encode(), tp.encode(), shape)
            else:
                f = self._lastObject().create_field(nm.encode(), tp.encode(), shape)
        else:
            f = self._lastObject().create_field(nm.encode(), tp.encode())


        for key in self._tagAttrs.keys():
            if key not in ["name"]:
                (f.attr(key.encode(), "string")).value = self._tagAttrs[key].strip().encode()

        for key in self.tagAttributes.keys():
            if key not in ["name"]:
                (f.attr(key.encode(), NTP.nTnp[self.tagAttributes[key][0]].encode())).value \
                    = self.tagAttributes[key][1].strip().encode()

        if self.strategy == "POSTRUN":
            f.attr("postrun".encode(), "string".encode()).value = self.postrun.encode()


        self.h5Object = f

        if self.source:
            if  self.source.isValid() :
                return self.strategy, self.trigger
        else:
            val = ("".join(self.content)).strip().encode()   
            if val:
                dh = DataHolder("SCALAR", val, "DevString", [1,0])
                self.h5Object.write(dh.cast(self.h5Object.dtype))
            else:
#                raise ValueError,"Warning: Invalid datasource for %s" % nm
                print "Warning: Invalid datasource for ", nm

    ## creates the error message
    def setMessage(self, exceptionMessage=None):
        if hasattr(self.h5Object, "name"):
            name = self.h5Object.name
        else:
            name = "unnamed object"
        if self.source:
            dsource = str(self.source)
        else:
            dsource = "unknown datasource"
            
            
        message = ("WARNING: Data for %s on %s not found" % (name, dsource), exceptionMessage )
        return message
        

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        try:
            if self.source:
                dh = self.source.getData()
                if not dh:
                    message = self.setMessage()
                    print message[0]
                    self.error = message
                else:
                    if not self._extraD:
                        self.h5Object.write(dh.cast(self.h5Object.dtype))
                    else:

                        if str(dh.format).split('.')[-1] == "SCALAR":
                            self.h5Object.grow()
                            self.h5Object[self.h5Object.shape[0]-1] = dh.cast(self.h5Object.dtype)
                        if str(dh.format).split('.')[-1] == "SPECTRUM":

                        # way around for a bug in pninx

                            arr = dh.cast(self.h5Object.dtype)

                            if isinstance(arr, numpy.ndarray) \
                                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                                self.h5Object.grow()
                                self.h5Object[self.h5Object.shape[0]-1,:] = arr[0]
                            else:
                                self.h5Object.grow()
                                self.h5Object[self.h5Object.shape[0]-1,:] = arr

                                
                        if str(dh.format).split('.')[-1] == "IMAGE":
                            self.h5Object.grow()
                            self.h5Object[self.h5Object.shape[0]-1,:,:] = dh.cast(self.h5Object.dtype)
        except:
            message = self.setMessage( sys.exc_info()[1].__str__()  )
            print message[0]
            self.error = message
                                #            self.error = sys.exc_info()
            


## group H5 tag element        
class EGroup(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        FElement.__init__(self, name, attrs, last)

        ## dictionary with attribures from sepatare attribute tags
        self.tagAttributes = {}

        if self._lastObject():
            if ("type" in attrs.keys()) and ("name" in attrs.keys()) :
                self.h5Object = self._lastObject().create_group(attrs["name"].encode(), attrs["type"].encode())
            elif "type" in attrs.keys() :
                self.h5Object = self._lastObject().create_group(attrs["type"][2:].encode(), attrs["type"].encode())
            else:
                raise XMLSettingSyntaxError, "The group type not defined"
        else:
                raise XMLSettingSyntaxError, "File object for the last element does not exist"
            

        for key in attrs.keys() :
            if key not in ["name","type"]:
                if key in NTP.aTn.keys():
                    (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = attrs[key].encode()
                else:
                    (self.h5Object.attr(key.encode(), "string")).value = attrs[key].encode()

    ## stores the tag content
    # \param name the tag name    
    def store(self, name):
        for key in self.tagAttributes.keys() :
            if key not in ["name","type"]:
                (self.h5Object.attr(key.encode(), NTP.nTnp[self.tagAttributes[key][0]].encode())).value \
                    = self.tagAttributes[key][1].encode()


    ## fetches the type and the name of the current group            
    # \param groupTypes dictionary with the group type:name pairs            
    def fetchName(self, groupTypes):
        if ("type" in self._tagAttrs.keys()) and ("name" in self._tagAttrs.keys()):
            groupTypes[self._tagAttrs["type"]] = self._tagAttrs["name"]
        elif "type" in self._tagAttrs.keys():
            groupTypes[self._tagAttrs["type"]] = self._tagAttrs["type"][2:]
        else:
            raise XMLSettingSyntaxError, "The group type not defined"
        
        


## link H5 tag element        
class ELink(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        FElement.__init__(self, name, attrs, last)
        self.h5Object = None

    ## converts types to Names using groupTypes dictionary
    # \param text original directory     
    # \param groupTypes dictionary with type:name group pairs
    # \returns directory defined by group namesS    
    def typesToNames(self, text, groupTypes):
        sp = text.split("/")
        res = "/"
        for gr in sp[:-1]:
            sgr = gr.split(":")
            if len(sgr)>1 :
                res = "/".join([res,sgr[1]])
            else:
                if sgr[0] in groupTypes:
                    res = "/".join([res,groupTypes[sgr[0]]])
                else:
                    raise XMLSettingSyntaxError, "No "+ str(sgr[0])+ "in  groupTypes " 
        res = res + "/" + sp[-1]

        return res

        
    ## creates the link the H5 file
    # \param groupTypes dictionary with type:name group pairs
    def createLink(self, groupTypes):
        if ("name" in self._tagAttrs.keys()) and ("target" in self._tagAttrs.keys()):
            self.h5Object = (self._lastObject()).link((self.typesToNames(self._tagAttrs["target"], groupTypes)).encode(),
                                                      self._tagAttrs["name"].encode())
        else:
            raise XMLSettingSyntaxError, "No name or type"
          
                


## attribute tag element        
class EAttribute(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)


    ## stores the tag content
    # \param name the tag name    
    def store(self, name):

        if "name" in self._tagAttrs.keys(): 
            nm = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys() :
                tp = self._tagAttrs["type"]
            else:        
                tp = "NX_CHAR"
                
            self._last.tagAttributes[nm] = (tp, ("".join(self.content)).strip().encode())




## file H5 element        
class EFile(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    # \param h5fileObject H5 file object
    def __init__(self, name, attrs, last, h5fileObject):
        FElement.__init__(self, name, attrs, last, h5fileObject)



## doc tag element        
class EDoc(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)

    ## stores the tag content
    # \param name the tag name    
    def store(self, name):
        if self._beforeLast():
            self._beforeLast().doc = self._beforeLast().doc + "".join(self.content)            


## symbol tag element        
class ESymbol(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        ## dictionary with symbols
        self.symbols = {}

    ## stores the tag content
    # \param name the tag name    
    def store(self, name):
        if "name" in self._tagAttrs.keys():
            self.symbols[self._tagAttrs["name"]] = self._last.doc


## record tag element        
class ERecord(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        if "name" in attrs.keys():
            self._beforeLast().source.name = attrs["name"]


## device tag element        
class EDevice(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        if "name" in attrs.keys():
            self._beforeLast().source.device = attrs["name"]
        if "hostname" in attrs.keys():
            self._beforeLast().source.hostname = attrs["hostname"]
        if "port" in attrs.keys():
            self._beforeLast().source.port = attrs["port"]
        if "encoding" in attrs.keys():
            self._beforeLast().source.encoding = attrs["encoding"]
        if "member" in attrs.keys():
            self._beforeLast().source.memberType = attrs["member"]
        else:
            self._beforeLast().source.memberType = "attribute"

## door tag element        
class EDoor(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        if "name" in attrs.keys():
            self._beforeLast().source.door = attrs["name"]
        if "hostname" in attrs.keys():
            self._beforeLast().source.hostname = attrs["hostname"]
        if "port" in attrs.keys():
            self._beforeLast().source.port = attrs["port"]


## query tag element        
class EQuery(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        if "format" in attrs.keys():
            self._beforeLast().source.format = attrs["format"]

    ## stores the tag content
    # \param name the tag name    
    def store(self, name):
        self._beforeLast().source.query = ("".join(self.content)).strip()        


## Database tag element        
class EDatabase(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        if "dbname" in attrs.keys():
            self._beforeLast().source.dbname = attrs["dbname"]
        if "dbtype" in attrs.keys():
            self._beforeLast().source.dbtype = attrs["dbtype"]
        if "user" in attrs.keys():
            self._beforeLast().source.user = attrs["user"]
        if "passwd" in attrs.keys():
            self._beforeLast().source.passwd = attrs["passwd"]
        if "mode" in attrs.keys():
            self._beforeLast().source.mode = attrs["mode"]
        if "mycnf" in attrs.keys():
            self._beforeLast().source.mycnf = attrs["mycnf"]
        if "hostname" in attrs.keys():
            self._beforeLast().source.hostname = attrs["hostname"]
        if "port" in attrs.keys():
            self._beforeLast().source.port = attrs["port"]

    ## stores the tag content
    # \param name the tag name    
    def store(self, name):
        self._beforeLast().source.dsn = ("".join(self.content)).strip()        

 
## dimensions tag element        
class EDimensions(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        if "rank" in attrs.keys():
            self._last.rank = attrs["rank"]


## dim tag element        
class EDim(Element):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        Element.__init__(self, name, attrs, last)
        if ("index"  in attrs.keys()) and  ("value"  in attrs.keys()) :
            self._beforeLast().lengths[attrs["index"]] = attrs["value"]


