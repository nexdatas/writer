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
    if ":/" in target:
        filename, path = target.slit(":/")
        parent._h5object[name] = h5py.ExternalLink(filename, path)
        return H5PYLink(
            parent._h5object.get(name, getlink=True), parent)
    else:
        parent._h5object[name] = h5py.SoftLink(target) 
        return H5PYLink(
            parent._h5object.get(name, getlink=True), parent)


def deflate_filter():
    return H5PYDeflate(None)



class H5PYAttribute(H5PYObject):
    """ file tree attribute
    """

    def __init__(self, h5object, tparent):
        FileWriter.FTAttribute.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]
        self.name = h5object[1]
        
    def close(self):
        pass

    def read(self):
        return self._h5object[self.name] 

    def write(self, o):
        self._h5object[self.name] = o

    def __setitem__(self, t, o):
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        return self._h5object.__getitem__(t)

    @property
    def is_valid(self):
        return self.name in self._h5object

    @property
    def dtype(self):
        return  type(self._h5object[self._name]).__name__

    @property
    def shape(self):
        if hasattr(self._h5object[self._name], "shape"):
            return  list(self._h5object[self._name].shape)
        else:
            return []

#    @property
#    def parent(self):
#        return H5PYGroup(self._h5object.parent)


class H5PYGroup(H5PYObject):
    """ file tree group
    """
    def __init__(self, h5object, tparent):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        H5PYObject.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    def open(self, n):
        try:
            itm = self._h5object[n]
        except:
            _ = self._h5object.attrs[n]
            return H5PYAttribute((self._h5object.attrs, n), self)
            
        if isinstance(itm, h5py._hl.dataset.Dataset):
            return H5PYField(itm, self)
        elif isinstance(itm, h5py._hl.group.Group):
            return H5PYGroup(itm, self)
        elif isinstance(itm, h5py._hl.group.SoftLink) or \
        isinstance(itm, h5py._hl.group.ExternalLink):
            return H5PYLink(itm, self)
        else:
            return H5PYObject(itm, self)

    def create_group(self, n, nxclass=""):
        grp = self._h5object.create_group(n)
        grp.attrs["NX_class"] = nxclass
        return H5PYGroup(grp, self)

    def create_field(self, name, type_code,
                     shape=None, chunk=None, filter=None):
        return H5PYField(
            self._h5object.create_field(
                name, type_code, shape, chunk,
                filter if not filter else filter._h5object), self)

    @property
    def parent(self):
        return H5PYGroup(self._h5object.parent,
                        self._tparent.getparent())

    @property
    def attributes(self):
        return H5PYAttributeManager(self._h5object.attrs, self)

    def close(self):
        return self._h5object.close()

    def exists(self, name):
        return name in self._h5object


class H5PYField(H5PYObject):
    """ file tree file
    """
    def __init__(self, h5object, tparent=None):
        H5PYObject.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    @property
    def attributes(self):
        return H5PYAttributeManager(self._h5object.attrs, self)

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
        return H5PYGroup(self._h5object.parent,
                        self._tparent.getparent())


class H5PYFile(H5PYObject):
    """ file tree file
    """

    def __init__(self, h5object, tparent=None):
        H5PYObject.__init__(self, h5object, tparent)
        self.path = ''
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    def root(self):
        return H5PYGroup(self._h5object, self)

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
    def __init__(self, h5object, tparent):
        H5PYObject.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    @property
    def is_valid(self):
        try:
            w = self._h5object
            return True
        except:
            return False

    @property
    def filename(self):
        if hasattr(self._h5object, "filename"):
            return self._h5object.filename
        else:
            return ""

    @property
    def target_path(self):
        return self._h5object._path

    @property
    def parent(self):
        return H5PYGroup(self._h5object.parent,
                        self._tparent.getparent())


class H5PYDeflate(H5PYObject):
    """ file tree deflate
    """
    def __init__(self, h5object, tparent):
        H5PYObject.__init__(self, h5object, tparent)
        self.shuffle = False
        self.rate = 2
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]


class H5PYAttributeManager(H5PYObject):
    """ file tree attribute
    """
    def __init__(self, h5object):
        H5PYObject.__init__(self, h5object)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    def create(self, name, type, shape=[], overwrite=False):
        return H5PYAttribute(
            self._h5object.create(
                name, type, shape, overwrite), self)

    def __len__(self):
        return self._h5object.__len__()

    def __setitem__(self, t, o):
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        return self._h5object.__getitem__(t)


