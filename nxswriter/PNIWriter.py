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

""" Provides pni file writer """

from .FileWriter import (
    FileWriter, FTObject, FTAttribute, FTGroup, FTFile, FTLink, FTRoot, FTDeflate)

import pni.io.nx.h5 as nx

class PNIWriter(object):
    """ PNI Writer abstraction
    """
    def __init__(self, writer):
        """ constructor
        """

    
        #: attribute class
        self.nxobject = PNIObject
        #: attribute class
        self.nxattribute = PNIAttribute
        #: field class
        self.nxfield = PNIField
        #: file class
        self.nxfile = PNIFile
        #: group class
        self.nxgroup = PNIGroup
        #: link class
        self.nxlink = PNILink
        #: root class
        self.nxroot = PNIRoot
        #: nxsdeflate class
        self.nxdeflate = PNIDeflate

    def open_file(self, filename, overwrite=False):
        """ open the new file
        """
        return PNIFile(nx.open_file(filename, overwrite))
        
    def deflate_filter(self):
        """ create deflate filter
        """
        return PNIDeflate(nx.deflate_filter())

    def create_file(self, filename, overwrite=False):
        """ create a new file
        """
        return PNIFile(nx.open_create(filename, overwrite))

    def link(self, target, parent, name):
        """ create link
        """
        return PNILink(nx.link(target, parent, name))

class PNIObject(FTObject):
    """ file tree object
    """

    
class PNIAttribute(FTObject):    
    """ file tree attribute
    """

    
class PNIGroup(FTObject):    
    """ file tree group
    """

    
class PNIFile(FTObject):    
    """ file tree file
    """

    
class PNILink(FTObject):    
    """ file tree link
    """

class PNIRoot(FTObject):    
    """ file tree root
    """
    
class PNIDeflate(FTObject):    
    """ file tree deflate
    """

