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
## \file ELink.py
# NeXus runnable elements

""" Definitions of link tag evaluation classes """

import sys

from .FElement import FElement
from .Errors import (XMLSettingSyntaxError)
from . import Streams
from .DataHolder import DataHolder

import pni.io.nx.h5 as nx


## link H5 tag element
class ELink(FElement):
    ## constructor
    # \param attrs dictionary of the tag attributes
    # \param last the last element from the stack
    def __init__(self, attrs, last):
        FElement.__init__(self, "link", attrs, last)
        ## stored H5 file object (defined in base class)
        self.h5Object = None
        ## strategy, i.e. INIT, STEP, FINAL
        self.strategy = None
        ## trigger for asynchronous writting
        self.trigger = None
        self.__groupTypes = None
        self.__target = None
        self.__name = None

    ## stores the tag content
    # \param xml xml setting
    # \param globalJSON global JSON string
    # \returns (strategy,trigger)
    def store(self, xml=None, globalJSON=None):

        if "name" in self._tagAttrs.keys():
            if self.source:
                if self.source.isValid():
                    return self.strategy, self.trigger

    ## runner
    # \brief During its thread run it fetches the data from the source
    def run(self):
        try:
            if self._tagAttrs["name"] is not None:
                if self.source:
                    dt = self.source.getData()
                    dh = None
                    if dt:
                        dh = DataHolder(**dt)
                    if not dh:
                        message = self.setMessage("Data without value")
                        self.error = message
                    target = dh.cast('string')
                    self.createLink(self.__groupTypes, target)
        except:
            message = self.setMessage(sys.exc_info()[1].__str__())
            self.error = message
        #            self.error = sys.exc_info()
        finally:
            if self.error:
                if self.canfail:
                    Streams.warn("Link::run() - %s  " % str(self.error))
                else:
                    Streams.error("Link::run() - %s  " % str(self.error))

    ## creates the link the H5 file
    # \param groupTypes dictionary with type:name group pairs
    # \param target NeXus target path
    def createLink(self, groupTypes=None, target=None):
        if groupTypes:
            self.__groupTypes = groupTypes
        if "name" in self._tagAttrs.keys():
            self.__setTarget(target)
            if self.__target:
                name = self._tagAttrs["name"]
                try:
                    self.h5Object = nx.link(
                        self.__target,
                        self._lastObject(),
                        name)
                except:
                    Streams.error(
                        "ELink::createLink() - "
                        "The link '%s' to '%s' type cannot be created"
                        % (name, self.__target),
                        std=False)
                    raise XMLSettingSyntaxError(
                        "The link '%s' to '%s' type cannot be created"
                        % (name, self.__target))
        else:
            Streams.error("ELink::createLink() - No name or type",
                          std=False)

            raise XMLSettingSyntaxError("No name or type")

    def __setTarget(self, target=None):
        if target is None and "target" in self._tagAttrs.keys():
            target = self._tagAttrs["target"]
        if target is not None:
            if '://' not in str(target) \
               and self.__groupTypes is not None:
                self.__target = (self.__typesToNames(
                    target, self.__groupTypes))
            else:
                self.__target = str(target)

    ## converts types to Names using groupTypes dictionary
    # \param text original directory
    # \param groupTypes tree of TNObject with name:nxtype
    # \returns directory defined by group names
    @classmethod
    def __typesToNames(cls, text, groupTypes):
        sp = str(text).split("/")
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
                        Streams.error(
                            "ELink::__typesToNames() - "
                            "Link creation problem: %s cannot be found"
                            % str(res + "/" + sgr[0]),
                            std=False)

                        raise XMLSettingSyntaxError(
                            "Link creation problem: %s cannot be found"
                            % str(res + "/" + sgr[0]))
        res = res + "/" + sp[-1]

        return res
