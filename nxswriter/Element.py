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
#

""" Provides the base class Element for xml tags """

from . import Streams


##
class Element(object):
    """ Tag element stored on our stack
    """

    def __init__(self, name, attrs, last=None):
        """ constructor

        :param name: tag name
        :param attrs: dictionary of the tag attributes
        :param last: the last element from the stack
        """
        #: stored tag name
        self.tagName = name
        #: tag attributes
        self._tagAttrs = attrs
        #: stored tag content
        self.content = []
        #: doc string
        self.doc = ""
        #: the previous element
        self.last = last

    def _lastObject(self):
        """ last H5 file object
        :returns: H5 file object of the previous element
        """
        if hasattr(self.last, "h5Object"):
            return self.last.h5Object
        else:
            Streams.warn(
                "Element::_lastObject() - H5 Object not found : %s"
                % self.tagName)

    def _beforeLast(self):
        """ before last stack element

        :returns:  before last element placed on the stack
        """
        if self.last:
            return self.last.last
        else:
            return None

    def store(self, xml=None, globalJSON=None):
        """ stores the tag

        :brief: abstract method to store the tag element
        :param xml: tuple of xml code
        :param globalJSON: global JSON string
        """
        pass
