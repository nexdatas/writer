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

""" pool with datasource evaluation classes """

import threading
import sys

from . import TangoSource
from . import DBaseSource
from . import ClientSource
from . import PyEvalSource


class DataSourcePool(object):

    """ DataSource pool
    """

    def __init__(self, configJSON=None):
        """ constructor

        :brief: It creates know datasources
        :param configJSON: JSON dictionary with datasources
        :type configJSON: \
        :    :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        self.__pool = {"DB": DBaseSource.DBaseSource,
                       "TANGO": TangoSource.TangoSource,
                       "CLIENT": ClientSource.ClientSource,
                       "PYEVAL": PyEvalSource.PyEvalSource}
        self.appendUserDataSources(configJSON)
        #: (:obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>) \
        #:       global variables for specific datasources
        self.common = {}
        #: (:obj:`int`) step counter: INIT: -1; STEP: 1,2,3...; FINAL: -2;
        self.counter = 0
        #: (:obj:`bool`) can fail switch
        self.canfail = False
        #: (:class:`nxswriter.FileWriter.FTGroup`) H5 file handle
        self.nxroot = None
        #: (:class:`threading.Lock`) pool lock
        self.lock = threading.Lock()

    def appendUserDataSources(self, configJSON):
        """ loads user datasources

        :param configJSON: string with datasources
        :type configJSON: \
        :    :obj:`dict` <:obj:`str`, :obj:`dict` <:obj:`str`, any>>
        """
        if configJSON and 'datasources' in configJSON.keys() \
                and hasattr(configJSON['datasources'], 'keys'):
            for dk in configJSON['datasources'].keys():
                pkl = configJSON['datasources'][dk].split(".")
                pkg = ".".join(pkl[:-1])

                if pkg in sys.modules.keys():
                    pdec = sys.modules[pkg]
                    dec = pdec
                else:
                    dec = __import__(pkg, globals(),
                                     locals(), pkl[-1])
                self.append(getattr(dec, pkl[-1]), dk)

    def hasDataSource(self, datasource):
        """ checks if the datasource is registered

        :param datasource: the given datasource
        :type datasource: :obj:`str`
        :returns: True if it the datasource is registered
        :rtype: :obj:`bool`
        """
        return True if datasource in self.__pool.keys() \
            else False

    def get(self, datasource):
        """checks it the datasource is registered

        :param datasource: the given datasource name
        :type datasource: :obj:`str`
        :returns: datasource type if it the datasource
                  is registered
        :rtype: :class:`nxswriter.DataSources.DataSource`
        """
        if datasource in self.__pool.keys():
            return self.__pool[datasource]

    def pop(self, name):
        """ adds additional datasource

        :param name: name of the adding datasource
        :type name: :obj:`str`
        """
        self.__pool.pop(name, None)

    def append(self, datasource, name):
        """ adds additional datasource

        :param name: name of the adding datasource
        :type name: :obj:`str`
        :param datasource: instance of the adding datasource
        :type datasource: :class:`nxswriter.DataSources.DataSource`
        :returns: name of datasource
        :rtype: :obj:`str`
        """
        self.__pool[name] = datasource
        if not hasattr(datasource, "setup") \
                or not hasattr(datasource, "getData") \
                or not hasattr(datasource, "isValid"):
            self.pop(name)
            return
        return name
