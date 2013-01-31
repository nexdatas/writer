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
            


    ## creates shape object from rank and lengths variables
    # \returns shape of the object
    def _findShape(self, rank, lengths=None, extraD = False, grows = None):
        shape = []
        if extraD:
            if grows and grows >1:
                exDim = grows  
            else:
                exDim = 1
        else:
            exDim = 0
                    
#            shape.append(0)
        if  int(rank) > 0:
            try:
                for i in range(int(rank)):
                    si = str(i+1)
                    if si in lengths.keys() and lengths[si] is not None:
                        if int(lengths[si]) > 0:
                            shape.append(int(self.lengths[si]))
                    else:
                        raise XMLSettingSyntaxError, "Dimensions not defined"
                if extraD:
                    shape.insert(exDim-1,0)    
            except:
                val = ("".join(self.content)).strip().encode()   
                if self.source and self.source.isValid():
#                    try:
                    dh = DataHolder(**self.source.getData())
                    dsShape = dh.shape
#                    except:
#                        raise DataSourceError, "Problem with fetching the data shape"
                    shape = []
                    if dsShape:    
                        for s in dsShape:
                            if s:
                                shape.append(s)
                    if extraD:
                        if shape == [1]:
                            shape = [0]
                        else:    
                            shape.insert(exDim-1,0)    
                elif val:
                    if not rank or int(rank) == 0:
                        shape = [1]
                    elif  int(rank) == 1:
                        spec = val.split()
                        shape = [len(spec)]
                    elif int(rank) == 2:
                        lines = val.split("\n")
                        image = [ln.split() for ln in lines ]
                        shape = [len(image),len(image[0])]
                else:
                    raise XMLSettingSyntaxError, "Wrongly defined shape"
                
        
        elif extraD:            
            shape = [0]
        return shape


    ## creates the error message
    # \param exceptionMessage additional message of exception
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


## NeXuS runnable tag element with attributes
# tag element corresponding to one of H5 objects with attributes
class FElementWithAttr(FElement):
    
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    # \param h5object H5 file object
    def __init__(self, name, attrs, last, h5object=None):
        FElement.__init__(self, name, attrs, last, h5object)
        ## dictionary with attribures from sepatare attribute tags
        self.tagAttributes = {}
        self.__h5Instances = {}
  

    ## creates h5 attributes
    # \brief It creates attributes instances which have been stored in tagAttributes dictionary
    def _createAttributes(self):
        for key in self.tagAttributes.keys():
            if key not in ["name","type"]:
                if len(self.tagAttributes[key]) < 3:
                    self.__h5Instances[key.encode()] = self.h5Object.attr(
                        key.encode(), NTP.nTnp[self.tagAttributes[key][0]].encode())
                    dh = DataHolder(
                        "SCALAR", self.tagAttributes[key][1].strip().encode(), "DevString", [1,0])
                    self.__h5Instances[key.encode()].value = dh.cast(self.__h5Instances[key.encode()].dtype)
#                    print "ATTR",key ,self.__h5Instances[key.encode()].dtype, dh.cast(self.__h5Instances[key.encode()].dtype)    
                else:
                    shape = self.tagAttributes[key][2]
                    self.__h5Instances[key.encode()] = self.h5Object.attr(
                        key.encode(), NTP.nTnp[self.tagAttributes[key][0]].encode(), 
                        shape)
                    val = self.tagAttributes[key][1].strip().encode()
