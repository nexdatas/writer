#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

## UTF8 decoder
class UTF8decoder(object):

    ## constructor
    # \brief It clears the local variables
    def __init__(self):
        ## decoder name
        self.name = "UTF8"
        ## decoder format
        self.format = None
        ## data type
        self.dtype = None
        
        ## image data
        self.__value = None
        ## header and image data
        self.__data = None


    ## loads encoded data
    # \param data encoded data    
    def load(self, data):
        self.__data = data
        self.format = data[0]
        self.__value = None
        self.dtype = "string"

    ## provides the data shape
    # \returns the data shape if data was loaded
    def shape(self):
        return [1,0]
        


    ## provides the decoded data
    # \returns the decoded data if data was loaded
    def decode(self):        
        if not self.__data:
            return
        if not self.__value:
            self.__value = self.__data[1]
        return self.__value



## INT decoder
class UINT32decoder(object):

    ## constructor
    # \brief It clears the local variables
    def __init__(self):
        ## decoder name
        self.name = "UINT32"
        ## decoder format
        self.format = None
        ## data type
        self.dtype = None
        
        ## image data
        self.__value = None
        ## header and image data
        self.__data = None


    ## loads encoded data
    # \param data encoded data    
    def load(self, data):
        self.__data = data
        self.format = data[0]
        self.__value = None
        self.dtype = "uint32"

    ## provides the data shape
    # \returns the data shape if data was loaded
    def shape(self):
        return [len(self.__data[1])/4,0]
        


    ## provides the decoded data
    # \returns the decoded data if data was loaded
    def decode(self):        
        if not self.__data:
            return
        if not len(self.__data) % 4:
            return
        if not self.__value:
            self.__value = numpy.array(
                struct.unpack('I'*(len(self.__data[1])/4), self.__data[1]), dtype=self.dtype
                ).reshape(len(self.__data[1])/4)
        return self.__value




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
        self.__value = None
        ## header and image data
        self.__data = None
        ## struct header format
        self.__headerFormat = '!IHHqiiHHHH'
        ## header data
        self.__header = {}
        ## format modes
        self.__formatID = {0:'B', 1:'H', 2:'I', 3:'L'}
        ## dtype modes
        self.__dtypeID = {0:'uint8', 1:'uint16', 2:'uint32', 3:'uint64'}


    ## loads encoded data
    # \param data encoded data    
    def load(self, data):
        self.__data = data
        self.format = data[0]
        self._loadHeader(data[1][:struct.calcsize(self.__headerFormat)])        
        self.__value = None
        


    ## loads the image header    
    # \param headerData buffer with header data
    def _loadHeader(self, headerData):
        hdr = struct.unpack(self.__headerFormat, headerData)
        self.__header = {}
        self.__header['magic'] = hdr[0]
        self.__header['headerVersion'] = hdr[1]
        self.__header['imageMode'] = hdr[2]
        self.__header['frameNumber'] = hdr[3]
        self.__header['width'] = hdr[4]
        self.__header['height'] = hdr[5]
        self.__header['endianness'] = hdr[6]
        self.__header['headerSize'] = hdr[7]
        self.__header['padding'] = hdr[7:]
        
        self.dtype = self.__dtypeID[self.__header['imageMode']]

    ## provides the data shape
    # \returns the data shape if data was loaded
    def shape(self):
        if self.__header:
            return [self.__header['width'],self.__header['height']]
        


    ## provides the decoded data
    # \returns the decoded data if data was loaded
    def decode(self):        
        if not self.__header or not self.__data:
            return
        if not self.__value:
            image = self.__data[1][struct.calcsize(self.__headerFormat):]
            format = self.__formatID[self.__header['imageMode']]
            fSize = struct.calcsize(format)
            self.__value = numpy.array(
                struct.unpack(format*(len(image)/fSize), image), dtype=self.dtype
                ).reshape(self.__header['width'],self.__header['height'])
        return self.__value




## Decoder pool
class DecoderPool(object):        


    ## constructor
    # \brief It creates know decoders    
    # \param configJSON string with decoders    
    def __init__(self, configJSON = None):
        self.__knowDecoders = { "LIMA_VIDEO_IMAGE":VDEOdecoder, "UTF8":UTF8decoder , "UINT32":UINT32decoder } 
        self.__pool = {}

        self.__createDecoders()
        self.__appendUserDecoders(configJSON)


    ## loads user decoders
    # \param configJSON string with decoders    
    def __appendUserDecoders(self, configJSON):
        if configJSON and 'decoders' in configJSON.keys() and  hasattr(configJSON['decoders'],'keys'):
            for dk in configJSON['decoders'].keys():
                pkl = configJSON['decoders'][dk].split(".")
                dec =  __import__(".".join(pkl[:-1]), globals(), locals(), pkl[-1])  
                self.append(getattr(dec, pkl[-1]), dk)
            

    ## creates know decoders
    # \brief It calls constructor of know decoders    
    def __createDecoders(self):
        for dk in self.__knowDecoders.keys():
            self.__pool[dk] = self.__knowDecoders[dk]()


            
    ## checks it the decoder is registered        
    # \param decoder the given decoder
    # \returns True if it the decoder is registered        
    def hasDecoder(self, decoder):
        return True if decoder in self.__pool.keys() else False


    ## checks it the decoder is registered        
    # \param decoder the given decoder
    # \returns True if it the decoder is registered        
    def get(self, decoder):
        if decoder in self.__pool.keys():
            return self.__pool[decoder]

    
    ## adds additional decoder
    # \param name name of the adding decoder
    # \param decoder instance of the adding decoder
    # \returns name of decoder
    def append(self, decoder, name):
        instance = decoder()  
        self.__pool[name] = instance

        if not hasattr(instance,"load") or not hasattr(instance,"name") \
                or not hasattr(instance,"shape") or not hasattr(instance,"decode") \
                or not hasattr(instance,"dtype") or not hasattr(instance,"format"):
            self.pop(name)
            return 
        return name


    ## adds additional decoder
    # \param name name of the adding decoder
    def pop(self, name):
        self.__pool.pop(name, None)

        
