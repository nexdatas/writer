#!/usr/bin/env python3
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
## \file EField.py
# NeXus runnable elements

""" Definitions of field tag evaluation classes """

import sys

import numpy

from .DataHolder import DataHolder
from .FElement import FElementWithAttr
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)
from . import Streams

import pni.io.nx.h5 as nx


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
        ## grew flag
        self.__grew = True
        ## data format
        self.__format = ''

    ## checks if it is growing in extra dimension
    # \brief It checks if it is growing in extra dimension
    # and setup internal variables
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
            Streams.error(
                "FElement::__typeAndName() - Field without a name",
                std=False)

            raise XMLSettingSyntaxError("Field without a name")

    ## provides shape
    # \returns object shape
    def __getShape(self):
        try:
            shape = self._findShape(
                self.rank, self.lengths,
                self.__extraD, self.grows, True, checkData=True)
            if self.grows and self.grows > len(shape):
                self.grows = len(shape)
            return shape
        except XMLSettingSyntaxError:
            if self.rank and int(self.rank) >= 0:
                shape = [0] * (int(self.rank) + int(self.__extraD))
            else:
                shape = [0]
            return shape

    ## creates H5 object
    # \param dtype object type
    # \param name object name
    # \param shape object shape
    # \returns H5 object
    def __createObject(self, dtype, name, shape):
        chunk = [s if s > 0 else 1 for s in shape]
        minshape = [1 if s > 0 else 0 for s in shape]
        deflate = None
        # create Filter

        if self.compression:
            deflate = nx.deflate_filter()
            deflate.rate = self.rate
            deflate.shuffle = self.shuffle

        try:
            if shape:
                if not chunk:
                    f = self._lastObject().create_field(
                        name, dtype, shape, [],
                        deflate)
                elif self.canfail:
                    f = self._lastObject().create_field(
                        name, dtype, shape, chunk,
                        deflate)
                else:
                    f = self._lastObject().create_field(
                        name, dtype, minshape or [1], chunk,
                        deflate)
            else:
                mshape = [1] if self.strategy in ['INIT', 'FINAL'] else [0]
                if deflate:
                    f = self._lastObject().create_field(
                        name, dtype, mshape, [1], deflate)
                else:
                    f = self._lastObject().create_field(
                        name, dtype, mshape, [1])
        except:
            info = sys.exc_info()
            import traceback
            message = str(info[1].__str__()) + "\n " + (" ").join(
                traceback.format_tb(sys.exc_info()[2]))
            Streams.error(
                "EField::__createObject() - "
                "The field '%s' of '%s' type cannot be created: %s" %
                (name, dtype, message),
                std=False)

            raise XMLSettingSyntaxError(
                "The field '%s' of '%s' type cannot be created: %s" %
                (name, dtype, message))
        return f

    ## creates attributes
    # \brief It creates attributes in h5Object
    def __setAttributes(self):
        for key in self._tagAttrs.keys():
            if key not in ["name"]:
                if key in NTP.aTn.keys():
                    h5att = self.h5Object.attributes.create(
                        key,
                        NTP.nTnp[NTP.aTn[key]],
                        overwrite=True
                    )
                    if hasattr(self._tagAttrs[key], "encode"):
                        try:
                            h5att[...] = NTP.convert[
                                str(self.h5Object.attributes[
                                    key].dtype)
                            ](self._tagAttrs[key].strip())
                        except:
                            h5att[...] = self._tagAttrs[key].strip()
                    else:
                        try:
                            h5att[...] = NTP.convert[
                                str(self.h5Object.attributes[
                                    key].dtype)
                            ](self._tagAttrs[key])
                        except:
                            h5att[...] = self._tagAttrs[key]

                elif key in NTP.aTnv.keys():
                    shape = (len(self._tagAttrs[key]),)
                    self.h5Object.attributes.create(
                        key,
                        NTP.nTnp[NTP.aTnv[key]],
                        shape,
                        overwrite=True
                    )[...] = numpy.array(self._tagAttrs[key])
                else:
                    self.h5Object.attributes.create(
                        key, "string", overwrite=True)[...] \
                        = self._tagAttrs[key].strip()

        self._createAttributes()

        if self.strategy == "POSTRUN":
            self.h5Object.attributes.create(
                "postrun",
                "string", overwrite=True)[...] \
                = self.postrun.strip()

    ## provides strategy or fill the value in
    # \param name object name
    # \returns strategy or strategy,trigger it trigger defined
    def __setStrategy(self, name):
        if self.source:
            if self.source.isValid():
                return self.strategy, self.trigger
        else:
            val = ("".join(self.content)).strip()
            if val:
                dh = self._setValue(int(self.rank), val)
                self.__growshape(dh.shape)
                self.h5Object[...] = dh.cast(self.h5Object.dtype)
            elif self.strategy != "POSTRUN":
                if self.h5Object.dtype != "string":
                    Streams.error(
                        "EField::__setStrategy() - "
                        "Warning: Invalid datasource for %s" % name,
                        std=False)

                    raise ValueError(
                        "Warning: Invalid datasource for %s" % name)

    ## stores the tag content
    # \param xml xml setting
    # \param globalJSON global JSON string
    # \returns (strategy, trigger)
    def store(self, xml=None, globalJSON=None):

        # if it is growing in extra dimension
        self.__isgrowing()
        # type and name
        tp, nm = self.__typeAndName()
        # shape
        shape = self.__getShape()
        ## stored H5 file object (defined in base class)
        self.h5Object = self.__createObject(tp, nm, shape)
        # create attributes
        self.__setAttributes()

        # return strategy or fill the value in
        return self.__setStrategy(nm)

    ## writes non-growing data
    # \param holder data holder
    def __writeData(self, holder):
        try:
            self.h5Object[...] = holder.cast(self.h5Object.dtype)
        except Exception:
            Streams.error(
                "EField::__writedata() - "
                "Storing single fields "
                "not supported by pniio",
                std=False)

            raise Exception("Storing single fields"
                            " not supported by pniio")

    ## writes growing scalar data
    # \param holder data holder
    def __writeScalarGrowingData(self, holder):

        arr = holder.cast(self.h5Object.dtype)
        if len(self.h5Object.shape) == 1:
            self.h5Object[self.h5Object.shape[0] - 1] = arr
        elif len(self.h5Object.shape) == 2:
            if self.grows == 2:
                self.h5Object[0, self.h5Object.shape[0] - 1] = arr
            else:
                self.h5Object[self.h5Object.shape[0] - 1, 0] = arr
        elif len(self.h5Object.shape) == 3:
            if self.grows == 3:
                self.h5Object[0, 0, self.h5Object.shape[0] - 1] = arr
            if self.grows == 2:
                self.h5Object[0, self.h5Object.shape[0] - 1, 0] = arr
            else:
                self.h5Object[self.h5Object.shape[0] - 1, 0, 0] = arr

    ## writes growing spectrum data
    # \param holder data holder
    def __writeSpectrumGrowingData(self, holder):

        # way around for a bug in pniio
        arr = holder.cast(self.h5Object.dtype)
        if self.grows == 1:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                if len(self.h5Object.shape) == 2 \
                        and self.h5Object.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, 0:len(arr)] = arr
                if len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0] - 1, 0:len(arr)] = arr
                else:
                    self.h5Object[self.h5Object.shape[0] - 1] = arr
            else:
                if len(self.h5Object.shape) == 3:
                    self.h5Object[self.h5Object.shape[0] - 1, :, :] = arr
                elif len(self.h5Object.shape) == 2:
                    self.h5Object[self.h5Object.shape[0] - 1, 0:len(arr)] = arr
                elif hasattr(arr, "__iter__") and type(arr).__name__ != 'str' \
                        and len(arr) == 1:
                    self.h5Object[self.h5Object.shape[0] - 1] = arr
                else:
                    Streams.error("Rank mismatch", std=False)
                    raise XMLSettingSyntaxError("Rank mismatch")

        else:
            if isinstance(arr, numpy.ndarray) \
                    and len(arr.shape) == 1 and arr.shape[0] == 1:
                self.h5Object[0:len(arr), self.h5Object.shape[1] - 1] = arr
            else:
                if len(self.h5Object.shape) == 3:
                    if self.grows == 2:
                        self.h5Object[:, self.h5Object.shape[1] - 1, :] = arr
                    else:
                        self.h5Object[:, :, self.h5Object.shape[2] - 1] = arr
                else:
                    self.h5Object[0:len(arr), self.h5Object.shape[1] - 1] = arr

    ## writes growing spectrum data
    # \param holder data holder
    def __writeImageGrowingData(self, holder):

        arr = holder.cast(self.h5Object.dtype)
        if self.grows == 1:
            if len(self.h5Object.shape) == 3:
                self.h5Object[self.h5Object.shape[0] - 1,
                              0:len(arr), 0:len(arr[0])] = arr
            elif len(self.h5Object.shape) == 2:
                if len(holder.shape) == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, :] = arr[0]
                elif len(holder.shape) > 1 and holder.shape[0] == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, :] \
                        = [c[0] for c in arr]
                elif len(holder.shape) > 1 and holder.shape[1] == 1:
                    self.h5Object[self.h5Object.shape[0] - 1, :] = arr[:, 0]
            elif len(self.h5Object.shape) == 2:
                self.h5Object[self.h5Object.shape[0] - 1, :] = arr[0]
            elif len(self.h5Object.shape) == 1:
                self.h5Object[self.h5Object.shape[0] - 1] = arr[0][0]
            else:
                Streams.error("Rank mismatch", std=False)
                raise XMLSettingSyntaxError("Rank mismatch")

        elif self.grows == 2:
            if len(self.h5Object.shape) == 3:
                self.h5Object[0: len(arr), self.h5Object.shape[1] - 1,
                              0: len(arr[0])] = arr
            elif len(self.h5Object.shape) == 2:
                self.h5Object[0: len(arr[0]),
                              self.h5Object.shape[1] - 1] = arr[0]
            else:
                Streams.error("Rank mismatch", std=False)
                raise XMLSettingSyntaxError("Rank mismatch")
        else:
            self.h5Object[0: len(arr), 0: len(arr[0]),
                          self.h5Object.shape[2] - 1] = arr

    ## writes growing data
    # \param holder data holder
    def __writeGrowingData(self, holder):
        if str(holder.format).split('.')[-1] == "SCALAR":
            self.__writeScalarGrowingData(holder)
        elif str(holder.format).split('.')[-1] == "SPECTRUM":
            self.__writeSpectrumGrowingData(holder)
        elif str(holder.format).split('.')[-1] == "IMAGE":
            self.__writeImageGrowingData(holder)
        else:
            Streams.error(
                "Case with %s format not supported " %
                str(holder.format).split('.')[-1],
                std=False)

            raise XMLSettingSyntaxError(
                "Case with %s  format not supported " %
                str(holder.format).split('.')[-1])

    ## grows the h5 field
    # \brief Ir runs the grow command of h5Object with grows-1 parameter
    def __grow(self):
        if self.grows and self.grows > 0 and hasattr(self.h5Object, "grow"):
            shape = self.h5Object.shape
            if self.grows > len(shape):
                self.grows = len(shape)
            if not self.grows and self.__extraD:
                self.grows = 1

            self.h5Object.grow(self.grows - 1)

    ## reshapes h5 object
    # \param shape required shape
    def __growshape(self, shape):
        h5shape = self.h5Object.shape
        ln = len(shape)
        if ln > 0 and len(h5shape) > 0:
            j = 0
            for i in range(len(h5shape)):
                if not self.__extraD or (
                        self.grows - 1 != i and
                        not (i == 0 and self.grows == 0)):
                    if shape[j] - h5shape[i] > 0:
                        self.h5Object.grow(i, shape[j] - h5shape[i])
                    elif not h5shape[i]:
                        self.h5Object.grow(i, 1)

                    j += 1

    ## runner
    # \brief During its thread run it fetches the data from the source
    def run(self):
        self.__grew = False
        try:
            if self.source:
                dt = self.source.getData()
                dh = None
                if dt and isinstance(dt, dict):
                    dh = DataHolder(**dt)
                self.__grow()
                self.__grew = True
                if not dh:
                    message = self.setMessage("Data without value")
                    self.error = message
                elif not hasattr(self.h5Object, 'shape'):
                    message = self.setMessage("PNI Object not created")
                    self.error = message
                else:
                    if not self.__extraD:
                        self.__growshape(dh.shape)
                        self.__writeData(dh)
                    else:
                        if len(self.h5Object.shape) >= self.grows \
                           and (self.h5Object.shape[self.grows - 1] == 1
                                or self.canfail):
                            self.__growshape(dh.shape)
                        self.__writeGrowingData(dh)
        except:
            info = sys.exc_info()
            import traceback
            message = self.setMessage(
                str(info[1].__str__()) + "\n " + (" ").join(
                    traceback.format_tb(sys.exc_info()[2])))
