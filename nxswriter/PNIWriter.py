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
    return PNILink(nx.link(target, parent._h5object, name), parent)


def deflate_filter():
    """ create deflate filter

    :returns: deflate filter object
    :rtype : :class:`PNIDeflate`
    """
    return PNIDeflate(nx.deflate_filter())


class PNIAttribute(FileWriter.FTAttribute):
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
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    def close(self):
        """ close attribute
        """
        self._h5object.close()

    def read(self):
        """ read attribute value

        :returns: python object
        :rtype: :obj:`any`
        """
        return self._h5object.read()

    def write(self, o):
        """ write attribute value

        :param o: python object
        :type o: :obj:`any`
        """
        self._h5object.write(o)

    def __setitem__(self, t, o):
        """ write attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: python object
        :type o: :obj:`any`
        """
        self._h5object.__setitem__(t, o)

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
        return self._h5object.is_valid

    @property
    def dtype(self):
        """ attribute data type

        :returns: attribute data type
        :rtype: :obj:`str`
        """
        return self._h5object.dtype

    @property
    def shape(self):
        """ attribute shape

        :returns: attribute shape
        :rtype: :obj:`list` < :obj:`int` >
        """
        return self._h5object.shape


class PNIGroup(FileWriter.FTGroup):
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
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    def open(self, name):
        """ open a file tree element

        :param name: element name
        :type name: :obj:`str`
        :returns: file tree object
        :rtype : :class:`FTObject`
        """
        itm = self._h5object.open(n)
        if isinstance(itm, nx.nxfield):
            return PNIField(itm, self)
        elif isinstance(itm, nx.nxgroup):
            return PNIGroup(itm, self)
        elif isinstance(itm, nx.nxattribute):
            return PNIAttribute(itm, self)
        elif isinstance(itm, nx.nxlink):
            return PNILink(itm, self)
        else:
            return PNIObject(itm, self)

    def create_group(self, n, nxclass=""):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param nxclass: group type
        :type nxclass: :obj:`str`
        :returns: file tree group
        :rtype : :class:`PNIGroup`
        """
        return PNIGroup(self._h5object.create_group(n, nxclass), self)

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
        :type filter: :class:`PNIDeflate`
        :returns: file tree field
        :rtype : :class:`PNIField`
        """
        return PNIField(
            self._h5object.create_field(
                name, type_code, shape, chunk,
                filter if not filter else filter._h5object), self)

    @property
    def parent(self):
        """ return the parent object

        :returns: file tree group
        :rtype : :class:`PNIGroup`
        """
        return PNIGroup(self._h5object.parent,
                        self._tparent.getparent())

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype : :class:`PNIAttributeManager`
        """
        return PNIAttributeManager(self._h5object.attributes, self)

    def close(self):
        """ close group
        """
        self._h5object.close()

    def exists(self, name):
        """ if child exists

        :param name: child name
        :type name: :obj:`str`
        :returns: existing flag
        :rtype: :obj:`bool`
        """
        return self._h5object.exists(name)


class PNIField(FileWriter.FTField):
    """ file tree file
    """
    def __init__(self, h5object, tparent):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTField.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype : :class:`PNIAttributeManager`
        """
        return PNIAttributeManager(self._h5object.attributes, self)

    def close(self):
        """ close field
        """
        self._h5object.close()

    def grow(self, dim=0, ext=1):
        """ grow the field

        :param dim: growing dimension
        :type dim: :obj:`int`
        :param dim: size of the grow
        :type dim: :obj:`int`
        """
        self._h5object.grow(dim, ext)

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
        self._h5object.write(o)

    def __setitem__(self, t, o):
        """ set value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: pni object
        :type o: :obj:`any`
        """
        self._h5object.__setitem__(t, o)

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
        return PNIGroup(self._h5object.parent, self._parent.getparent())


class PNIFile(FileWriter.FTFile):
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
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    def root(self):
        """ root object

        :returns: parent object
        :rtype: :class:`PNIGroup `
        """
        return PNIGroup(self._h5object.root(), self)

    def flush(self):
        """ flash the data
        """
        self._h5object.flush()

    def close(self):
        """ close file
        """
        self._h5object.close()

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


class PNILink(FileWriter.FTLink):
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
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    @property
    def is_valid(self):
        """ check if link is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.is_valid

    @property
    def filename(self):
        """ file name

        :returns: file name
        :rtype: :obj:`str`
        """
        return self._h5object.filename

    @property
    def target_path(self):
        """ target path

        :returns: target path
        :rtype: :obj:`str`
        """
        return self._h5object.target_path

    @property
    def parent(self):
        """ parent object

        :returns: parent object
        :rtype: :class:`FTObject`
        """
        return PNIGroup(self._h5object.parent)


class PNIDeflate(FileWriter.FTDeflate):
    """ file tree deflate
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTDeflate.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    @property
    def rate(self):
        """ getter for compression rate

        :returns: compression rate
        :rtype: :obj:`int`
        """
        return self._h5object.rate

    @rate.setter
    def rate(self, value):
        """ setter for compression rate

        :param value: compression rate
        :type value: :obj:`int`
        """
        self._h5object.rate = value

    @property
    def shuffle(self):
        """ getter for compression shuffle

        :returns: compression shuffle
        :rtype: :obj:`bool`
        """
        return self._h5object.shuffle

    @shuffle.setter
    def shuffle(self, value):
        """ setter for compression shuffle

        :param value: compression shuffle
        :type value: :obj:`bool`
        """
        self._h5object.shuffle = value


class PNIAttributeManager(FileWriter.FTAttributeManager):
    """ file tree attribute
    """
    def __init__(self, h5object, tparent):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTAttributeManager.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = None
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "path"):
            self.path = h5object.path
        if hasattr(h5object, "name"):
            self.name = h5object.name

    def create(self, name, type, shape=[], overwrite=False):
        """ create a new attribute

        :param name: attribute name
        :type name: :obj:`str`
        :param shape: attribute shape
        :type shape: :obj:`list` < :obj:`int` >
        :param overwrite: overwrite flag
        :type overwrite: :obj:`bool`
        :returns: attribute object
        :rtype : :class:`PNIAtribute`
        """
        return PNIAttribute(
            self._h5object.create(
                name, type, shape, overwrite), self.getparent())

    def __len__(self):
        """ number of attributes

        :returns: number of attributes
        :rtype: :obj:`int`
        """
        return self._h5object.__len__()

    def __setitem__(self, name, o):
        """ set value

        :param name: attribute name
        :type name: :obj:`str`
        :param o: pni object
        :type o: :obj:`any`
        """
        self._h5object.__setitem__(name, o)

    def __getitem__(self, name):
        """ get value

        :param name: attribute name
        :type name: :obj:`str`
        :returns: attribute object
        :rtype : :class:`FTAtribute`
        """
        return PNIAttribute(
            self._h5object.__getitem__(name), self.getparent())
