#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxswriter nexdatas
## \file FElement.py
# NeXus runnable elements

""" Definitions of file tag evaluation classes """

from __future__ import print_function

from .DataHolder import DataHolder
from .Element import Element
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)
from . import Streams


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
        ## scalar type
        self._scalar =  False

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
    @classmethod
    def _reshape(cls, dsShape, rank, extends, extraD, exDim):
        shape = []
        if dsShape:
            for s in dsShape:
                if s and extends:
                    shape.append(s)
                elif not extends and s and s > 0:
                    shape.append(s)

            while extends and len(shape) < int(rank):
                shape.append(0)
            if extraD:
                shape.insert(exDim - 1, 0)
        return shape

    ## fetches shape from value and rank
    # \param rank rank of the object
    # \param value of the object
    @classmethod
    def __fetchShape(cls, value, rank):
        if not rank or int(rank) == 0:
            return [1]
        elif int(rank) == 1:
            spec = value.split()
            return [len(spec)]
        elif int(rank) == 2:
            lines = value.split("\n")
            image = [ln.split() for ln in lines]
            return [len(image), len(image[0])]
        else:
            if Streams.log_error:
                print("FElement::__fetchShape() "
                      "- Case with not supported rank = %s" % rank,
                      file=Streams.log_error)

            raise XMLSettingSyntaxError(
                "Case with not supported rank = %s" % rank)

    # provides growing dimension
    # \param grows growing dimension
    # \param extraD if the object grows
    # \returns growing dimension
    @classmethod
    def _getExtra(cls, grows, extraD=False):
        if extraD:
            if grows and grows > 1:
                exDim = grows
            else:
                exDim = 1
        else:
            exDim = 0
        return exDim

    ## creates shape object from rank and lengths variables
    # \param rank rank of the object
    # \param lengths dictionary with dimensions as a string data ,
    #    e.g. {"1":"34","2":"40"}
    # \param extraD if the object grows
    # \param grows growing dimension
    # \param extends If True extends the shape up to rank value
    # \raise XMLSettingSyntaxError if shape cannot be found
    # \returns shape of the object
    def _findShape(self, rank, lengths=None, extraD=False,
                   grows=None, extends=False, checkData=False):
        self._scalar =  False
        shape = []
        exDim = self._getExtra(grows, extraD)
        if int(rank) > 0:
            try:
                for i in range(int(rank)):
                    si = str(i + 1)
                    if lengths and si in lengths.keys() \
                            and lengths[si] is not None:
                        if int(lengths[si]) > 0:
                            shape.append(int(lengths[si]))
                    else:
                        raise XMLSettingSyntaxError("Dimensions not defined")
                if len(shape) < int(rank):
                    raise XMLSettingSyntaxError("Too small dimension number")

                if extraD:
                    shape.insert(exDim - 1, 0)
            except:
                val = ("".join(self.content)).strip().encode()
                found = False
                if checkData and self.source and self.source.isValid():
                    data = self.source.getData()
                    if isinstance(data, dict):
                        dh = DataHolder(**data)
                        shape = self._reshape(dh.shape, rank, extends,
                                              extraD, exDim)
                        if shape is not None:
                            found = True

                if val and not found:
                    shape = self.__fetchShape(val, rank)
                    if shape is not None:
                        found = True

                if not found:
                    nm = "unnamed"
                    if "name" in self._tagAttrs.keys():
                        nm = self._tagAttrs["name"] + " "
                    raise XMLSettingSyntaxError(
                        "Wrongly defined %s shape: %s" %
                        (nm, str(self.source) if self.source else val))

        elif extraD:
            shape = [0]

        ## ?? probably wrong    
        if shape == []:
            shape = [1]
            self._scalar =  True
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

        message = ("Data for %s not found. DATASOURCE:%s"
                   % (name, dsource), exceptionMessage)
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

    ## creates DataHolder with given rank and value
    # \param rank data rank
    # \param val data value
    # \returns data holder
    @classmethod
    def _setValue(cls, rank, val):
        dh = None
        if not rank or rank == 0:
            dh = DataHolder("SCALAR", val, "DevString", [1, 0])
        elif rank == 1:
            spec = val.split()
            dh = DataHolder("SPECTRUM", spec, "DevString",
                            [len(spec), 0])
        elif rank == 2:
            lines = val.split("\n")
            image = [ln.split() for ln in lines]
            dh = DataHolder("IMAGE", image, "DevString",
                            [len(image), len(image[0])])
        else:
            if Streams.log_error:
                print("FElement::_createAttributes() - "
                      "Case with not supported rank = %s" % rank,
                      file=Streams.log_error)

            raise XMLSettingSyntaxError(
                "Case with not supported rank = %s", rank)
        return dh

    ## creates h5 attributes
    # \brief It creates attributes instances which have been
    #   stored in tagAttributes dictionary
    def _createAttributes(self):
        for key in self.tagAttributes.keys():
            if key not in ["name", "type"]:
                if len(self.tagAttributes[key]) < 3:
                    if key.encode() not in self.__h5Instances:
                        self.__h5Instances[key.encode()] \
                            = self.h5Object.attributes.create(
                                key.encode(),
                                NTP.nTnp[self.tagAttributes[key][0]].encode())
                    dh = DataHolder(
                        "SCALAR", self.tagAttributes[key][1].strip().encode(),
                        "DevString", [1, 0])
                    self.__h5Instances[key.encode()].value = \
                        dh.cast(self.__h5Instances[key.encode()].dtype)
                else:
                    shape = self.tagAttributes[key][2]
                    if key.encode() not in self.__h5Instances:
                        self.__h5Instances[key.encode()] \
                            = self.h5Object.attributes.create(
                                key.encode(),
                                NTP.nTnp[self.tagAttributes[key][0]].encode(),
                                shape)
                    val = self.tagAttributes[key][1].strip().encode()
                    if val:
                        rank = len(shape)
                        dh = self._setValue(rank, val)
                        self.__h5Instances[key.encode()].value = \
                            dh.cast(self.__h5Instances[key.encode()].dtype)

    ## provides attribute h5 object
    # \param name attribute name
    # \returns instance of the attribute object if created
    def h5Attribute(self, name):
        return self.__h5Instances.get(name)
