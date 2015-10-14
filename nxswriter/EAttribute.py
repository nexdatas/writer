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
## \file EAttribute.py
# NeXus runnable elements

""" Definitions of attribute tag evaluation classes """

import sys

import numpy

from .DataHolder import DataHolder
from .FElement import FElement
from . import Streams


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
    # \param globalJSON global JSON string
    # \returns (strategy,trigger)
    def store(self, xml=None, globalJSON=None):

        if "name" in self._tagAttrs.keys():
            self.name = self._tagAttrs["name"]
            if "type" in self._tagAttrs.keys():
                tp = self._tagAttrs["type"]
            else:
                tp = "NX_CHAR"

            if tp == "NX_CHAR":
                shape = self._findShape(self.rank, self.lengths)
            else:
                shape = self._findShape(self.rank, self.lengths,
                                        extends=True, checkData=True)
            val = ("".join(self.content)).strip().encode()
            if not shape:
                self.last.tagAttributes[self.name] = (tp, val)
            else:
                self.last.tagAttributes[self.name] = (tp, val, tuple(shape))

            if self.source:
                if self.source.isValid():
                    return self.strategy, self.trigger

    ## runner
    # \brief During its thread run it fetches the data from the source
    def run(self):
        try:
            if self.name:
                if not self.h5Object:
                    ## stored H5 file object (defined in base class)
                    self.h5Object = self.last.h5Attribute(self.name)
                if self.source:
                    dt = self.source.getData()
                    dh = None
                    if dt:
                        dh = DataHolder(**dt)
                    if not dh:
                        message = self.setMessage("Data without value")
                        self.error = message
                    elif not hasattr(self.h5Object, 'shape'):
                        message = self.setMessage("PNI Object not created")
                        Streams.warn("Group::run() - %s " % message[0])
                        self.error = message
                    else:
                        self.h5Object[...] = dh.cast(self.h5Object.dtype)
        except:
            message = self.setMessage(sys.exc_info()[1].__str__())
            self.error = message
        #            self.error = sys.exc_info()
        finally:
            if self.error:
                if self.canfail:
                    Streams.warn("Attribute::run() - %s  " % str(self.error))
                else:
                    Streams.error("Attribute::run() - %s  " % str(self.error))

    ## fills object with maximum value
    # \brief It fills object or an extend part of object by default value
    def __fillMax(self):
        if self.name and not self.h5Object:
            self.h5Object = self.last.h5Attribute(self.name)
        shape = list(self.h5Object.shape)

        nptype = self.h5Object.dtype
        value = ''

        if nptype != "string":
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

        if shape and len(shape) > 0:
            arr = numpy.empty(shape, dtype=nptype)
            arr.fill(value)
        else:
            arr = value

        self.h5Object[...] = arr

    ## marks the field as failed
    # \brief It marks the field as failed
    def markFailed(self):
        field = self._lastObject()
        if field is not None:
            field.attributes.create("nexdatas_canfail", "string",
                                    overwrite=True)[...] = "FAILED"
            Streams.info("EAttribute::markFailed() - "
                         "%s of %s marked as failed" %
                         (self.h5Object.name
                          if hasattr(self.h5Object, "name") else None,
                          field.name if hasattr(field, "name") else None))
            self.__fillMax()
