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

import pytz
import time
import h5py
import datetime


def open_file(filename, readonly=False):
    """ open the new file

    :param filename: file name
    :type filename: :obj:`str`
    :param readonly: readonly flag
    :type readonly: :obj:`bool`
    :returns: file object
    :rtype : :class:`H5PYFile`
    """
    if readonly:
        return H5PYFile(h5py.File(filename, "r"))
    else:
        return H5PYFile(h5py.File(filename, "r+"))


def create_file(filename, overwrite=False):
    """ create a new file

    :param filename: file name
    :type filename: :obj:`str`
    :param overwrite: overwrite flag
    :type overwrite: :obj:`bool`
    :returns: file object
    :rtype : :class:`H5PYFile`
    """
    fl = h5py.File(filename, "a" if overwrite else "w")
    fl.attrs.create("file_time", currenttime() + "\0")
    fl.attrs.create("HDF5_version", "\0")
    fl.attrs.create("NX_class", "NXroot" + "\0")
    fl.attrs.create("NeXus_version", "4.3.0\0")
    fl.attrs.create("file_name", filename + "\0")
    fl.attrs.create("file_update_time", currenttime() + "\0")
    return H5PYFile(fl)


def link(target, parent, name):
    """ create link

    :param target: file name
    :type target: :obj:`str`
    :param parent: parent object
    :type parent: :class:`FTObject`
    :param name: link name
    :type name: :obj:`str`
    :returns: link object
    :rtype : :class:`H5PYLink`
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
    """ create deflate filter

    :returns: deflate filter object
    :rtype : :class:`H5PYDeflate`
    """
    return H5PYDeflate(None)


def currenttime():
    """ returns current time string

    :returns: current time
    :rtype: :obj:`str`
    """
    tzone = time.tzname[0]
    tz = pytz.timezone(tzone)
    fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
    starttime = tz.localize(datetime.datetime.now())
    return str(starttime.strftime(fmt))


class H5PYAttribute(FileWriter.FTAttribute):
    """ file tree attribute
    """

    def __init__(self, h5object, tparent):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTAttribute.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]
        self.name = h5object[1]

    def close(self):
        """ close attribute
        """

    def read(self):
        """ read attribute value

        :returns: python object
        :rtype: :obj:`any`
        """
        return self._h5object[self.name]

    def write(self, o):
        """ write attribute value

        :param o: python object
        :type o: :obj:`any`
        """
        self._h5object[self.name] = o

    def __setitem__(self, t, o):
        """ write attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: python object
        :type o: :obj:`any`
        """
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        """ read attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :returns: python object
        :rtype: :obj:`any`
        """
        return self._h5object.__getitem__(t)

    @property
    def is_valid(self):
        """ check if attribute is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self.name in self._h5object

    @property
    def dtype(self):
        """ attribute data type

        :returns: attribute data type
        :rtype: :obj:`str`
        """
        return type(self._h5object[self._name]).__name__

    @property
    def shape(self):
        """ attribute shape

        :returns: attribute shape
        :rtype: :obj:`list` < :obj:`int` >
        """
        if hasattr(self._h5object[self._name], "shape"):
            return list(self._h5object[self._name].shape)
        else:
            return []


class H5PYGroup(FileWriter.FTGroup):
    """ file tree group
    """
    def __init__(self, h5object, tparent):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTGroup.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    def open(self, name):
        """ open a file tree element

        :param name: element name
        :type name: :obj:`str`
        :returns: file tree object
        :rtype : :class:`FTObject`
        """
        try:
            itm = self._h5object[n]
        except:
            _ = self._h5object.attrs[n]
            return H5PYAttribute((self._h5object.attrs, n), self)

        if isinstance(itm, h5py._hl.dataset.Dataset):
            return H5PYField(itm, self)
        elif isinstance(itm, h5py._hl.group.Group):
            return H5PYGroup(itm, self)
        elif (isinstance(itm, h5py._hl.group.SoftLink)
              or isinstance(itm, h5py._hl.group.ExternalLink)):
            return H5PYLink(itm, self)
        else:
            return H5PYObject(itm, self)

    def create_group(self, n, nxclass=""):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param nxclass: group type
        :type nxclass: :obj:`str`
        :returns: file tree group
        :rtype : :class:`H5PYGroup`
        """
        grp = self._h5object.create_group(n)
        grp.attrs["NX_class"] = nxclass
        return H5PYGroup(grp, self)

    def create_field(self, name, type_code,
                     shape=None, chunk=None, filter=None):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param type_code: nexus field type
        :type type_code: :obj:`str`
        :param shape: shape
        :type shape: :obj:`list` < :obj:`int` >
        :param chunk: chunk
        :type chunk: :obj:`list` < :obj:`int` >
        :param filter: filter deflater
        :type filter: :class:`H5PYDeflate`
        :returns: file tree field
        :rtype : :class:`H5PYField`
        """
        return H5PYField(
            self._h5object.create_field(
                name, type_code, shape, chunk,
                filter if not filter else filter._h5object), self)

    @property
    def parent(self):
        """ return the parent object

        :returns: file tree group
        :rtype : :class:`H5PYGroup`
        """
        return H5PYGroup(self._h5object.parent,
                         self._tparent.getparent())

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype : :class:`H5PYAttributeManager`
        """
        return H5PYAttributeManager(self._h5object.attrs, self)

    def close(self):
        """ close group
        """
        return self._h5object.close()

    def exists(self, name):
        """ if child exists

        :param name: child name
        :type name: :obj:`str`
        :returns: existing flag
        :rtype: :obj:`bool`
        """
        return name in self._h5object


class H5PYField(FileWriter.FTField):
    """ file tree file
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTField.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype : :class:`H5PYAttributeManager`
        """
        return H5PYAttributeManager(self._h5object.attrs, self)

    def close(self):
        """ close field
        """
        return self._h5object.close()

    def grow(self, dim=0, ext=1):
        """ grow the field

        :param dim: growing dimension
        :type dim: :obj:`int`
        :param dim: size of the grow
        :type dim: :obj:`int`
        """
        return self._h5object.grow(dim, ext)

    def read(self):
        """ read the field value

        :returns: pni object
        :rtype: :obj:`any`
        """
        return self._h5object.read()

    def write(self, o):
        """ write the field value

        :param o: pni object
        :type o: :obj:`any`
        """
        return self._h5object.write(o)

    def __setitem__(self, t, o):
        """ set value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: pni object
        :type o: :obj:`any`
        """
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        """ get value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :returns: pni object
        :rtype: :obj:`any`
        """
        return self._h5object.__getitem__(t)

    @property
    def is_valid(self):
        """ check if field is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.is_valid

    @property
    def dtype(self):
        """ field data type

        :returns: field data type
        :rtype: :obj:`str`
        """
        return self._h5object.dtype

    @property
    def shape(self):
        """ field shape

        :returns: field shape
        :rtype: :obj:`list` < :obj:`int` >
        """
        return self._h5object.shape

    @property
    def size(self):
        """ field size

        :returns: field size
        :rtype: :obj:`int`
        """
        return self._h5object.size

    @property
    def filename(self):
        """ file name

        :returns: file name
        :rtype: :obj:`str`
        """
        return self._h5object.filename

    @property
    def parent(self):
        """ parent object

        :returns: parent object
        :rtype: :class:`FTObject`
        """
        return H5PYGroup(self._h5object.parent,
                         self._tparent.getparent())


