#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""@package docstring
@file DataHolder.py
"""
                         
import numpy

class DataHolder:
    """ A holder for passing data """
    def __init__(self,dFormat,dValue,dType,dShape):
        """ Constructor """
        self.format=dFormat
        self.value=dValue
        self.type=dType
        self.shape=dShape
    def array(self):
        if str(self.format).split('.')[-1] == "SPECTRUM":
            return numpy.array(self.value)
        if str(self.format).split('.')[-1] == "IMAGE":
            return numpy.array(self.value)


