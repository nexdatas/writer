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
## \file DataSourceFactory.py
# data-source types

""" factory with datasources """

from __future__ import print_function

import sys

from . import Streams
from . import DataSources
from .Element import Element


## Data source creator
class DataSourceFactory(Element):
    ## constructor
    # \param attrs dictionary with the tag attributes
    # \param last the last element on the stack
    def __init__(self, attrs, last):
        Element.__init__(self, "datasource", attrs, last)
        ## datasource pool
        self.__dsPool = None

    ## sets the used datasources
    # \param datasources pool to be set
    def setDataSources(self, datasources):
        self.__dsPool = datasources

    ## creates data source
    # \param attrs dictionary with the tag attributes
    def __createDSource(self, attrs):
        if "type" in attrs.keys():
            if self.__dsPool and self.__dsPool.hasDataSource(attrs["type"]):
                self.last.source = self.__dsPool.get(attrs["type"])()
            else:
                print("DataSourceFactory::__createDSource - "
                      "Unknown data source",
                      file=sys.stderr)

                if Streams.log_error:
                    print("DataSourceFactory::__createDSource - "
                          "Unknown data source",
                          file=Streams.log_error)

                self.last.source = DataSources.DataSource()
        else:
            print("DataSourceFactory::__createDSource - Typeless data source",
                  file=sys.stderr)

            if Streams.log_error:
                print("DataSourceFactory::__createDSource - "
                      "Typeless data source",
                      file=Streams.log_error)

            self.last.source = DataSources.DataSource()

    ##  sets the datasource form xml string
    # \param xml input parameter
    # \param globalJSON global JSON string
    def store(self, xml=None, globalJSON=None):
        self.__createDSource(self._tagAttrs)
        jxml = "".join(xml)
        self.last.source.setup(jxml)
        if hasattr(self.last.source, "setJSON") and globalJSON:
            self.last.source.setJSON(globalJSON)
        if hasattr(self.last.source, "setDataSources"):
            self.last.source.setDataSources(self.__dsPool)
        if self.last and hasattr(self.last, "tagAttributes"):
            self.last.tagAttributes["nexdatas_source"] = ("NX_CHAR", jxml)

    ## sets the used decoders
    # \param decoders pool to be set
    def setDecoders(self, decoders):
        if self.last and self.last.source and self.last.source.isValid() \
                and hasattr(self.last.source, "setDecoders"):
            self.last.source.setDecoders(decoders)
