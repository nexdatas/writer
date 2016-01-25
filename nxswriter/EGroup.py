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
## \file EGroup.py
# NeXus runnable elements

""" Definitions of group tag evaluation classes """

import numpy

from .FElement import FElementWithAttr
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)
from . import Streams


## group H5 tag element
class EGroup(FElementWithAttr):
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElementWithAttr.__init__(self, "group", attrs, last)
        if self._lastObject() is not None:
            if ("type" in attrs.keys()) and ("name" in attrs.keys()):
                gname = attrs["name"]
            elif "type" in attrs.keys():
                gname = attrs["type"][2:]
            else:
                Streams.error(
                    "EGroup::__init__() - The group type not defined",
                    std=False)

                raise XMLSettingSyntaxError("The group type not defined")
            try:
                ## stored H5 file object (defined in base class)
                self.h5Object = self._lastObject().create_group(
                    gname, attrs["type"])
            except:
                Streams.error(
                    "EGroup::__init__() - "
                    "The group '%s' of '%s' type cannot be created. \n"
                    "Please remove the old file, change the file name "
                    "or change the group name." %
                    (gname, attrs["type"]),
                    std=False)

                raise XMLSettingSyntaxError(
                    "The group '%s' of '%s' type cannot be created. \n"
                    "Please remove the old file, change the file name "
                    "or change the group name." %
                    (gname, attrs["type"]))

        else:
            Streams.error(
                "EGroup::__init__() - "
                "File object for the last element does not exist",
                std=False)

            raise XMLSettingSyntaxError(
                "File object for the last element does not exist")

        for key in attrs.keys():
            if key not in ["name", "type"]:
                if key in NTP.aTn.keys():
                    if hasattr(attrs[key], "encode"):
                        try:
                            (self.h5Object.attributes.create(
                                key,
                                NTP.nTnp[NTP.aTn[key]],
                                overwrite=True))[...] = \
                                attrs[key]
                        except:
                            (self.h5Object.attributes.create(
                                key,
                                NTP.nTnp[NTP.aTn[key]],
                                overwrite=True
                            ))[...] = \
                                NTP.convert[
                                    str(self.h5Object.attributes[
                                        key
                                    ].dtype)](attrs[key])

                    else:
                        try:
                            self.h5Object.attributes.create(
                                key,
                                NTP.nTnp[NTP.aTn[key]],
                                overwrite=True
                            )[...] = attrs[key]
                        except:
                            self.h5Object.attributes.create(
                                key,
                                NTP.nTnp[NTP.aTn[key]],
                                overwrite=True
                            )[...] \
                                = NTP.convert[str(self.h5Object.attributes[
                                    key].dtype)](attrs[key])

                elif key in NTP.aTnv.keys():

                    shape = (len(attrs[key]),)
                    (self.h5Object.attributes.create(
                        key, NTP.nTnp[NTP.aTnv[key]],
                        shape, overwrite=True))[...] = numpy.array(attrs[key])
                else:
                    (self.h5Object.attributes.create(
                        key, "string", overwrite=True))[...] \
                        = attrs[key]

    ## stores the tag content
    # \param xml xml setting
    # \param globalJSON global JSON string
    def store(self, xml=None, globalJSON=None):
        self._createAttributes()
