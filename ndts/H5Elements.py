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

import numpy 

#from DataSource import DataSource

from DataHolder import DataHolder

from Element import Element

from FieldArray import FieldArray

from Types import NTP

from Errors import (XMLSettingSyntaxError, DataSourceError )

import Streams

try:
    import pni.io.nx.h5 as nx
except:
    import pni.nx.h5 as nx


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
        ##  flag for devices for which is allowed to failed
        self.canfail = False

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        if self.source:
            self.source.getData()
            

    ## recalculates shape
    # \param dsShape origin shape of the object
    # \param rank rank of the object
    # \param extends If True extends the shape up to rank value
    # \param exDim grows growing dimension + 1        
    # \param extraD if the object grows
    # \returns shape of the  h5 field
    def __reshape(self, dsShape, rank, extends, extraD, exDim):        
        shape = []
        if dsShape:    
            for s in dsShape:
                if s and extends:
                    shape.append(s)
                elif not extends and s and s>1:
                    shape.append(s)
    
            while extends and len(shape) < int(rank):
                shape.append(1)
            if extraD:
                shape.insert(exDim-1,0)    
        return shape       


    ## fetches shape from value and rank
    # \param rank rank of the object
    # \param value of the object
    def __fetchShape(self, value, rank):
        if not rank or int(rank) == 0:
            return [1]
        elif  int(rank) == 1:
            spec = value.split()
            return [len(spec)]
        elif int(rank) == 2:
            lines = value.split("\n")
            image = [ln.split() for ln in lines ]
            return [len(image),len(image[0])]
        else:    
            if Streams.log_error:
                print >> Streams.log_error,\
                    "FElement::__fetchShape() - Case with not supported rank = %s" % rank

            raise XMLSettingSyntaxError, "Case with not supported rank = %s" % rank


    ## creates shape object from rank and lengths variables
    # \param rank rank of the object
    # \param lengths dictionary with dimensions as a string data , e.g. {"1":"34","2":"40"}
    # \param extraD if the object grows
    # \param grows growing dimension        
    # \param extends If True extends the shape up to rank value
    # \raise XMLSettingSyntaxError if shape cannot be found      
    # \returns shape of the object
    def _findShape(self, rank, lengths=None, extraD = False, grows = None, extends = False):
        shape = []
        if extraD:
            if grows and grows >1:
                exDim = grows  
            else:
                exDim = 1
        else:
            exDim = 0
                    
        if  int(rank) > 0:
            try:
                for i in range(int(rank)):
                    si = str(i+1)
                    if si in lengths.keys() and lengths[si] is not None:
                        if int(lengths[si]) > 0:
                            shape.append(int(lengths[si]))
                    else:
                        raise XMLSettingSyntaxError, "Dimensions not defined"
                if len(shape) < int(rank):
                    raise XMLSettingSyntaxError, "Too small dimension number"
                        
                if extraD:
                    shape.insert(exDim-1,0)    
            except:
                val = ("".join(self.content)).strip().encode()   
                found = False
                if self.source and self.source.isValid():
                    data = self.source.getData()

                    if isinstance(data, dict):                        
                        dh = DataHolder(**data)
                        shape = self.__reshape(dh.shape, rank, extends, extraD, exDim)
                        if shape is not None:
                            found = True
                if val and not found:
                    shape = self.__fetchShape(val,rank)
                    if shape is not None:
                        found = True
                    
                if not found:
                    nm = "unnamed"
                    if "name" in self._tagAttrs.keys():
                        nm = self._tagAttrs["name"] + " "
                    raise XMLSettingSyntaxError, "Wrongly defined %sshape: %s"% (nm, str(self.source) if self.source else val) 
                
                
        elif extraD:            
            shape = [0]

        return shape


    ## creates the error message
    # \param exceptionMessage additional message of exception
    def setMessage(self, exceptionMessage=None):
        if hasattr(self.h5Object, "path"):
            name = self.h5Object.path
        elif hasattr(self.h5Object, "name"):
            name = self.h5Object.name
        else:    
            name = "unnamed object"
        if self.source:
            dsource = str(self.source)
        else:
            dsource = "unknown datasource"
            
            
        message = ("Data for %s not found. DATASOURCE:%s" % (name, dsource), exceptionMessage )
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
                        else:    
                            if Streams.log_error:
                                print >> Streams.log_error,\
                                    "FElement::_createAttributes() - Case with not supported rank = %s", rank
                            raise XMLSettingSyntaxError, "Case with not supported rank = %s", rank
                            
                        self.__h5Instances[key.encode()].value = dh.cast(self.__h5Instances[key.encode()].dtype)
                    

    ## provides attribute h5 object
    # \param name attribute name
    # \returns instance of the attribute object if created            
    def h5Attribute(self, name):
        return self.__h5Instances.get(name)


