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

""" Definitions of PYEVAL datasource """

import threading
import copy
from xml.dom import minidom

from .Types import NTP
from . import Streams

from .DataHolder import DataHolder
from .DataSources import DataSource
from .Errors import DataSourceSetupError


class Variables(object):
    """ Variables for PyEval datasource
    """


class PyEvalSource(DataSource):
    """ Python Eval data source
    """

    def __init__(self):
        """ constructor

        :brief: It cleans all member variables
        """
        DataSource.__init__(self)
        #: (:obj:`str`) name of data
        self.__name = None
        #: (:obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>) \
        #:     the current  static JSON object
        self.__globalJSON = None
        #: (:obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>) \
        #:     the current  dynamic JSON object
        self.__localJSON = None
        #: (:class:`nxswriter.DataSourcePool.DataSourcePool`) datasource pool
        self.__pool = None
        #: (:obj:`dict` <:obj:`str`, (:obj:`str`,:obj:`str`) > ) \
        #:     datasources dictionary with {dsname: (dstype, dsxml)}
        self.__sources = {}
        #: (:obj:`dict` \
        #:     <:obj:`str`, (:class:`nxswriter.DataSources.DataSource`) > ) \
        #:  datasource dictionary {name: DataSource}
        self.__datasources = {}
        #: (:obj:`str`) python script
        self.__script = ""
        #: (:obj:`bool`) True if common block used
        self.__commonblock = False
        #: (:class:`threading.Lock`) lock for common block
        self.__lock = None
        #: (:obj:`dict` <:obj:`str`, any> ) \
        #:    common block variables
        self.__common = None
        #: ({"rank": :obj:`str`, "value": any, "tangoDType": :obj:`str`, \
        #:   "shape": :obj:`list`<int>, "encoding": :obj:`str`, \
        #:   "decoders": :obj:`str`} ) \
        #:    data format
        self.__result = {"rank": "SCALAR",
                         "value": None,
                         "tangoDType": "DevString",
                         "shape": [1, 0],
                         "encoding": None,
                         "decoders": None}

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml:  datasource parameters
        :type xml: :obj:`str`
        """

        dom = minidom.parseString(xml)
        mds = dom.getElementsByTagName("datasource")
        inputs = []
        if mds and len(mds) > 0:
            inputs = mds[0].getElementsByTagName("datasource")
        for inp in inputs:
            if inp.hasAttribute("name") and inp.hasAttribute("type"):
                name = inp.getAttribute("name").strip()
                dstype = inp.getAttribute("type").strip()
                if len(name) > 0:
                    if len(name) > 3 and name[:2] == 'ds.':
                        name = name[3:]
                    self.__sources[name] = (dstype, inp.toxml())
                else:
                    Streams.error(
                        "PyEvalSource::setup() - "
                        "PyEval input %s not defined" % name,
                        std=False)

                    raise DataSourceSetupError(
                        "PyEvalSource::setup() - "
                        "PyEval input %s not defined" % name)

            else:
                Streams.error(
                    "PyEvalSource::setup() - "
                    "PyEval input name wrongly defined",
                    std=False)

                raise DataSourceSetupError(
                    "PyEvalSource::setup() - "
                    "PyEval input name wrongly defined")
        res = dom.getElementsByTagName("result")
        if res and len(res) > 0:
            self.__name = res[0].getAttribute("name") \
                if res[0].hasAttribute("name") else 'result'
            if len(self.__name) > 3 and self.__name[:2] == 'ds.':
                self.__name = self.__name[3:]
            self.__script = self._getText(res[0])

        if len(self.__script) == 0:
            Streams.error(
                "PyEvalSource::setup() - "
                "PyEval script %s not defined" % self.__name,
                std=False)

            raise DataSourceSetupError(
                "PyEvalSource::setup() - "
                "PyEval script %s not defined" % self.__name)

        if "commonblock" in self.__script:
            self.__commonblock = True
        else:
            self.__commonblock = False

    ##
    def __str__(self):
        """ self-description

        :returns: self-describing string
        :rtype: :obj:`str`
        """
        return " PYEVAL %s" % (self.__script)

    def setJSON(self, globalJSON, localJSON=None):
        """ sets JSON string

        :brief: It sets the currently used  JSON string
        :param globalJSON: static JSON string
        :type globalJSON: \
        :     :obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>
        :param localJSON: dynamic JSON string
        :type localJSON: \
        :     :obj:`dict` <:obj:`str` , :obj:`dict` <:obj:`str`, any>>
        """
        self.__globalJSON = globalJSON
        self.__localJSON = localJSON
        for source in self.__datasources.values():
            if hasattr(source, "setJSON"):
                source.setJSON(self.__globalJSON,
                               self.__localJSON)

    def getData(self):
        """ provides access to the data

        :returns:  dictionary with collected data
        :rtype: {'rank': :obj:`str`, 'value': any, 'tangoDType': :obj:`str`, \
        :        'shape': :obj:`list` <int>, 'encoding': :obj:`str`, \
        :        'decoders': :obj:`str`} )
        """
        if not self.__name:
            Streams.error(
                "PyEvalSource::getData() - PyEval datasource not set up",
                std=False)

            raise DataSourceSetupError(
                "PyEvalSource::getData() - PyEval datasource not set up")

        ds = Variables()
        for name, source in self.__datasources.items():
            if name in self.__script:
                dt = source.getData()
                value = None
                if dt:
                    dh = DataHolder(**dt)
                    if dh and hasattr(dh, "value"):
                        value = dh.value
                setattr(ds, name, value)

        setattr(ds, self.__name, None)

        if not self.__commonblock:
            exec(self.__script.strip(), {}, {"ds": ds})
            rec = getattr(ds, self.__name)
        else:
            rec = None
            with self.__lock:
                exec(self.__script.strip(), {}, {
                    "ds": ds, "commonblock": self.__common})
                rec = copy.deepcopy(getattr(ds, self.__name))
        if isinstance(rec,list):
            print "RES", (rec[0].dtype if hasattr(rec[0], "dtype") else type(rec[0]))
            if hasattr(rec[0], "tolist"):
                print "RES1", type(rec[0].tolist()),type(rec[0].tolist()[0]) 
        ntp = NTP()
        rank, shape, dtype = ntp.arrayRankShape(rec)
        if isinstance(rec,list):
            print "RE2", rank, shape, pythonDType        
        if rank in NTP.rTf:
            if shape is None:
                shape = [1, 0]

            return {"rank": NTP.rTf[rank],
                    "value": rec,
                    "tangoDType": NTP.aTt[dtype],
                    "shape": shape}

    def setDecoders(self, decoders):
        """ sets the used decoders

        :param decoders: pool to be set
        :type decoders: :class:`nxswriter.DecoderPool.DecoderPool`
        """
        self.__result["decoders"] = decoders
        for source in self.__datasources.values():
            if hasattr(source, "setDecoders"):
                source.setDecoders(decoders)

    def setDataSources(self, pool):
        """ sets the datasources

        :param pool: datasource pool
        :type pool: :class:`nxswriter.DataSourcePool.DataSourcePool`
        """
        self.__pool = pool
        pool.lock.acquire()
        try:
            if 'PYEVAL' not in self.__pool.common.keys():
                self.__pool.common['PYEVAL'] = {}
            if "lock" not in self.__pool.common['PYEVAL'].keys():
                self.__pool.common['PYEVAL']["lock"] = threading.Lock()
            self.__lock = self.__pool.common['PYEVAL']["lock"]
            if "common" not in self.__pool.common['PYEVAL'].keys():
                self.__pool.common['PYEVAL']["common"] = {}
                if self.__pool.nxroot is not None:
                    self.__pool.common['PYEVAL']["common"]["__nxroot__"] = \
                        self.__pool.nxroot.h5object
                    self.__pool.common['PYEVAL']["common"]["__root__"] = \
                        self.__pool.nxroot
            self.__common = self.__pool.common['PYEVAL']["common"]

        finally:
            pool.lock.release()

        for name, inp in self.__sources.items():
            if name in self.__script:
                if pool and pool.hasDataSource(inp[0]):
                    self.__datasources[name] = pool.get(inp[0])()
                    self.__datasources[name].setup(inp[1])
                    if hasattr(self.__datasources[name], "setJSON") \
                            and self.__globalJSON:
                        self.__datasources[name].setJSON(self.__globalJSON)
                    if hasattr(self.__datasources[name], "setDataSources"):
                        self.__datasources[name].setDataSources(pool)

                else:
                    Streams.error(
                        "PyEvalSource::setDataSources - Unknown data source")
                    self.__datasources[name] = DataSource()