#                    print "ATTR MD",key, shape ,self.__h5Instances[key.encode()].dtype, True if val else False , val
                    if val:
                        rank = len(shape)
                        if not rank or rank == 0:
                            dh = DataHolder("SCALAR", val, "DevString", [1,0])
                        elif  rank == 1:
                            spec = val.split()
                            dh = DataHolder("SPECTRUM", spec, "DevString", [len(spec),0])
                        elif  rank == 2:
                            lines = val.split("\n")
                            image = [ln.split() for ln in lines ]
                            dh = DataHolder("IMAGE", image, "DevString", [len(image),len(image[0])])
    
                        self.__h5Instances[key.encode()].value = dh.cast(self.__h5Instances[key.encode()].dtype)
                    

    ## provides attribute h5 object
    # \param name attribute name
    # \returns instance of the attribute object if created            
    def h5Attribute(self, name):
        return self.__h5Instances.get(name)


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
        if "grows" in attrs.keys() and hasattr(self._last,"grows"):
            self._last.grows = int(attrs["grows"])
            if self._last.grows < 1:
                self._last.grows = 1
        if "compression" in attrs.keys() and hasattr(self._last,"compression"):
            self._last.compression = True if attrs["compression"].upper() == "TRUE" else False
            if self._last.compression:
                if "rate" in attrs.keys() and hasattr(self._last,"rate"):
                    self._last.rate = int(attrs["rate"])
                    if self._last.rate < 0:
                        self._last.rate = 0
                    if self._last.rate > 9:
                        self._last.rate = 9
                if "suffle" in attrs.keys() and hasattr(self._last,"suffle"):
                    self._last.shuffle = False if attrs["suffle"].upper() == "FALSE" else True
                
            


    ## stores the tag content
    # \param xml xml setting 
    def store(self, xml = None):
        self._last.postrun = ("".join(self.content)).strip()        


## field H5 tag element
class EField(FElementWithAttr):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        FElementWithAttr.__init__(self, name, attrs, last)
        ## rank of the field
        self.rank = "0"
        ## shape of the field
        self.lengths = {}
        ## if field is stored in STEP mode
        self.__extraD = False
        ## if field array is splitted into columns
        self.__splitArray = False
        ## strategy, i.e. INIT, STEP, FINAL, POSTRUN
        self.strategy = None
        ## trigger for asynchronous writing
        self.trigger = None
        ## growing dimension
        self.grows = None
        ## label for postprocessing data
        self.postrun = ""
        ## compression flag
        self.compression = False
        ## compression rate
        self.rate = 5
        ## compression shuffle
        self.shuffle = True




    ## stores the tag content
    # \param xml xml setting 
    # \returns (strategy, trigger)
    def store(self, xml = None):
        
        # if growing in extra dimension
        self.__extraD = False
        if self.source and self.source.isValid() and self.strategy == "STEP":
            self.__extraD = True
            if not self.grows:
                self.grows = 1

        #  type and name
        if "name" in self._tagAttrs.keys():
            nm = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys():
                tp = NTP.nTnp[self._tagAttrs["type"]]
            else:
                tp = "string"
        else:
            raise XMLSettingSyntaxError, " Field without a name"

        # shape and chunk
        try:
            shape = self._findShape(self.rank, self.lengths, self.__extraD, self.grows)
            if len(shape) > 1 and tp.encode() == "string":
                self.__splitArray = True
                shape = self._findShape(self.rank, self.lengths, self.__extraD)
                self.grows = 1
        except XMLSettingSyntaxError, ex:
            if self.strategy == "POSTRUN": 
                self.__splitArray = False
                if self.rank and int(self.rank) >=0:
                    shape = [0 for d in range(int(self.rank))]
                else:
                    shape = [0]
            else:
                raise
            
            
        chunk = [s if s > 0 else 1 for s in shape]  

        deflate = None
        # create Filter
        if self.compression:
            deflate = nx.NXDeflateFilter()
            deflate.rate = self.rate
            deflate.shuffle = self.shuffle
            
        # create h5 object
        if shape:
            if self.__splitArray:
                f = FieldArray(self._lastObject(), nm.encode(), tp.encode(), shape)
            else:
                if not chunk:
                    f = self._lastObject().create_field(nm.encode(), tp.encode(), shape, filter=deflate)
                else:
                    f = self._lastObject().create_field(nm.encode(), tp.encode(), shape, chunk, filter=deflate)
        else:
            f = self._lastObject().create_field(nm.encode(), tp.encode(), filter=deflate)

        self.h5Object = f
        # create attributes
        for key in self._tagAttrs.keys():
            if key not in ["name"]:
                (self.h5Object.attr(key.encode(), "string")).value = self._tagAttrs[key].strip().encode()

        self._createAttributes()        
                
        if self.strategy == "POSTRUN":
            self.h5Object.attr("postrun".encode(), "string".encode()).value = self.postrun.encode()

            

        # return strategy or fill the value in
        if self.source:
            if  self.source.isValid() :
                return self.strategy, self.trigger
        else:
            val = ("".join(self.content)).strip().encode()   
            if val:
                if not self.rank or int(self.rank) == 0:
                    dh = DataHolder("SCALAR", val, "DevString", [1,0])
                elif  int(self.rank) == 1:
                    spec = val.split()
                    dh = DataHolder("SPECTRUM", spec, "DevString", [len(spec),0])
                elif  int(self.rank) == 2:
                    lines = val.split("\n")
                    image = [ln.split() for ln in lines ]
                    dh = DataHolder("IMAGE", image, "DevString", [len(image),len(image[0])])


                if self.h5Object.dtype != "string" or not self.rank or int(self.rank) == 0:
                    self.h5Object.write(dh.cast(self.h5Object.dtype))
                elif int(self.rank) == 1:
                    sts = dh.cast(self.h5Object.dtype)
                    for i in range(len(sts)):
                        self.h5Object[i] = sts[i] 
                elif int(self.rank) == 2:        
                    sts = dh.cast(self.h5Object.dtype)
                    for i in range(len(sts)):
                        for j in range(len(sts[i])):
                            self.h5Object[i,j] = sts[i][j] 

            elif self.strategy != "POSTRUN": 
