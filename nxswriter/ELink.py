#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \file ELink.py
# NeXus runnable elements

""" Definitions of link tag evaluation classes """

from .FElement import FElement
from .Errors import (XMLSettingSyntaxError)
from . import Streams


## link H5 tag element
class ELink(FElement):
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElement.__init__(self, "link", attrs, last)
        ## stored H5 file object (defined in base class)
        self.h5Object = None

    ## converts types to Names using groupTypes dictionary
    # \param text original directory
    # \param groupTypes tree of TNObject with name:nxtype
    # \returns directory defined by group names
    @classmethod
    def __typesToNames(cls, text, groupTypes):
        sp = text.split("/")
        res = ""
        ch = groupTypes
        valid = True if ch.name == "root" else False

        for gr in sp[:-1]:
            if len(gr) > 0:
                sgr = gr.split(":")
                if len(sgr) > 1:
                    res = "/".join([res, sgr[0]])
                    if valid:
                        ch = ch.child(name=sgr[0])
                        if not ch:
                            valid = False
                else:
                    if valid:
                        c = ch.child(nxtype=sgr[0])
                        if c:
                            res = "/".join([res, c.name])
                            ch = c
                        else:
                            c = ch.child(name=sgr[0])
                            if c:
                                res = "/".join([res, sgr[0]])
                                ch = c
                            else:
                                valid = False
                    if not valid:
                        if Streams.log_error:
                            print >> Streams.log_error, \
                                "ELink::__typesToNames() - "\
                                "No %s in  groupTypes " % str(sgr[0])
                        raise XMLSettingSyntaxError(
                            "No " + str(sgr[0]) + " in groupTypes ")
        res = res + "/" + sp[-1]

        return res

    ## creates the link the H5 file
    # \param groupTypes dictionary with type:name group pairs
    def createLink(self, groupTypes):
        if ("name" in self._tagAttrs.keys()) and \
                ("target" in self._tagAttrs.keys()):
            path = (self.__typesToNames(
                    self._tagAttrs["target"], groupTypes)).encode()
            name = self._tagAttrs["name"].encode()
            try:
                self.h5Object = self._lastObject().link(path, name)
            except:
                if Streams.log_error:
                    print >> Streams.log_error, \
                        "ELink::createLink() - "\
                        "The link '%s' to '%s' type cannot be created" \
                        % (name, path)
                raise XMLSettingSyntaxError(
                    "The link '%s' to '%s' type cannot be created"
                    % (name, path))
        else:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "ELink::createLink() - No name or type"
            raise XMLSettingSyntaxError("No name or type")
