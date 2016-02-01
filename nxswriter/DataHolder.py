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
## \file DataHolder.py
# holder for data

""" definition of a data holder with casting methods """

import numpy

from .Types import NTP
from . import Streams


## Holder for passing data
class DataHolder(object):

    ## constructor
    # \param rank format of the data, i.e. SCALAR, SPECTRUM, IMAGE
    # \param value value of the data. It may be also 1D and 2D array
    # \param tangoDType type of the data
    # \param shape shape of the data
    # \param encoding encoding type of Tango DevEncoded varibles
    # \param decoders poll with decoding classes
    def __init__(self, rank, value, tangoDType, shape,
                 encoding=None, decoders=None):

        ## data format
        self.format = rank
        ## data value
        self.value = value
        ## data type
        self.tangoDType = tangoDType
        ## data shape
        self.shape = shape
        ## encoding type of Tango DevEncoded varibles
        self.encoding = str(encoding) if encoding else None
        ## pool with decoding algorithm
        self.decoders = decoders

        if str(self.tangoDType) == 'DevEncoded':
            self.__setupEncoded()

    def __setupEncoded(self):
        self.shape = None
        if self.encoding and self.decoders and \
                self.decoders.hasDecoder(self.encoding):
            decoder = self.decoders.get(self.encoding)
            decoder.load(self.value)
            self.shape = decoder.shape()
            if self.shape:
                self.value = decoder.decode()
                rank = NTP().arrayRank(self.value)
                if rank > 2:
                    Streams.error(
                        "DataHolder::__setupEncoded() - "
                        "Unsupported variables format",
                        std=False)

                    raise ValueError("Unsupported variables format")
                self.format = ["SCALAR", "SPECTRUM",
                               "IMAGE", "VERTEX"][rank]

            tp = decoder.dtype
            if tp in NTP.npTt.keys():

                self.tangoDType = NTP.npTt[tp]

        if self.value is None:
            Streams.error(
                "DataHolder::__setupEncoded() - "
                "Encoding of DevEncoded variables not defined",
                std=False)

            raise ValueError(
                "Encoding of DevEncoded variables not defined")

        if self.shape is None:
            Streams.error(
                "DataHolder::__setupEncoded() - "
                "Encoding or Shape not defined",
                std=False)

            raise ValueError("Encoding or Shape not defined")

    ## casts the data into given type
    # \param dtype given type of data
    # \returns numpy array of defined type or list
    #          for strings or value for SCALAR
    def cast(self, dtype):
        if str(self.format).split('.')[-1] == "SCALAR":
            if dtype in NTP.npTt.keys() \
               and NTP.npTt[dtype] == str(self.tangoDType):
                return self.value
            else:
                if self.value == "" and (dtype not in ['str', 'string']):
                    return NTP.convert[dtype](0)
                else:
                    return NTP.convert[dtype](self.value)

        else:

            if dtype in NTP.npTt.keys() \
                    and NTP.npTt[dtype] == str(self.tangoDType) \
                    and (dtype not in ['str', 'string']):
                if type(self.value).__name__ == 'ndarray' and \
                        self.value.dtype.name == dtype:
                    return self.value
                else:
                    return numpy.array(self.value, dtype=dtype)
            else:
                if dtype in ['str', 'string']:
                    return numpy.array(self.value, dtype='str')
                else:
                    return numpy.array(
                        NTP().createArray(self.value, NTP.convert[dtype]),
                        dtype=dtype)