#            message = self.setMessage(  sys.exc_info()[1].__str__()  )
            del info
            ##  notification of error in the run method
            #   (defined in base class)
            self.error = message

#            self.error = sys.exc_info()
        finally:
            if self.error:
                if self.canfail:
                    Streams.warn("EField::run() - %s  " % str(self.error))
                else:
                    Streams.error("EField::run() - %s  " % str(self.error))

    ## fills object with maximum value
    # \brief It fills object or an extend part of object by default value
    def __fillMax(self):
        shape = list(self.h5Object.shape)
        nptype = self.h5Object.dtype
        value = ''

        if self.grows and self.grows > len(shape):
            self.grows = len(shape)
        if not self.grows and self.__extraD:
            self.grows = 1
        if self.grows:
            shape.pop(self.grows - 1)

        shape = [s if s > 0 else 1 for s in shape]
        self.__growshape(shape)

        if nptype == "bool":
            value = False
        elif nptype != "string":
            try:
                # workaround for bug #5618 in numpy for 1.8 < ver < 1.9.2
                #
                if nptype == 'uint64':
                    value = numpy.iinfo(getattr(numpy, 'int64')).max
                else:
                    value = numpy.iinfo(getattr(numpy, nptype)).max
            except:
                try:
                    value = numpy.asscalar(
                        numpy.finfo(getattr(numpy, nptype)).max)
                except:
                    value = 0
        else:
            nptype = "str"

        dformat = 'SCALAR'
        if not self._scalar and shape and len(shape) > 0 and shape[0] >= 1:
            arr = numpy.empty(shape, dtype=nptype)
            arr.fill(value)
            if len(shape) == 1:
                dformat = 'SPECTRUM'
            else:
                dformat = 'IMAGE'
        else:
            arr = value

        dh = DataHolder(dformat, arr, NTP.npTt[self.h5Object.dtype], shape)

        if not self.__extraD:
            self.__writeData(dh)
        else:
            if not self.__grew:
                self.__grow()
            self.__writeGrowingData(dh)

    ## marks the field as failed
    # \brief It marks the field as failed
    def markFailed(self):
        if self.h5Object is not None:
            self.h5Object.attributes.create(
                "nexdatas_canfail", "string", overwrite=True)[...] = "FAILED"
            Streams.info(
                "EField::markFailed() - %s marked as failed" %
                (self.h5Object.name if hasattr(self.h5Object, "name")
                 else None))

            self.__fillMax()
