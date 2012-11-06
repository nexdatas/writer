#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \package ndts nexdatas
## \file DecoderPool.py
# decoder classes

import struct
import numpy

## VIDEO IMAGE LIMA decoder
class VDEOdecoder(object):

    ## constructor
    # \brief It clears the local variables
    def __init__(self):
        ## decoder name
        self.name = "LIMA_VIDEO_IMAGE"
        ## decoder format
        self.format = None
        ## data type
        self.dtype = None
        
        ## image data
        self._value = None
        ## header and image data
        self._data = None
        ## struct header format
        self._headerFormat = '!IHHqiiHHHH'
        ## header data
        self._header = {}
        ## format modes
        self._formatID = {0:'B', 1:'H', 2:'I', 3:'L'}
        ## dtype modes
        self._dtypeID = {0:'uint8', 1:'uint16', 2:'uint32', 3:'uint64'}


    ## loads encoded data
    # \param data encoded data    
    def load(self, data):
        self._data = data
        self.format = data[0]
        self._loadHeader(data[1][:struct.calcsize(self._headerFormat)])        
        self._value = None
        


    ## loads the image header    
    # \param headerData buffer with header data
    def _loadHeader(self, headerData):
        hd = struct.unpack(self._headerFormat, headerData)
        hdr = struct.unpack(self._headerFormat, headerData)
        self._header = {}
        self._header['magic'] = hdr[0]
        self._header['headerVersion'] = hdr[1]
        self._header['imageMode'] = hdr[2]
        self._header['frameNumber'] = hdr[3]
        self._header['width'] = hdr[4]
        self._header['height'] = hdr[5]
        self._header['endianness'] = hdr[6]
        self._header['headerSize'] = hdr[7]
        self._header['padding'] = hdr[7:]
        
        self.dtype = self._dtypeID[self._header['imageMode']]

    ## provides the data shape
    # \returns the data shape if data was loaded
    def shape(self):
        if self._header:
            return [self._header['width'],self._header['height']]
        


    ## provides the decoded data
    # \returns the decoded data if data was loaded
    def decode(self):        
        if not self._header or not self._data:
            return
        if not self._value:
            image = self._data[1][struct.calcsize(self._headerFormat):]
            format = self._formatID[self._header['imageMode']]
            fSize = struct.calcsize(format)
            self._value = numpy.array(
                struct.unpack(format*(len(image)/fSize), image), dtype=self.dtype
                ).reshape(self._header['width'],self._header['height'])
        return self._value




## Data source creator
class DecoderPool(object):        


    ## constructor
    # \brief It creates know decoders    
    # \param configJSON string with decoders    
    def __init__(self, configJSON = None):
        self._knowDecoders = { "LIMA_VIDEO_IMAGE":VDEOdecoder }
        self._pool = {}
        self._userDecoders = {}
        
        self._createDecoders()
        self._appendUserDecoders(configJSON)


    ## loads user decoders
    # \param configJSON string with decoders    
    def _appendUserDecoders(self, configJSON):
        if configJSON and 'decoders' in configJSON.keys() and  hasattr(configJSON['decoders'],'keys'):
            for dk in configJSON['decoders'].keys():
                pkl = configJSON['decoders'][dk].split(".")
                dec =  __import__(".".join(pkl[:-1]), globals(), locals(), pkl[-1])  
                self.append(getattr(dec, pkl[-1]), dk)
            

    ## creates know decoders
    # \brief It calls constructor of know decoders    
    def _createDecoders(self):
        for dk in self._knowDecoders.keys():
            self._pool[dk] = self._knowDecoders[dk]()


            
    ## checks it the decoder is registered        
    # \param decoder the given decoder
    # \returns True if it the decoder is registered        
    def hasDecoder(self, decoder):
        return True if decoder in self._pool.keys() else False


    ## checks it the decoder is registered        
    # \param decoder the given decoder
    # \returns True if it the decoder is registered        
    def get(self, decoder):
        if decoder in self._pool.keys():
            return self._pool[decoder]

    
    ## adds additional decoder
    # \param name name of the adding decoder
    # \param decoder instance of the adding decoder
    # \returns name of decoder
    def append(self, decoder, name = None):
        if not hasattr(decoder,"load") or not hasattr(decoder,"name") \
                or not hasattr(decoder,"shape") or not hasattr(decoder,"decode") \
                or not hasattr(decoder,"dtype") or not hasattr(decoder,"format"):
            return 
        if name is None:
            if not decoder.name:
                return
            dname = decoder.name
        else:
            dname = name
        self._pool[dname] = decoder
        return dname


    ## adds additional decoder
    # \param name name of the adding decoder
    def pop(self, name):
        self._pool.pop(name, None)

        