#                raise ValueError,"Warning: Invalid datasource for %s" % nm
                print "Warning: Invalid datasource for ", nm


        

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        try:
            if self.source:
                dh = DataHolder(**self.source.getData())
                if not dh:
                    message = self.setMessage()
                    print message[0]
                    self.error = message
                else:
                    if not self.__extraD:
                        
#                        print "DATA3", self.h5Object.name, self.h5Object.dtype, len(self.h5Object.shape), self.__splitArray, dh.cast(self.h5Object.dtype)
                        if len(self.h5Object.shape) == 1 and self.h5Object.shape[0] >1 and self.h5Object.dtype == "string":
                            sts = dh.cast(self.h5Object.dtype)
                            for i in range(len(sts)):
                                self.h5Object[i] = sts[i] 
#                            self.h5Object[:] = dh.cast(self.h5Object.dtype)
                        elif len(self.h5Object.shape) == 1 and self.h5Object.shape[0] == 1 :
                            sts = dh.cast(self.h5Object.dtype)
                            if hasattr(sts, "__iter__")  and type(sts).__name__ != 'str':
                                self.h5Object.write(sts[0])
                            else:
                                self.h5Object.write(sts)
                                
#                            self.h5Object[:] = dh.cast(self.h5Object.dtype)

                        elif  len(self.h5Object.shape) == 2 and self.h5Object.dtype == "string":       
                            sts = dh.cast(self.h5Object.dtype)
                            if str(dh.format).split('.')[-1] == "IMAGE":
                                for i in range(len(sts)):
                                    for j in range(len(sts[i])):
                                        self.h5Object[i,j] = sts[i][j] 
                            elif str(dh.format).split('.')[-1] == "SPECTRUM":
                                for i in range(len(sts)):
                                        self.h5Object[i,:] = sts[i]
                            else:            
                                self.h5Object[:,:] = sts
                        else:
                            self.h5Object.write(dh.cast(self.h5Object.dtype))
