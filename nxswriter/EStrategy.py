#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
#

""" Definitions of strategy evaluation classes """

from .Element import Element
from . import Streams


class EStrategy(Element):
    """## strategy tag element

    """
    def __init__(self, attrs, last):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        """
        Element.__init__(self, "strategy", attrs, last)

        if "mode" in attrs.keys():
            self.last.strategy = attrs["mode"]
            if hasattr(self.last, "tagAttributes"):
                self.last.tagAttributes["nexdatas_strategy"] = (
                    "NX_CHAR", attrs["mode"])
        if "trigger" in attrs.keys():
            self.last.trigger = attrs["trigger"]
            Streams.info("TRIGGER %s" % attrs["trigger"])
            if hasattr(self.last, "tagAttributes"):
                self.last.tagAttributes["nexdatas_strategy"] = (
                    "NX_CHAR", attrs["trigger"])
        if "grows" in attrs.keys() and hasattr(self.last, "grows"):
            self.last.grows = int(attrs["grows"])
            if self.last.grows < 1:
                self.last.grows = 1
        if "canfail" in attrs.keys():
            self.last.canfail = True \
                if attrs["canfail"].upper() == "TRUE" else False
        if "compression" in attrs.keys() and hasattr(self.last, "compression"):
            self.last.compression = True \
                if attrs["compression"].upper() == "TRUE" else False
            if self.last.compression:
                if "rate" in attrs.keys() and hasattr(self.last, "rate"):
                    self.last.rate = int(attrs["rate"])
                    if self.last.rate < 0:
                        self.last.rate = 0
                    if self.last.rate > 9:
                        self.last.rate = 9
                if "shuffle" in attrs.keys() and hasattr(self.last, "shuffle"):
                    self.last.shuffle = False \
                        if attrs["shuffle"].upper() == "FALSE" else True

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj:`str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        self.last.postrun = ("".join(self.content)).strip()
