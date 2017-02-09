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


import pni.io.nx.h5 as nx


def open_file(filename, readonly=False):
    """ open the new file

    :param filename: file name 
    :type filename: :obj:`str`
    :param readonly: readonly flag
    :type readonly: :obj:`bool`
    :returns: file object
    :rtype : :class:`PNIFile`
    """
    return PNIFile(nx.open_file(filename, readonly))


def create_file(filename, overwrite=False):
    """ create a new file

    :param filename: file name 
    :type filename: :obj:`str`
    :param overwrite: overwrite flag
    :type overwrite: :obj:`bool`
    :returns: file object
    :rtype : :class:`PNIFile`
    """
    return PNIFile(nx.create_file(filename, overwrite))


def link(target, parent, name):
    """ create link

    :param target: file name 
    :type target: :obj:`str`
    :param parent: parent object
    :type parent: :class:`FTObject`
    :param name: link name 
    :type name: :obj:`str`
    :returns: link object
    :rtype : :class:`PNILink`
    """
    return PNILink(nx.link(target, parent._h5object, name))


def deflate_filter():
    """ create deflate filter

    :returns: deflate filter object
    :rtype : :class:`PNIDeflate`
    """
    return PNIDeflate(nx.deflate_filter())


class PNIObject(FileWriter.FTObject):
    """ file tree object
    """
    
    def __init__(self, h5object):
        """ constructor

        :param h5object: pni object
        :type h5object: :class:`pni.io.nx.h5.nxfield` or \
                        :class:`pni.io.nx.h5.nxgroup` or \
                        :class:`pni.io.nx.h5.nxlink` or \
                        :class:`pni.io.nx.h5.nxattribute` or \
                        :class:`pni.io.nx.h5.nxfile`
        """

        #: (:class:`pni.io.nx.h5.nxfield` or \
        #  :class:`pni.io.nx.h5.nxgroup` or \
        #  :class:`pni.io.nx.h5.nxlink` or \
        #  :class:`pni.io.nx.h5.nxattribute` or \
        #  :class:`pni.io.nx.h5.nxfile`) stored H5 file object
        self._h5object = h5object
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    @property
    def gobject(self):
        """ get method for pni gobject property

        :returns: pni object
        :rtype h5object: :class:`pni.io.nx.h5.nxfield` or \
                        :class:`pni.io.nx.h5.nxgroup` or \
                        :class:`pni.io.nx.h5.nxlink` or \
                        :class:`pni.io.nx.h5.nxattribute` or \
                        :class:`pni.io.nx.h5.nxfile`
        """
        
        return self._h5object


class PNIAttribute(PNIObject):
    """ file tree attribute
    """

    def __init__(self, h5object):
        PNIObject.__init__(self, h5object)

    def close(self):
        self._h5object.close()

    def read(self):
        return self._h5object.read()

    def write(self, o):
        self._h5object.write(o)

    def __setitem__(self, t, o):
        self._h5object.__setitem__(t, o)

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


class PNIGroup(PNIObject):
    """ file tree group
    """
    def __init__(self, h5object):
        PNIObject.__init__(self, h5object)

    def open(self, n):
        itm = self._h5object.open(n)
        if isinstance(itm, nx.nxfield):
            return PNIField(itm)
        elif isinstance(itm, nx.nxgroup):
            return PNIGroup(itm)
        elif isinstance(itm, nx.nxattribute):
            return PNIAttribute(itm)
        elif isinstance(itm, nx.nxlink):
            return PNILink(itm)
        else:
            return PNIObject(itm)

    def create_group(self, n, nxclass=""):
        return PNIGroup(self._h5object.create_group(n, nxclass))

    def create_field(self, name, type_code,
                     shape=None, chunk=None, filter=None):
        return PNIField(
            self._h5object.create_field(
                name, type_code, shape, chunk,
                filter if not filter else filter._h5object))

    @property
    def parent(self):
        return PNIGroup(self._h5object.parent)

    @property
    def attributes(self):
        return PNIAttributeManager(self._h5object.attributes)

    def close(self):
        self._h5object.close()

    def exists(self, name):
        return self._h5object.exists(name)



class PNIField(PNIObject):
    """ file tree file
    """
    def __init__(self, h5object):
        PNIObject.__init__(self, h5object)

    @property
    def attributes(self):
        return PNIAttributeManager(self._h5object.attributes)

    def close(self):
        self._h5object.close()

    def grow(self, dim=0, ext=1):
        self._h5object.grow(dim, ext)

    def read(self):
        return self._h5object.read()

    def write(self, o):
        self._h5object.write(o)

    def __setitem__(self, t, o):
        self._h5object.__setitem__(t, o)

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
        return PNIGroup(self._h5object.parent)


class PNIFile(PNIObject):
    """ file tree file
    """

    def __init__(self, h5object):
        PNIObject.__init__(self, h5object)

    def root(self):
        return PNIGroup(self._h5object.root())

    def flush(self):
        self._h5object.flush()

    def close(self):
        self._h5object.close()

    @property
    def is_valid(self):
        return self._h5object.is_valid

    @property
    def readonly(self):
        return self._h5object.readonly


class PNILink(PNIObject):
    """ file tree link
    """
    def __init__(self, h5object):
        PNIObject.__init__(self, h5object)

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
    def parent(self):
        return PNIGroup(self._h5object.parent)


class PNIDeflate(PNIObject):
    """ file tree deflate
    """
    def __init__(self, h5object):
        PNIObject.__init__(self, h5object)

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


class PNIAttributeManager(PNIObject):
    """ file tree attribute
    """
    def __init__(self, h5object):
        PNIObject.__init__(self, h5object)

    def create(self, name, type, shape=[], overwrite=False):
        return PNIAttribute(
            self._h5object.create(
                name, type, shape, overwrite))

    def __len__(self):
        return self._h5object.__len__()

    def __setitem__(self, t, o):
        self._h5object.__setitem__(t, o)

    def __getitem__(self, t):
        return self._h5object.__getitem__(t)


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
#: nxsdeflate class
nxdeflate = PNIDeflate