class H5PYFile(FileWriter.FTFile):
    """ file tree file
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTFile.__init__(self, h5object, tparent)
        self.path = ''
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    def root(self):
        """ root object

        :returns: parent object
        :rtype: :class:`H5PYGroup `
        """
        return H5PYGroup(self._h5object, self)

    def flush(self):
        """ flash the data
        """
        if self._h5object.mode in ["r+"]:
            self._h5object.attrs.create(
                "file_update_time", currenttime() + "\0")
        return self._h5object.flush()

    def close(self):
        """ close file
        """
        if self._h5object.mode in ["r+"]:
            self._h5object.attrs.create(
                "file_update_time", currenttime() + "\0")
        return self._h5object.close()

    @property
    def is_valid(self):
        """ check if file is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.is_valid

    @property
    def readonly(self):
        """ check if file is readonly

        :returns: readonly flag
        :rtype: :obj:`bool`
        """
        return self._h5object.readonly


class H5PYLink(FileWriter.FTLink):
    """ file tree link
    """
    def __init__(self, h5object, tparent):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTLink.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    @property
    def is_valid(self):
        """ check if link is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        try:
            w = self._h5object
            return True
        except:
            return False

    @property
    def filename(self):
        """ file name

        :returns: file name
        :rtype: :obj:`str`
        """
        if hasattr(self._h5object, "filename"):
            return self._h5object.filename
        else:
            return ""

    @property
    def target_path(self):
        """ target path

        :returns: target path
        :rtype: :obj:`str`
        """
        return self._h5object._path

    @property
    def parent(self):
        """ parent object

        :returns: parent object
        :rtype: :class:`FTObject`
        """
        return H5PYGroup(self._h5object.parent,
                         self._tparent.getparent())


class H5PYDeflate(FileWriter.FTDeflate):
    """ file tree deflate
    """
    def __init__(self, h5object, tparent):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTDeflate.__init__(self, h5object, tparent)
        #: (:obj:`bool`) compression shuffle
        self.shuffle = False
        #: (:obj:`int`) compression rate
        self.rate = 2
        #: (:obj:`str`) object nexus path
        self.path = ''
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]


class H5PYAttributeManager(FileWriter.FTAttributeManager):
    """ file tree attribute
    """
    def __init__(self, h5object):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTAttributeManager.__init__(self, h5object)
        #: (:obj:`str`) object nexus path
        self.path = ''
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    def create(self, name, type, shape=[], overwrite=False):
        """ create a new attribute

        :param name: attribute name
        :type name: :obj:`str`
        :param shape: attribute shape
        :type shape: :obj:`list` < :obj:`int` >
        :param overwrite: overwrite flag
        :type overwrite: :obj:`bool`
        :returns: attribute object
        :rtype : :class:`H5PYAtribute`
        """
        return H5PYAttribute(
            self._h5object.create(
                name, type, shape, overwrite), self)

    def __len__(self):
        """ number of attributes

        :returns: number of attributes
        :rtype: :obj:`int`
        """
        return self._h5object.__len__()

    def __setitem__(self, t, o):
        """ set value

        :param name: attribute name
        :type name: :obj:`str`
        :param o: pni object
        :type o: :obj:`any`
        """
        return self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        """ get value

        :param name: attribute name
        :type name: :obj:`str`
        :returns: attribute object
        :rtype : :class:`FTAtribute`
        """
        return self._h5object.__getitem__(t)
