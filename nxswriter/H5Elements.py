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

""" Definitions of tag evaluation classes """

from .Element import Element
from .FElement import FElement
from .DataHolder import DataHolder


class EFile(FElement):
    """ file H5 element
    """
    def __init__(self, attrs, last, h5fileObject):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :obj:`Element.Element`
        :param h5fileObject: H5 file object
        :type h5fileObject: :obj:`pni.io.nx.h5._nxh5.nxfile`
        """
        FElement.__init__(self, "file", attrs, last, h5fileObject)


class EDoc(Element):
    """ doc tag element
    """
    def __init__(self, attrs, last):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :obj:`Element.Element`
        """
        Element.__init__(self, "doc", attrs, last)

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if self._beforeLast():
            self._beforeLast().doc += "".join(xml[1])


class ESymbol(Element):
    """ symbol tag element
    """
    def __init__(self, attrs, last):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :obj:`Element.Element`
        """
        Element.__init__(self, "symbol", attrs, last)
        #: (:obj:`dict` <:obj:`str`, :obj:`str`>) \
        #:    dictionary with symbols4
        self.symbols = {}

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting2
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if "name" in self._tagAttrs.keys():
            self.symbols[self._tagAttrs["name"]] = self.last.doc


class EDimensions(Element):
    """ dimensions tag element
    """
    def __init__(self, attrs, last):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :obj:`Element.Element`
        """
        Element.__init__(self, "dimensions", attrs, last)
        if "rank" in attrs.keys():
            self.last.rank = attrs["rank"]


class EDim(Element):
    """ dim tag element
    """
    def __init__(self, attrs, last):
        """ constructor

        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :obj:`Element.Element`
        """
        Element.__init__(self, "dim", attrs, last)
        if ("index" in attrs.keys()) and ("value" in attrs.keys()):
            self._beforeLast().lengths[attrs["index"]] = attrs["value"]
        #: (:obj:`str`) index attribute
        self.__index = None
        #: (:obj:`DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`list` <:obj:`str`>) tag content
        self.content = []
        if "index" in attrs.keys():
            self.__index = attrs["index"]

    def store(self, xml=None, globalJSON=None):
        """ stores the tag content

        :param xml: xml setting
        :type xml: :obj: `str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if self.__index is not None and self.source:
            dt = self.source.getData()
            if dt and isinstance(dt, dict):
                dh = DataHolder(**dt)
                if dh:
                    self._beforeLast().lengths[self.__index] = str(
                        dh.cast("string"))