## query tag element        
class EStrategy(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "strategy", attrs, last)

        if "mode" in attrs.keys():
            self._last.strategy = attrs["mode"]
        if "trigger" in attrs.keys():
            self._last.trigger = attrs["trigger"]
            if Streams.log_info:
                print >> Streams.log_info, "TRIGGER" , attrs["trigger"]
            print "TRIGGER" , attrs["trigger"]
        if "grows" in attrs.keys() and hasattr(self._last,"grows"):
            self._last.grows = int(attrs["grows"])
            if self._last.grows < 1:
                self._last.grows = 1
        if "canfail" in attrs.keys():
            self._last.canfail = True if attrs["canfail"].upper() == "TRUE" else False
        if "compression" in attrs.keys() and hasattr(self._last,"compression"):
            self._last.compression = True if attrs["compression"].upper() == "TRUE" else False
            if self._last.compression:
                if "rate" in attrs.keys() and hasattr(self._last,"rate"):
                    self._last.rate = int(attrs["rate"])
                    if self._last.rate < 0:
                        self._last.rate = 0
                    if self._last.rate > 9:
                        self._last.rate = 9
                if "shuffle" in attrs.keys() and hasattr(self._last,"shuffle"):
                    self._last.shuffle = False if attrs["shuffle"].upper() == "FALSE" else True
                
            


    ## stores the tag content
    # \param xml xml setting 
    def store(self, xml = None):
        self._last.postrun = ("".join(self.content)).strip()        


## field H5 tag element
class EField(FElementWithAttr):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElementWithAttr.__init__(self, "field", attrs, last)
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
        ## data format
        self.__format = ''

    ## checks if it is growing in extra dimension
    # \brief It checks if it is growing in extra dimension and setup internal variables     
    def __isgrowing(self):
        self.__extraD = False
        if self.source and self.source.isValid() and self.strategy == "STEP":
            self.__extraD = True
            if not self.grows:
                self.grows = 1
        else:
            self.grows = None

    ## provides type and name of the field
    # \returns (type, name) tuple        
    def __typeAndName(self):
        if "name" in self._tagAttrs.keys():
            nm = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys():
                tp = NTP.nTnp[self._tagAttrs["type"]]
            else:
                tp = "string"
            return tp, nm    
        else:
            if Streams.log_error:
                print >> Streams.log_error,\
                    "FElement::__typeAndName() - Field without a name"

            raise XMLSettingSyntaxError, "Field without a name"

    ## provides shape
    # \param tp object type    
    # \returns object shape    
    def __getShape(self, tp):
        try:
            if tp.encode() == "string":
                shape = self._findShape(self.rank, self.lengths, self.__extraD, self.grows)
            else:
                shape = self._findShape(self.rank, self.lengths, self.__extraD, self.grows, True)