#                        print "DATA4"
                    else:
                        if str(dh.format).split('.')[-1] == "SCALAR":
                            if len(self.h5Object.shape) == 1:
                                self.h5Object.grow()
                                self.h5Object[self.h5Object.shape[0]-1] = dh.cast(self.h5Object.dtype)
                            elif  len(self.h5Object.shape) == 2:
                                if self.grows == 2:
                                    self.h5Object.grow()
                                    self.h5Object[:,self.h5Object.shape[0]-1] = dh.cast(self.h5Object.dtype)
                                else:
                                    self.h5Object.grow()
                                    self.h5Object[self.h5Object.shape[0]-1,:] = dh.cast(self.h5Object.dtype)
                            elif  len(self.h5Object.shape) == 3:
                                if self.grows == 3:
                                    self.h5Object.grow()
                                    self.h5Object[:,:,self.h5Object.shape[0]-1] = dh.cast(self.h5Object.dtype)
                                if self.grows == 2:
                                    self.h5Object.grow()
                                    self.h5Object[:,self.h5Object.shape[0]-1,:] = dh.cast(self.h5Object.dtype)
                                else:
                                    self.h5Object.grow()
                                    self.h5Object[self.h5Object.shape[0]-1,:,:] = dh.cast(self.h5Object.dtype)

                        if str(dh.format).split('.')[-1] == "SPECTRUM":
                        # way around for a bug in pninx

                            arr = dh.cast(self.h5Object.dtype)
#                            print "arr", arr
                            if self.grows == 1:
                                if isinstance(arr, numpy.ndarray) \
                                        and len(arr.shape) == 1 and arr.shape[0] == 1:
                                    self.h5Object.grow()
                                    if len(self.h5Object.shape) == 2:
                                        self.h5Object[self.h5Object.shape[0]-1,:] = arr[0]
                                    else:                                
                                        self.h5Object[self.h5Object.shape[0]-1] = arr[0]
                                else:
                                    self.h5Object.grow()
                                    if len(self.h5Object.shape) == 3:
                                        self.h5Object[self.h5Object.shape[0]-1,:,:] = arr
                                    elif  len(self.h5Object.shape) == 2:
                                        self.h5Object[self.h5Object.shape[0]-1,:] = arr
                                    else:
                                        if hasattr(arr,"__iter__") and type(arr).__name__ != 'str' and len(arr) == 1:
                                            self.h5Object[self.h5Object.shape[0]-1] = arr[0]
                                        else:
                                            self.h5Object[self.h5Object.shape[0]-1] = arr
                                        
                            else:
                                if isinstance(arr, numpy.ndarray) \
                                        and len(arr.shape) == 1 and arr.shape[0] == 1:
                                    self.h5Object.grow(1)
                                    self.h5Object[:,self.h5Object.shape[1]-1] = arr[0]
                                else:
                                    if len(self.h5Object.shape) == 3: 
                                        if self.grows == 2:
                                            self.h5Object.grow(1)
                                            self.h5Object[:,self.h5Object.shape[1]-1,:] = arr
                                        else:
                                            self.h5Object.grow(2)
                                            self.h5Object[:,:,self.h5Object.shape[1]-1] = arr
                                    else:
                                        self.h5Object.grow(1)
                                        self.h5Object[:,self.h5Object.shape[1]-1] = arr

                        if str(dh.format).split('.')[-1] == "IMAGE":

                            if self.grows == 1:
                                self.h5Object.grow()
                                self.h5Object[self.h5Object.shape[0]-1,:,:] = dh.cast(self.h5Object.dtype)
                            elif self.grows == 2:
                                self.h5Object.grow(1)
                                self.h5Object[:,self.h5Object.shape[1]-1,:] = dh.cast(self.h5Object.dtype)
                            else:
                                self.h5Object.grow(2)
                                self.h5Object[:,:,self.h5Object.shape[2]-1] = dh.cast(self.h5Object.dtype)
        except:
            info = sys.exc_info()
            import traceback
            message = self.setMessage(str(info[1].__str__()) +"\n "+ (" ").join(traceback.format_tb(sys.exc_info()[2]) ))
