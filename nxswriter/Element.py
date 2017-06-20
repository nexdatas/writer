#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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


class Element(object):

    """ Tag element stored on our stack
    """

    def __init__(self, name, attrs, last=None, streams=None):
        """ constructor

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`PyTango.Device_4Impl`
        """
        #: (:obj:`str`) stored tag name
        self.tagName = name
        #: tag attributes
        self._tagAttrs = attrs
        #: (:obj:`list` <:obj:`str`>) stored tag content
        self.content = []
        #: (:obj:`str`) doc string
        self.doc = ""
        #: (:class:`nxswriter.Element.Element`) the previous element
        self.last = last
        #: (:class:`StreamSet` or :class:`PyTango.Device_4Impl`) stream set
        self._streams = streams

    def _lastObject(self):
        """ last H5 file object
        :returns: H5 file object of the previous element
        :rtype: (:class:`nxswriter.Element.Element`)
        """
        if hasattr(self.last, "h5Object"):
            return self.last.h5Object
        else:
            if self._streams:
                self._streams.warn(
                    "Element::_lastObject() - H5 Object not found : %s"
                    % self.tagName)

    def _beforeLast(self):
        """ before last stack element

        :returns:  before last element placed on the stack
        :rtype: (:obj: `Element.Element`)
        """
        if self.last:
            return self.last.last
        else:
            return None

    def store(self, xml=None, globalJSON=None):
        """ stores the tag

        :brief: abstract method to store the tag element
        :param xml: tuple of xml code
        :type xml: :obj:`str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        : :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        pass