#            print "ifstring", nm, shape, self.grows
            if self.grows > len(shape):
                self.grows = len(shape)

            if len(shape) > 1 and tp.encode() == "string":
                self.__splitArray = True
                shape = self._findShape(self.rank, self.lengths, self.__extraD)
                if self.__extraD:
                    self.grows = 1
                    
            return shape
        except XMLSettingSyntaxError, ex:
            if self.strategy == "POSTRUN": 
                self.__splitArray = False
                if self.rank and int(self.rank) >=0:
                    shape = [0 for d in range(int(self.rank))]
                else:
                    shape = [0]
                return shape
            else:
                if Streams.log_error:
                    print >> Streams.log_error,\
                        "FElement::__getShape() - Shape of %s cannot be found  " % self._tagAttrs["name"]
                raise XMLSettingSyntaxError, "Wrongly defined %sshape: %s"% (self._tagAttrs["name"] + " " , str(self.source)) 
            

    ## creates H5 object
    # \param tp object type    
    # \param nm object name
    # \param shape object shape    
    # \returns H5 object
    def __createObject(self, tp, nm, shape):
        chunk = [s if s > 0 else 1 for s in shape]  
        deflate = None
        # create Filter
        if self.compression:
            deflate = nx.NXDeflateFilter()
            deflate.rate = self.rate
            deflate.shuffle = self.shuffle
            
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

        return f
        

    ## creates attributes 
    # \brief It creates attributes in h5Object
    def __setAttributes(self):
        for key in self._tagAttrs.keys():
            if key not in ["name"]:
                if key in NTP.aTn.keys():
                    if hasattr(self._tagAttrs[key],"encode"):
                        try:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = \
                                self._tagAttrs[key].strip().encode()
                        except:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = \
                                NTP.convert[str(self.h5Object.attr(key.encode()).dtype)](self._tagAttrs[key].strip().encode())
                    else:
                        try:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = self._tagAttrs[key]
                        except:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = \
                                NTP.convert[str(self.h5Object.attr(key.encode()).dtype)](self._tagAttrs[key])
                            
                elif key in NTP.aTnv.keys():
                    shape = (len(self._tagAttrs[key]),)
                    (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTnv[key]].encode(),shape)).value = \
                        numpy.array(self._tagAttrs[key])
                else:
                    (self.h5Object.attr(key.encode(), "string")).value = self._tagAttrs[key].strip().encode()

        self._createAttributes()        
                
        if self.strategy == "POSTRUN":
            self.h5Object.attr("postrun".encode(), "string".encode()).value = self.postrun.encode().strip()




    ## provides strategy or fill the value in
    # \param nm object name
    # \returns strategy or strategy,trigger it trigger defined 
    def __setStrategy(self, nm):
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
                else:    
                    if Streams.log_error:
                        print >> Streams.log_error,\
                            "EField::__setStrategy() - Case with not supported rank = %s" % self.rank

                    raise XMLSettingSyntaxError, "Case with not supported rank = %s" % self.rank


                if self.h5Object.dtype != "string" or not self.rank or int(self.rank) == 0:
                    self.h5Object[...] = dh.cast(self.h5Object.dtype)
