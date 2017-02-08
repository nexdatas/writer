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

""" Provides h5py file writer """

from . import FileWriter


import h5py


def open_file(filename, readonly=False):
    """ open the new file
    """
    if readonly:
        return H5PYFile(h5py.File(filename, "r"))
    else:
        return H5PYFile(h5py.File(filename, "r+"))
        


def create_file(filename, overwrite=False):
    """ create a new file
    """
    if overwrite:
        return H5PYFile(h5py.File(filename, "a"))
    else:
        return H5PYFile(h5py.File(filename, "w"))


def link(target, parent, name):
    """ create link
    """
    return H5PYLink(nx.link(target, parent._h5object, name))


def deflate_filter():
    return H5PYDeflate(nx.deflate_filter())


class H5PYObject(FileWriter.FTObject):
    """ file tree object
    """
    def __init__(self, h5object):
        self._h5object = h5object
        self.path = ''
        self.name = None
        elif hasattr(h5object, "name"):
            self.name = h5object.name

    @property
    def gobject(self):
        return self._h5object


class H5PYAttribute(H5PYObject):
    """ file tree attribute
    """

    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)

    def close(self):
        return self._h5object.close()

    def read(self):
        return self._h5object.read()

    def write(self, o):
        return self._h5object.write(o)

    def __setitem__(self, t, o):
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        return self._h5object.__getitem__(t)

    @property
    def is_valid(self):
        return self._h5object.is_valid

    @property
    def dtype(self):
        return self._h5object.dtype

    @property
    def shape(self):
        return self._h5object.shape

    @property
    def size(self):
        return self._h5object.size

    @property
    def filename(self):
        return self._h5object.filename

    @property
    def parent(self):
        return H5PYGroup(self._h5object.parent)


class H5PYGroup(H5PYObject):
    """ file tree group
    """
    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)

    def open(self, n):
        itm = self._h5object.open(n)
        if isinstance(itm, nx.nxfield):
            return H5PYField(itm)
        elif isinstance(itm, nx.nxgroup):
            return H5PYGroup(itm)
        elif isinstance(itm, nx.nxattribute):
            return H5PYAttribute(itm)
        elif isinstance(itm, nx.nxlink):
            return H5PYLink(itm)
        else:
            return H5PYObject(itm)

    def create_group(self, n, nxclass=""):
        return H5PYGroup(self._h5object.create_group(n, nxclass))

    def create_field(self, name, type_code,
                     shape=None, chunk=None, filter=None):
        return H5PYField(
            self._h5object.create_field(
                name, type_code, shape, chunk,
                filter if not filter else filter._h5object))

    @property
    def parent(self):
        return H5PYGroup(self._h5object.parent)

    @property
    def attributes(self):
        return H5PYAttributeManager(self._h5object.attributes)

    def close(self):
        return self._h5object.close()

    def exists(self):
        return self._h5object.exists()

    @property
    def filename(self):
        return self._h5object.filename


class H5PYField(H5PYObject):
    """ file tree file
    """
    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)

    @property
    def attributes(self):
        return H5PYAttributeManager(self._h5object.attributes)

    def close(self):
        return self._h5object.close()

    def grow(self, dim=0, ext=1):
        return self._h5object.grow(dim, ext)

    def read(self):
        return self._h5object.read()

    def write(self, o):
        return self._h5object.write(o)

    def __setitem__(self, t, o):
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        return self._h5object.__getitem__(t)

    @property
    def is_valid(self):
        return self._h5object.is_valid

    @property
    def dtype(self):
        return self._h5object.dtype

    @property
    def shape(self):
        return self._h5object.shape

    @property
    def size(self):
        return self._h5object.size

    @property
    def filename(self):
        return self._h5object.filename

    @property
    def parent(self):
        return H5PYGroup(self._h5object.parent)


class H5PYFile(H5PYObject):
    """ file tree file
    """

    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)
        self.path = ''

    def root(self):
        return H5PYGroup(self._h5object)

    def flush(self):
        return self._h5object.flush()

    def close(self):
        return self._h5object.close()

    @property
    def is_valid(self):
        return self._h5object.is_valid

    @property
    def readonly(self):
        return self._h5object.readonly


class H5PYLink(H5PYObject):
    """ file tree link
    """
    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)

    @property
    def is_valid(self):
        return self._h5object.is_valid

    @property
    def filename(self):
        return self._h5object.filename

    @property
    def target_path(self):
        return self._h5object.target_path

    @property
    def status(self):
        return self._h5object.status

    @property
    def type(self):
        return self._h5object.type

    @property
    def parent(self):
        return H5PYGroup(self._h5object.parent)


class H5PYDeflate(H5PYObject):
    """ file tree deflate
    """
    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)

    @property
    def rate(self):
        return self._h5object.rate

    @rate.setter
    def rate(self, value):
        self._h5object.rate = value

    @property
    def shuffle(self):
        return self._h5object.shuffle

    @shuffle.setter
    def shuffle(self, value):
        self._h5object.shuffle = value


class H5PYAttributeManager(H5PYObject):
    """ file tree attribute
    """
    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)

    def create(self, name, type, shape=[], overwrite=False):
        return H5PYAttribute(
            self._h5object.create(
                name, type, shape, overwrite))

    def __len__(self):
        return self._h5object.__len__()

    def __setitem__(self, t, o):
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        return self._h5object.__getitem__(t)


#: attribute class
nxobject = H5PYObject
#: attribute class
nxattribute = H5PYAttribute
#: field class
nxfield = H5PYField
#: file class
nxfile = H5PYFile
#: group class
nxgroup = H5PYGroup
#: link class
nxlink = H5PYLink
#: nxsdeflate class
nxdeflate = H5PYDeflate
