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

from . import FileWriter

#from .FileWriter import (
#    FileWriter, FTObject, FTAttribute, FTGroup, FTFile, FTLink, FTRoot, FTDeflate)

import pni.io.nx.h5 as nx




def open_file(filename, overwrite=False):
    """ open the new file
    """
    return PNIFile(nx.open_file(filename, overwrite))

def create_file(filename, overwrite=False):
    """ create a new file
    """
    return PNIFile(nx.open_create(filename, overwrite))

def link(target, parent, name):
    """ create link
    """
    return PNILink(nx.link(target, parent, name))


class PNIObject(FileWriter.FTObject):
    """ file tree object
    """
    def __init__(self, h5object):
        self.__h5object = h5object
        self.path = None
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        elif hasattr(h5object, "name"):
            self.name = h5object.name

class PNIAttribute(PNIObject):
    """ file tree attribute
    """
    
    def close(self):
        return self.__h5object.close()

    def read(self):
        return self.__h5object.read()

    def write(self, o):
        return self.__h5object.write(o)

    def __setitem__(t, o):
        return self.__h5object.__setitem__(t, o)

    def __getitem__(t):
        return self.__h5object.__getitem__(t)

    @property
    def is_valid(self):
        return self.__h5object.is_valid

    @property
    def dtype(self):
        return self.__h5object.dtype

    @property
    def shape(self):
        return self.__h5object.shape
    
    @property
    def size(self):
        return self.__h5object.size

    @property
    def filename(self):
        return self.__h5object.filename
    
    @property
    def parent(self):
        return PNIGroup(self.__h5object.parent)
    

    
class PNIGroup(PNIObject):
    """ file tree group
    """

    def open(self, n):
        return PNIGroup(self.__h5object.open(n))

    @property
    def attributes(self):
        return PNIAttributeManager(self.__h5object.attributes)


class PNIField(PNIObject):
    """ file tree file
    """
    @property
    def attributes(self):
        return PNIAttributeManager(self.__h5object.attributes)

    def close(self):
        return self.__h5object.close()

    def grows(self, dim=0, ext=1):
        return self.__h5object.grows(dim, ext)

    def read(self):
        return self.__h5object.read()

    def write(self, o):
        return self.__h5object.write(o)

    def __setitem__(t, o):
        return self.__h5object.__setitem__(t, o)

    def __getitem__(t):
        return self.__h5object.__getitem__(t)

    @property
    def is_valid(self):
        return self.__h5object.is_valid

    @property
    def dtype(self):
        return self.__h5object.dtype

    @property
    def shape(self):
        return self.__h5object.shape
    
    @property
    def size(self):
        return self.__h5object.size

    @property
    def filename(self):
        return self.__h5object.filename
    
    @property
    def parent(self):
        return PNIGroup(self.__h5object.parent)
    
    
class PNIFile(PNIObject):
    """ file tree file
    """


    def root(self):
        pass

    def flush(self):
        pass

    def close(self):
        pass

    @property
    def is_valid(self):
        return self.__h5object.is_valid

    @property
    def readonly(self):
        return self.__h5object.readonly


class PNILink(PNIObject):
    """ file tree link
    """
    @property
    def is_valid(self):
        return self.__h5object.is_valid

    @property
    def filename(self):
        return self.__h5object.filename
    
    @property
    def target_path(self):
        return self.__h5object.target_path

    @property
    def status(self):
        return self.__h5object.status

    @property
    def type(self):
        return self.__h5object.type
    
    @property
    def parent(self):
        return PNIGroup(self.__h5object.parent)


class PNIRoot(PNIObject):
    """ file tree root
    """


class PNIDeflate(PNIObject):
    """ file tree deflate
    """

class PNIAttributeManager(PNIObject):
    """ file tree attribute
    """

#: attribute class
nxobject = PNIObject
#: attribute class
nxattribute = PNIAttribute
#: field class
nxfield = PNIField
#: file class
nxfile = PNIFile
#: group class
nxgroup = PNIGroup
#: link class
nxlink = PNILink
#: root class
nxroot = PNIRoot
#: nxsdeflate class
nxdeflate = PNIDeflate
#: nxsdeflate class
deflate_filter = PNIDeflate