#                    self.h5Object.write(dh.cast(self.h5Object.dtype))
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
                if self.h5Object.dtype != "string": 
                    if Streams.log_error:
                        print >> Streams.log_error, "EField::__setStrategy() - Warning: Invalid datasource for %s" % nm
                    raise ValueError,"Warning: Invalid datasource for %s" % nm
                else:
                    print >> sys.stderr, "EField::__setStrategy() - Warning: Empty value for the field:", nm

            
    ## stores the tag content
    # \param xml xml setting 
    # \returns (strategy, trigger)
    def store(self, xml = None):
        
        # if it is growing in extra dimension
        self.__isgrowing()
        # type and name
        tp, nm = self.__typeAndName()
        # shape
        shape = self.__getShape(tp)
        # create h5 object
        self.h5Object = self.__createObject(tp, nm, shape)
        # create attributes
        self.__setAttributes()

        # return strategy or fill the value in
        return self.__setStrategy(nm)



    ## writes non-growing data
    # \param dh data holder
    def __writeData(self, dh):
        if len(self.h5Object.shape) == 1 and self.h5Object.shape[0] >1 and self.h5Object.dtype == "string":
            sts = dh.cast(self.h5Object.dtype)
            if len(dh.shape) > 1 and dh.shape[0] == 1:
                for i in range(len(sts[0])):
                    self.h5Object[i] = sts[0][i] 
            elif len(dh.shape) > 1 and dh.shape[1] == 1:
                for i in range(len(sts)):
                    self.h5Object[i] = sts[i][0] 
            else:
                for i in range(len(sts)):
                    self.h5Object[i] = sts[i] 
        elif len(self.h5Object.shape) == 1 and self.h5Object.shape[0] == 1 :
            sts = dh.cast(self.h5Object.dtype)
            if hasattr(sts, "__iter__")  and type(sts).__name__ != 'str':
                if self.h5Object.dtype == "string":
                    if hasattr(sts[0], "__iter__")  and type(sts[0]).__name__ != 'str':
                        self.h5Object.write(sts[0][0])
                    else:
                        self.h5Object.write(sts[0])
                else:
                    try:
                        self.h5Object.write(sts)
                    except:    
                        if Streams.log_error:
                            print >> Streams.log_error,\
                                "EField::__writedata() - Storing one-dimension single fields not supported by pniio"
                        raise Exception("Storing one-dimension single fields not supported by pniio")
            else:
                self.h5Object.write(sts)

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
        elif  len(self.h5Object.shape) == 3 and self.h5Object.dtype == "string":       
            sts = dh.cast(self.h5Object.dtype)
            if str(dh.format).split('.')[-1] == "VERTEX":
                for i in range(len(sts)):
                    for j in range(len(sts[i])):
                        for k in range(len(sts[i][j])):
                            self.h5Object[i,j,k] = sts[i][j][k] 
            if str(dh.format).split('.')[-1] == "IMAGE":
                for i in range(len(sts)):
                    for j in range(len(sts[i])):
                        self.h5Object[i,j,:] = sts[i][j] 
            elif str(dh.format).split('.')[-1] == "SPECTRUM":
                for i in range(len(sts)):
                        self.h5Object[i,:,:] = sts[i]
            else:            
                self.h5Object[:,:,:] = sts
        else:
            try:
                self.h5Object.write(dh.cast(self.h5Object.dtype))
            except:    
                if Streams.log_error:
                    print >> Streams.log_error,\
                        "EField::__writedata() - Storing two-dimension single fields not supported by pniio"
                raise Exception("Storing two-dimension single fields not supported by pniio")


    ## writes growing scalar data
    # \param dh data holder
    def __writeScalarGrowingData(self, dh):
            
        arr = dh.cast(self.h5Object.dtype)
        if len(self.h5Object.shape) == 1:
            self.h5Object[self.h5Object.shape[0]-1] = arr
        elif  len(self.h5Object.shape) == 2:
            if self.grows == 2:
                self.h5Object[:,self.h5Object.shape[0]-1] = arr
            else:
                self.h5Object[self.h5Object.shape[0]-1,:] = arr
        elif  len(self.h5Object.shape) == 3:
            if self.grows == 3:
                self.h5Object[:,:,self.h5Object.shape[0]-1] = arr
            if self.grows == 2:
                self.h5Object[:,self.h5Object.shape[0]-1,:] = arr
            else:
                self.h5Object[self.h5Object.shape[0]-1,:,:] = arr


    ## writes growing spectrum data
    # \param dh data holder
    def __writeSpectrumGrowingData(self, dh):

        # way around for a bug in pniio
        arr = dh.cast(self.h5Object.dtype)
        if self.grows == 1:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                if len(self.h5Object.shape) == 2 and self.h5Object.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0]-1,:] = arr
                if len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0]-1,:] = arr
                else:                      
                    self.h5Object[self.h5Object.shape[0]-1] = arr
            else:
                if len(self.h5Object.shape) == 3:
                    self.h5Object[self.h5Object.shape[0]-1,:,:] = arr
                elif  len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0]-1,:] = arr
                else:
                    if hasattr(arr,"__iter__") and type(arr).__name__!= 'str' and len(arr) == 1:
                        self.h5Object[self.h5Object.shape[0]-1] = arr[0]
                    else:
                        self.h5Object[self.h5Object.shape[0]-1] = arr

        else:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                self.h5Object[:,self.h5Object.shape[1]-1] = arr
            else:
                if len(self.h5Object.shape) == 3: 
                    if self.grows == 2:
                        self.h5Object[:,self.h5Object.shape[1]-1,:] = arr
                    else:
                        self.h5Object[:,:,self.h5Object.shape[2]-1] = arr
                else:
                    self.h5Object[:,self.h5Object.shape[1]-1] = arr


    ## writes growing spectrum data
    # \param dh data holder
    def __writeImageGrowingData(self, dh):

        arr = dh.cast(self.h5Object.dtype)
        if self.grows == 1:
            if len(self.h5Object.shape) == 3:
                self.h5Object[self.h5Object.shape[0]-1,:,:] = arr
            elif len(self.h5Object.shape) == 2:
                if len(dh.shape) == 1 :
                    self.h5Object[self.h5Object.shape[0]-1,:] = arr[0]
                elif len(dh.shape) > 1  and dh.shape[0] == 1:
                    self.h5Object[self.h5Object.shape[0]-1,:] = [c[0] for c in arr]
                elif len(dh.shape) > 1  and dh.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0]-1,:] = arr[:,0]
            elif len(self.h5Object.shape) == 2:
                self.h5Object[self.h5Object.shape[0]-1,:] = arr[0]
            elif len(self.h5Object.shape) == 1:
                self.h5Object[self.h5Object.shape[0]-1] = arr[0][0]
        elif self.grows == 2:
            if len(self.h5Object.shape) == 3:
                self.h5Object[:,self.h5Object.shape[1]-1,:] = arr
            elif len(self.h5Object.shape) == 2:
                self.h5Object[:,self.h5Object.shape[1]-1] = arr[0]
        else:
            self.h5Object[:,:,self.h5Object.shape[2]-1] = arr        



    ## writes growing data
    # \param dh data holder
    def __writeGrowingData(self, dh):
        if str(dh.format).split('.')[-1] == "SCALAR":
            self.__writeScalarGrowingData(dh)
        elif str(dh.format).split('.')[-1] == "SPECTRUM":
            self.__writeSpectrumGrowingData(dh)
        elif str(dh.format).split('.')[-1] == "IMAGE":
            self.__writeImageGrowingData(dh)
        else:
            if Streams.log_error:
                print >> Streams.log_error,\
                    "Case with %s format not supported " % str(dh.format).split('.')[-1] 
            raise XMLSettingSyntaxError, "Case with %s  format not supported " % str(dh.format).split('.')[-1]

    ## grows the h5 field    
    # \brief Ir runs the grow command of h5Object with grows-1 parameter
    def __grow(self):
        if self.grows and self.grows>0 and hasattr(self.h5Object,"grow"):
            self.h5Object.grow(self.grows-1)
                

    ## runner  
    # \brief During its thread run it fetches the data from the source  
    def run(self):
        try:
            if self.source:
                self.__grow()
                dt = self.source.getData()
                dh = None
                if dt:
                    dh = DataHolder(**dt)
                if not dh:
                    message = self.setMessage("Data without value")
                    self.error = message
                elif not hasattr(self.h5Object,'shape'):
                    message = self.setMessage("PNI Object not created")
                    self.error = message
                else:
                    if not self.__extraD:
                        self.__writeData(dh)
                    else:
                        self.__writeGrowingData(dh)
        except:
            info = sys.exc_info()
            import traceback
            message = self.setMessage(str(info[1].__str__()) +"\n "+ (" ").join(traceback.format_tb(sys.exc_info()[2]) ))
