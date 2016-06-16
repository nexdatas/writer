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

""" factory with datasources """

from . import Streams
from . import DataSources
from .Element import Element


class DataSourceFactory(Element):
    """ Data source creator
    """
    def __init__(self, attrs, last):
        """ constructor

        :param attrs: dictionary with the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element on the stack
        :type last: :obj:`Element.Element`
        """
        Element.__init__(self, "datasource", attrs, last)
        #: (:obj:`DataSourcePool.DataSourcePool`) datasource pool
        self.__dsPool = None

    def setDataSources(self, datasources):
        """ sets the used datasources

        :param datasources: pool to be set
        :type datasources: :obj:`DataSourcePool.DataSourcePool`
        """
        self.__dsPool = datasources

    def __createDSource(self, attrs):
        """ creates data source

        :param attrs: dictionary with the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        """
        if "type" in attrs.keys():
            if self.__dsPool and self.__dsPool.hasDataSource(attrs["type"]):
                self.last.source = self.__dsPool.get(attrs["type"])()
            else:
                Streams.error(
                    "DataSourceFactory::__createDSource - "
                    "Unknown data source")
                self.last.source = DataSources.DataSource()
        else:
            Streams.error(
                "DataSourceFactory::__createDSource - "
                "Typeless data source")
            self.last.source = DataSources.DataSource()

    def store(self, xml=None, globalJSON=None):
        """ sets the datasource form xml string

        :param xml: input parameter
        :type xml: :obj:`str`
        :param globalJSON: global JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        self.__createDSource(self._tagAttrs)
        jxml = "".join(xml)
        self.last.source.setup(jxml)
        if hasattr(self.last.source, "setJSON") and globalJSON:
            self.last.source.setJSON(globalJSON)
        if hasattr(self.last.source, "setDataSources"):
            self.last.source.setDataSources(self.__dsPool)
        if self.last and hasattr(self.last, "tagAttributes"):
            self.last.tagAttributes["nexdatas_source"] = ("NX_CHAR", jxml)

    def setDecoders(self, decoders):
        """ sets the used decoders

        :param decoders: pool to be set
        :type decoders: :obj:`nxswriter.DecoderPool.DecorderPool`
        """
        if self.last and self.last.source and self.last.source.isValid() \
                and hasattr(self.last.source, "setDecoders"):
            self.last.source.setDecoders(decoders)
