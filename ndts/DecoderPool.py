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


## LIMA VDEO decoder
class VDEOdecoder(object):

    ## constructor
    # \brief It clears the local variables
    def __init__(self):
        self._value = None
        self._data = None
        self.name = "VDEO"

    ## loads encoded data
    # \param data encoded data    
    def load(self, data):
        self._data = data
        self._value = None

    ## provides the data shape
    # \returns the data shape if data was loaded
    def shape(self):
        pass

    ## provides the decoded data
    # \returns the decoded data if data was loaded
    def decode(self):        
        if self._value:
            return self._value



## Data source creator
class DecoderPool(object):        

    ## constructor
    # \brief It creates know decoders    
    def __init__(self):
        self._knowDecoders={"VDEO":VDEOdecoder}
        self._pool = {}
        self._createDecoders()

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

    
    ## adds additional decoder
    # \param name name of the adding decoder
    # \param decoder instance of the adding decoder
    # \returns name of decoder
    def append(self, decoder, name = None):
        if not hasattr(decoder,"load") or not hasattr(decoder,"name") \
                or not hasattr(decoder,"shape") or not hasattr(decoder,"decode"):
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

        