#            message = self.setMessage(  sys.exc_info()[1].__str__()  )
            del info
            print >> sys.stderr, "EField::run() - %s\n %s " % (message[0],message[1])
            self.error = message

#            self.error = sys.exc_info()
        finally:
            if self.error:
                if self.canfail:
                    if Streams.log_warn:
                        print >> Streams.log_warn, "EField::run() - %s  " % str(self.error)
                else:
                    if Streams.log_error:
                        print >> Streams.log_error, "EField::run() - %s  " % str(self.error)
                print >> sys.stderr, "EField::run() - ERROR", str(self.error)

#            pass

    ## fills object with maximum value            
    # \brief It fills object or an extend part of object by default value 
    def __fillMax(self):
        shape = list(self.h5Object.shape)
        nptype = self.h5Object.dtype
        value = ''

        if self.grows:
            shape.pop(self.grows-1)
            
        if nptype == "bool":
            value = False
        elif nptype != "string":
            try:
                value = numpy.iinfo(getattr(numpy, nptype)).max
            except:
                try:
                    value = numpy.finfo(getattr(numpy, nptype)).max
                except:    
                    value = 0
        else:
            nptype = "str"

            
        format = 'SCALAR'
        if shape and  len(shape) > 0  and shape[0] >= 1:
            arr = numpy.empty(shape, dtype=nptype)
            arr.fill(value)
            if len(shape) == 1:
                format = 'SPECTRUM'
            else:
                format = 'IMAGE'
        else:
            arr = value

        dh = DataHolder(format,arr,NTP.npTt[self.h5Object.dtype],shape)    
        
        
        if not self.__extraD:
            self.__writeData(dh)
        else:
            self.__writeGrowingData(dh)

            


    ## marks the field as failed
    # \brief It marks the field as failed            
    def markFailed(self):          
        if self.h5Object:
            self.h5Object.attr("nexdatas_canfail","string").value = "FAILED"
            if Streams.log_info:
                print >> Streams.log_info, "EField::markFailed() - %s marked as failed" % (self.h5Object.name) 
            self.__fillMax()
    
