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

""" Definitions of CLIENT datasource """

from xml.dom import minidom

from . import Streams
from .DataSources import DataSource
from .Errors import DataSourceSetupError


class ClientSource(DataSource):
    """ Client data source
    """
    def __init__(self):
        """ constructor

        :brief: It sets all member variables to None
        """
        DataSource.__init__(self)
        #: (:obj:`str`) data name
        self.name = None
        #: (:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>)
        #: the current static JSON object
        self.__globalJSON = None
        #: (:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>)
        #: the current dynamic JSON object
        self.__localJSON = None

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml: datasource parameters
        :type xml: :obj:`str`
        :raises: :exc:`nxswriter.Errors.DataSourceSetupError` \
        :        if :obj:`name` is not defined
        """
        dom = minidom.parseString(xml)
        rec = dom.getElementsByTagName("record")
        if rec and len(rec) > 0:
            self.name = rec[0].getAttribute("name") \
                if rec[0].hasAttribute("name") else None
        if not self.name:
            Streams.error(
                "ClientSource::setup() - "
                "Client record name not defined: %s" % xml,
                std=False)
            raise DataSourceSetupError(
                "Client record name not defined: %s" % xml)

    def __str__(self):
        """ self-description

        :returns: self-describing string
        :rtype: :obj:`str`
        """
        return " CLIENT record %s" % (self.name)

    def setJSON(self, globalJSON, localJSON=None):
        """ sets JSON string

        :brief: It sets the currently used  JSON string
        :param globalJSON: static JSON string
        :type globalJSON: :obj:`dict` \
        :                 <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        :param localJSON: dynamic JSON string
        :type localJSON: :obj:`dict` \
                         <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        self.__globalJSON = globalJSON
        self.__localJSON = localJSON

    def getData(self):
        """ provides access to the data

        :returns: dictionary with collected data
        :rtype: {'rank': :obj:`str`, 'value': any, 'tangoDType': :obj:`str`, \
        :        'shape': :obj:`list` <int>, 'encoding': :obj:`str`, \
        :        'decoders': :obj:`str`} )
        """
        return self._getJSONData(
            self.name, self.__globalJSON, self.__localJSON)