#            message = self.setMessage(  sys.exc_info()[1].__str__()  )
            del info
            print message[0]
            print message[1]
            self.error = message
#            self.error = sys.exc_info()
        finally:
            pass


## group H5 tag element        
class EGroup(FElementWithAttr):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        FElementWithAttr.__init__(self, name, attrs, last)

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
    # \param xml xml setting 
    def store(self, xml = None):
        self._createAttributes()


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
                res = "/".join([res,sgr[0]])
            else:
                if sgr[0] in groupTypes.keys():
                    res = "/".join([res,groupTypes[sgr[0]]])
                else:
                    raise XMLSettingSyntaxError, "No "+ str(sgr[0])+ "in  groupTypes " 
        res = res + "/" + sp[-1]

        return res

        
    ## creates the link the H5 file
    # \param groupTypes dictionary with type:name group pairs
    def createLink(self, groupTypes):
        if ("name" in self._tagAttrs.keys()) and ("target" in self._tagAttrs.keys()):
            self.h5Object = (self._lastObject()).link((self.typesToNames(self._tagAttrs["target"], 
                                                                         groupTypes)).encode(),
                                                      self._tagAttrs["name"].encode())
        else:
            raise XMLSettingSyntaxError, "No name or type"
          
                


## attribute tag element        
class EAttribute(FElement):        
    ## constructor
    # \param name tag name
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, name, attrs, last):
        FElement.__init__(self, name, attrs, last)
        ## attribute name
        self.name = ""
        ## rank of the attribute
        self.rank = "0"
        ## shape of the attribute
        self.lengths = {}
        ## strategy, i.e. INIT, STEP, FINAL
        self.strategy = None
        ## trigger for asynchronous writting
        self.trigger = None


    ## stores the tag content
    # \param xml xml setting
    def store(self, xml = None):

        if "name" in self._tagAttrs.keys(): 
            self.name = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys() :
                tp = self._tagAttrs["type"]
            else:        
                tp = "NX_CHAR"
                
            shape = self._findShape(self.rank, self.lengths)
            val = ("".join(self.content)).strip().encode()   
            if not shape:
                self._last.tagAttributes[self.name] = (tp, val)
            else:
                self._last.tagAttributes[self.name] = (tp, val, tuple(shape))

            if self.source:
                if  self.source.isValid() :
                    return self.strategy, self.trigger


    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        try:
            if self.name:
                if not self.h5Object:
                    self.h5Object = self._last.h5Attribute(self.name)
                if self.source:
                    dh = DataHolder(**self.source.getData())

                    if not dh:
                        message = self.setMessage()
                        print message[0]
                        self.error = message
                    else:
                        arr = dh.cast(self.h5Object.dtype)
                        if self.h5Object.dtype != "string" or len(self.h5Object.shape) == 0:
                            self.h5Object.value = arr
                        else:
                            ## pninx does not support this case
#                            self.h5Object.value = numpy.array(arr,dtype = self.h5Object.dtype)
                            self.h5Object.value = arr
                            raise Exception("Storing multi-dimension string attributes not supported by pninx")
        except:
            message = self.setMessage( sys.exc_info()[1].__str__()  )
            print message[0]
            self.error = message
                                #            self.error = sys.exc_info()
            


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
    # \param xml xml setting
    # \param globalJSON global JSON string
    def store(self, xml, globalJSON = None):
        if self._beforeLast():
            self._beforeLast().doc +=  "".join(xml[1])            


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
    # \param xml xml setting
    def store(self, xml = None):
        if "name" in self._tagAttrs.keys():
            self.symbols[self._tagAttrs["name"]] = self._last.doc


 
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