## group H5 tag element        
class EGroup(FElementWithAttr):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElementWithAttr.__init__(self, "group", attrs, last)

        if self._lastObject():
            if ("type" in attrs.keys()) and ("name" in attrs.keys()) :
                self.h5Object = self._lastObject().create_group(attrs["name"].encode(), attrs["type"].encode())
            elif "type" in attrs.keys() :
                self.h5Object = self._lastObject().create_group(attrs["type"][2:].encode(), attrs["type"].encode())
            else:
                if Streams.log_error:
                    print >> Streams.log_error,\
                        "EGroup::__init__() - The group type not defined"
                raise XMLSettingSyntaxError, "The group type not defined"
        else:
            if Streams.log_error:
                print >> Streams.log_error,\
                    "EGroup::__init__() - File object for the last element does not exist"
            raise XMLSettingSyntaxError, "File object for the last element does not exist"
            
        for key in attrs.keys() :
            if key not in ["name","type"]:
                if key in NTP.aTn.keys():
                    if hasattr(attrs[key],"encode"):
                        try:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = attrs[key].encode()
                        except:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = NTP.convert[str(self.h5Object.attr(key.encode()).dtype)](attrs[key].encode())
                            
                    else:
                        try:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = attrs[key]
                        except:
                            (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTn[key]].encode())).value = NTP.convert[str(self.h5Object.attr(key.encode()).dtype)](attrs[key])
                            
                elif key in NTP.aTnv.keys():
                    
                    shape = (len(attrs[key]),)
                    (self.h5Object.attr(key.encode(), NTP.nTnp[NTP.aTnv[key]].encode(),shape)).value = numpy.array(attrs[key])
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
            if Streams.log_error:
                print >> Streams.log_error,\
                    "EGroup::fetchName() - The group type attribute not defined"
            raise XMLSettingSyntaxError, "The group type attribute not defined"
        
        


## link H5 tag element        
class ELink(FElement):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElement.__init__(self, "link", attrs, last)
        self.h5Object = None

    ## converts types to Names using groupTypes dictionary
    # \param text original directory     
    # \param groupTypes dictionary with type:name group pairs
    # \returns directory defined by group namesS    
    def __typesToNames(self, text, groupTypes):
        sp = text.split("/")
        res = ""
        for gr in sp[:-1]:
            if len(gr) > 0: 
                sgr = gr.split(":")
                if len(sgr)>1 :
                    res = "/".join([res,sgr[0]])
                else:
                    if sgr[0] in groupTypes.keys():
                        res = "/".join([res,groupTypes[sgr[0]]])
                    elif sgr[0] in groupTypes.values():    
                        res = "/".join([res,sgr[0]])
                    else:
                        if Streams.log_error:
                            print >> Streams.log_error,\
                                "ELink::__typesToNames() - No %s in  groupTypes " %  str(sgr[0])
                        raise XMLSettingSyntaxError, "No "+ str(sgr[0])+ "in  groupTypes " 
        res = res + "/" + sp[-1]
                
        return res

        
    ## creates the link the H5 file
    # \param groupTypes dictionary with type:name group pairs
    def createLink(self, groupTypes):
        if ("name" in self._tagAttrs.keys()) and ("target" in self._tagAttrs.keys()):
            self.h5Object = (self._lastObject()).link(
                (self.__typesToNames(self._tagAttrs["target"], groupTypes)).encode(),
                self._tagAttrs["name"].encode())
        else:
            if Streams.log_error:
                print >> Streams.log_error,\
                    "ELink::createLink() - No name or type"
            raise XMLSettingSyntaxError, "No name or type"
          
                


## attribute tag element        
class EAttribute(FElement):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElement.__init__(self, "attribute", attrs, last)
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
                
            if tp == "NX_CHAR":    
                shape = self._findShape(self.rank, self.lengths)
            else:
                shape = self._findShape(self.rank, self.lengths, extends= True)
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
                    dt = self.source.getData()
                    dh = None
