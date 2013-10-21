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
## \file DataSources.py
# data-source types

""" Definitions of various datasources """

import time
import sys
import threading
from xml.dom import minidom

from .Types import NTP
from . import Streams

from .DataHolder import DataHolder
from .Errors import (PackageError, DataSourceSetupError)





## Data source
class DataSource(object):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        pass


    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        pass


    ## access to data
    # \brief It is an abstract method providing data   
    def getData(self):
        pass


    ## checks if the data is valid
    # \returns if the data is valid
    def isValid(self):
        return True



    ## self-description 
    # \returns self-describing string
    def __str__(self):
        return "unknown DataSource"


    ## provides xml content of the node
    # \param node DOM node
    # \returns xml content string
    @classmethod
    def _getText(cls, node):
        xml = node.toxml() 
        start = xml.find('>')
        end = xml.rfind('<')
        if start == -1 or end < start:
            return ""
        return xml[start + 1:end].replace("&lt;","<").\
            replace("&gt;",">").replace("&quot;","\"").\
            replace("&amp;","&")