#                    print "dt", dt, self.h5Object.shape
                    if dt:
                        dh = DataHolder(**dt)
#                        print "VAL", dh.value, type(dh.value)
                    if not dh:
                        message = self.setMessage("Data without value")
                    #                    message = self.setMessage()
                        self.error = message
                    elif not hasattr(self.h5Object,'shape'):
                        message = self.setMessage("PNI Object not created")
                        print >> sys.stderr , "Group::run() - %s " % message[0]
                        self.error = message
                    else:
#                        print "ARR",self.name
                        arr = dh.cast(self.h5Object.dtype)
#                        print "ARR2",arr
                        
                        if self.h5Object.dtype != "string" or len(self.h5Object.shape) == 0:
                            if self.h5Object.dtype == "string" and len(dh.shape)>0 and dh.shape[0] ==1 and type(arr).__name__ != "str":
                                self.h5Object.value = arr[0]
                            else:
                                self.h5Object.value = arr
        
                        else:
                            ## pniio does not support this case
#                                print "ARR", arr
                            self.h5Object.value = arr
#                                self.h5Object.value = numpy.array(arr,dtype = self.h5Object.dtype)
                            if Streams.log_error:
                                print >> Streams.log_error,\
                                    "EAttribute::run() - Storing multi-dimension string attributes not supported by pniio"
                            raise Exception("Storing multi-dimension string attributes not supported by pniio")
        except:
            message = self.setMessage( sys.exc_info()[1].__str__()  )
            print >> sys.stderr , "Group::run() - %s " % message[0]
            self.error = message
                                #            self.error = sys.exc_info()
        finally:
            if self.error:
                if self.canfail:
                    if Streams.log_warn:
                        print >> Streams.log_warn, "Group::run() - %s  " % str(self.error)
                else:
                    if Streams.log_error:
                        print >> Streams.log_error, "Group::run() - %s  " % str(self.error)
                print >> sys.stderr, "Group::run() - ERROR", str(self.error)


    ## fills object with maximum value            
    # \brief It fills object or an extend part of object by default value 
    def __fillMax(self):
        if self.name and not self.h5Object:
            self.h5Object = self._last.h5Attribute(self.name)
        shape = list(self.h5Object.shape)
        
        nptype = self.h5Object.dtype
        value = ''

        if nptype != "string":
            try:
                value = numpy.iinfo(getattr(numpy, nptype)).max
            except:
                try:
                    value = numpy.finfo(getattr(numpy, nptype)).max
                except:    
                    value = 0
        else:
            nptype = "str"

        if shape and  len(shape) > 0:
            arr = numpy.empty(shape, dtype=nptype)
            arr.fill(value)
        else:
            arr = value


        self.h5Object.value = arr
        
            
            

    ## marks the field as failed
    # \brief It marks the field as failed            
    def markFailed(self):          
        field = self._lastObject()
        if field:
            field.attr("nexdatas_canfail","string").value = "FAILED"
            if Streams.log_info:
                print >> Streams.log_info, "EAttribute::markFailed() - %s of %s marked as failed" % (self.h5Object.name, field.name)
                print >> Streams.log_info, "EAttribute::markFailed() - marked as failed  "
            self.__fillMax()    

## file H5 element        
class EFile(FElement):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    # \param h5fileObject H5 file object
    def __init__(self, attrs, last, h5fileObject):
        FElement.__init__(self, "file", attrs, last, h5fileObject)



## doc tag element        
class EDoc(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "doc", attrs, last)

    ## stores the tag content
    # \param xml xml setting
    # \param globalJSON global JSON string
    def store(self, xml, globalJSON = None):
        if self._beforeLast():
            self._beforeLast().doc +=  "".join(xml[1])            


## symbol tag element        
class ESymbol(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "symbol", attrs, last)
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
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "dimensions", attrs, last)
        if "rank" in attrs.keys():
            self._last.rank = attrs["rank"]


## dim tag element        
class EDim(Element):        
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "dim", attrs, last)
        if ("index"  in attrs.keys()) and  ("value"  in attrs.keys()) :
            self._beforeLast().lengths[attrs["index"]] = attrs["value"]


