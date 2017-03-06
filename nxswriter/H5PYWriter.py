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

import pytz
import time
import h5py
import datetime
import numpy as np
import os

from . import FileWriter


def open_file(filename, readonly=False, **pars):
    """ open the new file

    :param filename: file name
    :type filename: :obj:`str`
    :param readonly: readonly flag
    :type readonly: :obj:`bool`
    :param pars: parameters
    :type pars: :obj:`dict` < :obj:`str`, :obj:`str`>
    :returns: file object
    :rtype: :class:`H5PYFile`
    """
    if readonly:
        return H5PYFile(h5py.File(filename, "r", **pars), filename)
    else:
        return H5PYFile(h5py.File(filename, "r+", **pars), filename)


def create_file(filename, overwrite=False, **pars):
    """ create a new file

    :param filename: file name
    :type filename: :obj:`str`
    :param overwrite: overwrite flag
    :type overwrite: :obj:`bool`
    :param pars: parameters
    :type pars: :obj:`dict` < :obj:`str`, :obj:`str`>
    :returns: file object
    :rtype: :class:`H5PYFile`
    """
    fl = h5py.File(filename, "a" if overwrite else "w-", **pars)
    fl.attrs.create("file_time", H5PYFile.currenttime() + "\0")
    fl.attrs.create("HDF5_version", "\0")
    fl.attrs.create("NX_class", "NXroot" + "\0")
    fl.attrs.create("NeXus_version", "4.3.0\0")
    fl.attrs.create("file_name", filename + "\0")
    fl.attrs.create("file_update_time", H5PYFile.currenttime() + "\0")
    return H5PYFile(fl, filename)


def link(target, parent, name):
    """ create link

    :param target: file name
    :type target: :obj:`str`
    :param parent: parent object
    :type parent: :class:`FTObject`
    :param name: link name
    :type name: :obj:`str`
    :returns: link object
    :rtype: :class:`H5PYLink`
    """
    localfname = H5PYLink.getfilename(parent)
    if ":/" in target:
        filename, path = target.split(":/")

        if os.path.abspath(filename) != os.path.abspath(localfname):
            parent.h5object[name] = h5py.ExternalLink(filename, path)
        else:
            parent.h5object[name] = h5py.SoftLink(path)

    else:
        parent.h5object[name] = h5py.SoftLink(target)
    return H5PYLink(
        parent.h5object.get(name, getlink=True), parent).setname(name)


def deflate_filter():
    """ create deflate filter

    :returns: deflate filter object
    :rtype: :class:`H5PYDeflate`
    """
    return H5PYDeflate()


class H5PYFile(FileWriter.FTFile):
    """ file tree file
    """

    def __init__(self, h5object, filename):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param filename:  file name
        :type filename: :obj:`str`
        """
        FileWriter.FTFile.__init__(self, h5object, filename)
        #: (:obj:`str`) object nexus path
        self.path = None

    def root(self):
        """ root object

        :returns: parent object
        :rtype: :class:`H5PYGroup`
        """
        g = H5PYGroup(self._h5object, self)
        g.name = "/"
        g.path = "/"
        return g

    def flush(self):
        """ flash the data
        """
        if self._h5object.mode in ["r+"]:
            self._h5object.attrs.create(
                "file_update_time", self.currenttime() + "\0")
        return self._h5object.flush()

    def close(self):
        """ close file
        """
        FileWriter.FTFile.close(self)
        if self._h5object.mode in ["r+"]:
            self._h5object.attrs.create(
                "file_update_time", self.currenttime() + "\0")
        return self._h5object.close()

    @classmethod
    def currenttime(cls):
        """ returns current time string

        :returns: current time
        :rtype: :obj:`str`
        """
        tzone = time.tzname[0]
        tz = pytz.timezone(tzone)
        fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
        starttime = tz.localize(datetime.datetime.now())
        return str(starttime.strftime(fmt))

    @property
    def is_valid(self):
        """ check if group is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self._h5object.name is not None

    @property
    def readonly(self):
        """ check if file is readonly

        :returns: readonly flag
        :rtype: :obj:`bool`
        """
        isvalid = self.is_valid
        return self._h5object.mode in ["r"] if isvalid else None

    def reopen(self, readonly=False, swmr=False, libver=None):
        """ reopen file

        :param readonly: readonly flag
        :type readonly: :obj:`bool`
        :param swmr: swmr flag
        :type swmr: :obj:`bool`
        :param libver:  library version, default: 'latest'
        :type libver: :obj:`str`
        """
        libver = libver or 'latest'
        isvalid = self.is_valid
        lreadonly = self._h5object.mode in ["r"] if isvalid else None

        if (not isvalid or lreadonly != readonly or
           self._h5object.libver != libver):
            if isvalid:
                self.close()
            self._h5object = h5py.File(
                self.name, "r" if readonly else "r+", libver=libver)
            FileWriter.FTFile.reopen(self)
        if hasattr(self._h5object, "swmr_mode") and swmr:
            self._h5object.swmr_mode = swmr
        if swmr:
            raise Exception("SWMR not supported")


class H5PYGroup(FileWriter.FTGroup):
    """ file tree group
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTGroup.__init__(self, h5object, tparent)
        self.path = ""
        self.name = None
        if hasattr(h5object, "name"):
            name = h5object.name
            self.name = name.split("/")[-1]
            if tparent and tparent.path:
                if tparent.path == "/":
                    self.path = "/" + self.name
                else:
                    self.path = tparent.path + "/" + self.name
            if ":" not in self.name:
                if "NX_class" in h5object.attrs:
                    clss = h5object.attrs["NX_class"]
                else:
                    clss = ""
                if clss:
                    self.path += ":" + clss

    def open(self, name):
        """ open a file tree element

        :param name: element name
        :type name: :obj:`str`
        :returns: file tree object
        :rtype: :class:`FTObject`
        """
        if name not in self._h5object:
            _ = self._h5object.attrs[name]
            return H5PYAttribute((self._h5object.attrs, name), self)

        itm = self._h5object.get(name)
        if isinstance(itm, h5py._hl.dataset.Dataset):
            el = H5PYField(itm, self)
        elif isinstance(itm, h5py._hl.group.Group):
            el = H5PYGroup(itm, self)
        else:
            itm = self._h5object.get(name, getlink=True)
            el = H5PYLink(itm, self).setname(name)
        return el

    class H5PYGroupIter(object):

        def __init__(self, group):
            """ constructor

            :param group: group object
            :type manager: :obj:`H5PYGroup`
            """

            self.__group = group
            self.__names = self.__group._h5object.keys() or []

        def next(self):
            """ the next attribute

            :returns: attribute object
            :rtype: :class:`FTAtribute`
            """
            if self.__names:
                return self.__group.open(self.__names.pop(0))
            else:
                raise StopIteration()

        def __iter__(self):
            """ attribute iterator

            :returns: attribute iterator
            :rtype: :class:`H5PYAttrIter`
            """
            return self

    def __iter__(self):
        """ attribute iterator

        :returns: attribute iterator
        :rtype: :class:`H5PYAttrIter`
        """
        return self.H5PYGroupIter(self)

    def close(self):
        """ close group
        """
        FileWriter.FTGroup.close(self)
        self._h5object = None

    def create_group(self, n, nxclass=""):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param nxclass: group type
        :type nxclass: :obj:`str`
        :returns: file tree group
        :rtype: :class:`H5PYGroup`
        """
        grp = self._h5object.create_group(n)
        if nxclass:
            grp.attrs["NX_class"] = nxclass
        return H5PYGroup(grp, self)

    def create_field(self, name, type_code,
                     shape=None, chunk=None, dfilter=None):
        """ open a file tree element

        :param n: group name
        :type n: :obj:`str`
        :param type_code: nexus field type
        :type type_code: :obj:`str`
        :param shape: shape
        :type shape: :obj:`list` < :obj:`int` >
        :param chunk: chunk
        :type chunk: :obj:`list` < :obj:`int` >
        :param dfilter: filter deflater
        :type dfilter: :class:`H5PYDeflate`
        :returns: file tree field
        :rtype: :class:`H5PYField`
        """
        shape = shape or [1]
        mshape = [None for _ in shape] or (None,)
        if type_code == "string":
            type_code = h5py.special_dtype(vlen=unicode)
            # type_code = h5py.special_dtype(vlen=bytes)
        if dfilter:
            f = H5PYField(
                self._h5object.create_dataset(
                    name, shape, type_code,
                    chunks=(tuple(chunk)
                            if chunk is not None else None),
                    compression="gzip",
                    compression_opts=dfilter.rate,
                    shuffle=dfilter.shuffle, maxshape=mshape
                ),
                self)
        else:
            f = H5PYField(
                self._h5object.create_dataset(
                    name, shape, type_code,
                    chunks=(tuple(chunk)
                            if chunk is not None else None),
                    maxshape=mshape
                ),
                self)
        return f

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype: :class:`H5PYAttributeManager`
        """
        return H5PYAttributeManager(self._h5object.attrs, self)

    @property
    def size(self):
        """ group size

        :returns: group size
        :rtype: :obj:`int`
        """
        return len(self._h5object.keys())

    def exists(self, name):
        """ if child exists

        :param name: child name
        :type name: :obj:`str`
        :returns: existing flag
        :rtype: :obj:`bool`
        """
        return name in self._h5object

    @property
    def is_valid(self):
        """ check if group is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        try:
            return self._h5object.name is not None
        except:
            return False

    def reopen(self):
        """ reopen file
        """
        if isinstance(self._tparent, H5PYFile):
            self._h5object = self._tparent.h5object
        else:
            self._h5object = self._tparent.h5object.get(self.name)
        FileWriter.FTGroup.reopen(self)


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
            name = h5object.name
            self.name = name.split("/")[-1]
            if tparent and tparent.path:
                if tparent.path == "/":
                    self.path = "/" + self.name
                else:
                    self.path = tparent.path + "/" + self.name

    @property
    def attributes(self):
        """ return the attribute manager

        :returns: attribute manager
        :rtype: :class:`H5PYAttributeManager`
        """
        return H5PYAttributeManager(self._h5object.attrs, self)

    def reopen(self):
        """ reopen field
        """
        self._h5object = self._tparent.h5object.get(self.name)
        FileWriter.FTField.reopen(self)

    def grow(self, dim=0, ext=1):
        """ grow the field

        :param dim: growing dimension
        :type dim: :obj:`int`
        :param dim: size of the grow
        :type dim: :obj:`int`
        """
        shape = list(self._h5object.shape)
        shape[dim] += ext
        return self._h5object.resize(shape)

    def read(self):
        """ read the field value

        :returns: pni object
        :rtype: :obj:`any`
        """
        return self._h5object[...]

    def write(self, o):
        """ write the field value

        :param o: pni object
        :type o: :obj:`any`
        """
        self._h5object[...] = o

    def __setitem__(self, t, o):
        """ set value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: pni object
        :type o: :obj:`any`
        """
        if isinstance(o, np.ndarray):
            hsh = self._h5object.shape
            if t is Ellipsis:
                tsz = [i for i in range(len(hsh))]
            else:
                tsz = [i for (i, s) in enumerate(t) if isinstance(s, slice)]
            osz = len(o.shape)
            if len(tsz) > osz and len(hsh) > max(tsz):
                shape = tuple([hsh[e] for e in tsz])
                o = o.reshape(shape)
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
        """ check if group is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        try:
            return self._h5object.name is not None
        except:
            return False

    def close(self):
        """ close field
        """
        FileWriter.FTField.close(self)
        self._h5object = None

    @property
    def dtype(self):
        """ field data type

        :returns: field data type
        :rtype: :obj:`str`
        """

        if self._h5object.dtype.kind == 'O':
            return "string"

        return str(self._h5object.dtype)

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


class H5PYLink(FileWriter.FTLink):
    """ file tree link
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTLink.__init__(self, h5object, tparent)
        self.path = ''
        self.name = None
        if tparent and tparent.path:
            self.path = tparent.path
        if not self.path.endswith("/"):
            self.path += "/"

    def setname(self, name):
        self.name = name
        self.path += self.name
        return self

    @property
    def is_valid(self):
        """ check if link is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        try:
            _ = self._h5object
            self.parent.h5object[self.name]
            return True
        except:
            return False

    def read(self):
        """ read object value

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self.parent.h5object[self.name][...]

    @classmethod
    def getfilename(cls, obj):
        filename = ""
        while not filename:
            par = obj.parent
            if par is None:
                break
            if isinstance(par, H5PYFile):
                filename = par.name
                break
            else:
                obj = par
        return filename

    @property
    def target_path(self):
        """ target path

        :returns: target path
        :rtype: :obj:`str`
        """
        filename = self.getfilename(self)
        if filename and ":" not in self._h5object.path:
            return filename + ":/" + "/".join(
                self._h5object.path.split("/"))
        return self._h5object.path

    def reopen(self):
        """ reopen field
        """
        self._h5object = self._tparent.h5object.get(self.name, getlink=True)
        FileWriter.FTLink.reopen(self)

    def close(self):
        """ close group
        """
        FileWriter.FTLink.close(self)
        self._h5object = None


class H5PYDeflate(FileWriter.FTDeflate):
    """ file tree deflate
    """
    def __init__(self):
        """ constructor

        """
        FileWriter.FTDeflate.__init__(self, None)
        #: (:obj:`bool`) compression shuffle
        self._shuffle = False
        #: (:obj:`int`) compression rate
        self._rate = 0

    def __getrate(self):
        """ getter for compression rate

        :returns: compression rate
        :rtype: :obj:`int`
        """
        return self._rate

    def __setrate(self, value):
        """ setter for compression rate

        :param value: compression rate
        :type value: :obj:`int`
        """
        self._rate = value

    #: (:obj:`int`) compression rate
    rate = property(__getrate, __setrate)

    def __getshuffle(self):
        """ getter for compression shuffle

        :returns: compression shuffle
        :rtype: :obj:`bool`
        """
        return self._shuffle

    def __setshuffle(self, value):
        """ setter for compression shuffle

        :param value: compression shuffle
        :type value: :obj:`bool`
        """
        self._shuffle = value

    #: (:obj:`bool`) compression shuffle
    shuffle = property(__getshuffle, __setshuffle)


class H5PYAttributeManager(FileWriter.FTAttributeManager):
    """ file tree attribute
    """
    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTAttributeManager.__init__(self, h5object, tparent)
        #: (:obj:`str`) object nexus path
        self.path = ''
        #: (:obj:`str`) object name
        self.name = None
        if hasattr(h5object, "name"):
            self.path = h5object.name
            self.name = self.path.split("/")[-1]

    def create(self, name, dtype, shape=[], overwrite=False):
        """ create a new attribute

        :param name: attribute name
        :type name: :obj:`str`
        :param dtype: attribute type
        :type dtype: :obj:`str`
        :param shape: attribute shape
        :type shape: :obj:`list` < :obj:`int` >
        :param overwrite: overwrite flag
        :type overwrite: :obj:`bool`
        :returns: attribute object
        :rtype: :class:`H5PYAtribute`
        """

        if not overwrite and name in self.h5object.keys():
            raise Exception("Attribute %s exists" % name)

        if shape:
            if isinstance(shape, list):
                shape = tuple(shape)
            if dtype == 'string':
                dtype = h5py.special_dtype(vlen=bytes)
                self._h5object.create(
                    name, np.empty(shape, dtype=dtype), shape, dtype)
            else:
                self._h5object.create(
                    name, np.zeros(shape, dtype=dtype), shape, dtype)
        else:
            if dtype == "string":
                self._h5object.create(name, "")
            else:
                self._h5object.create(
                    name, np.array(0, dtype=dtype), (1,), dtype)
        at = H5PYAttribute((self._h5object, name), self.parent)
        return at

    def __len__(self):
        """ number of attributes

        :returns: number of attributes
        :rtype: :obj:`int`
        """
        return len(self._h5object.keys())

    class H5PYAttrIter(object):

        def __init__(self, manager):
            """ constructor

            :param manager: attribute manager
            :type manager: :obj:`H5PYAttributeManager`
            """

            self.__manager = manager
            self.__iter = self.__manager._h5object.__iter__()

        def next(self):
            """ the next attribute

            :returns: attribute object
            :rtype: :class:`FTAtribute`
            """
            name = self.__iter.next()
            if name is None:
                return None
            return H5PYAttribute((self.__manager._h5object, name),
                                 self.__manager.parent)

        def __iter__(self):
            """ attribute iterator

            :returns: attribute iterator
            :rtype: :class:`H5PYAttrIter`
            """
            return self

    def __iter__(self):
        """ attribute iterator

        :returns: attribute iterator
        :rtype: :class:`H5PYAttrIter`
        """
        return self.H5PYAttrIter(self)

    def __getitem__(self, name):
        """ get value

        :param name: attribute name
        :type name: :obj:`str`
        :returns: attribute object
        :rtype: :class:`FTAtribute`
        """
        return H5PYAttribute((self._h5object, name), self.parent)

    def reopen(self):
        """ reopen field
        """
        self._h5object = self._tparent.h5object.attrs
        FileWriter.FTAttributeManager.reopen(self)

    def close(self):
        """ close attribure manager
        """
        FileWriter.FTAttributeManager.close(self)

    @property
    def is_valid(self):
        """ check if link is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        return self.parent.is_valid


class H5PYAttribute(FileWriter.FTAttribute):
    """ file tree attribute
    """

    def __init__(self, h5object, tparent=None):
        """ constructor

        :param h5object: pni object
        :type h5object: :obj:`any`
        :param tparent: treee parent
        :type tparent: :obj:`FTObject`
        """
        FileWriter.FTAttribute.__init__(self, h5object, tparent)
        self.name = h5object[1]

        self.path = tparent.path
        self.path += "@%s" % self.name

    def read(self):
        """ read attribute value

        :returns: python object
        :rtype: :obj:`any`
        """
        return self._h5object[0][self.name]

    def write(self, o):
        """ write attribute value

        :param o: python object
        :type o: :obj:`any`
        """
        if isinstance(o, str) and not o.endswith("\0"):
            o += "\0"
        self._h5object[0][self.name] = np.array(o, dtype=self.dtype)

    def __setitem__(self, t, o):
        """ write attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :param o: python object
        :type o: :obj:`any`
        """
        if isinstance(o, str) and not o.endswith("\0"):
            o += "\0"

        if t is Ellipsis or t == slice(None, None, None) or \
           t == (slice(None, None, None), slice(None, None, None)) or \
           (hasattr(o, "__len__") and t == slice(0, len(o), None)):
            self._h5object[0][self.name] = np.array(o, dtype=self.dtype)
        elif isinstance(t, slice):
            var = self._h5object[0][self.name]
            if self.dtype is not 'string':
                var[t] = np.array(o, dtype=self.dtype)
            else:
                if hasattr(var, "tolist"):
                    var = var.tolist()
                var[t] = np.array(o, dtype=self.dtype).tolist()
            self._h5object[0][self.name] = var
        elif isinstance(t, tuple):
            var = self._h5object[0][self.name]
            if self.dtype is not 'string':
                var[t] = np.array(o, dtype=self.dtype)
            else:
                if hasattr(var, "flatten"):
                    vv = var.flatten().tolist() + \
                        np.array(o, dtype=self.dtype).flatten().tolist()
                    nt = np.array(vv, dtype=self.dtype)
                    var = np.array(var, dtype=nt.dtype)
                    var[t] = np.array(o, dtype=self.dtype)
                elif hasattr(var, "tolist"):
                    var = var.tolist()
                    var[t] = np.array(o, dtype=self.dtype).tolist()
                else:
                    var[t] = np.array(o, dtype=self.dtype).tolist()
            self._h5object[0][self.name] = var
        else:
            self._h5object[0][self.name] = np.array(o, dtype=self.dtype)

    def __getitem__(self, t):
        """ read attribute value

        :param t: slice tuple
        :type t: :obj:`tuple`
        :returns: python object
        :rtype: :obj:`any`
        """
        if not isinstance(t, int):
            if t is Ellipsis:
                return self._h5object[0][self.name]
            else:
                return self._h5object[0][self.name][t]
        return self._h5object[0][self.name].__getitem__(t)

    @property
    def is_valid(self):
        """ check if field is valid

        :returns: valid flag
        :rtype: :obj:`bool`
        """
        try:
            return self.name in self._h5object[0].keys()
        except:
            return False

    @property
    def dtype(self):
        """ attribute data type

        :returns: attribute data type
        :rtype: :obj:`str`
        """
        dt = type(self._h5object[0][self.name]).__name__
        if dt == "ndarray":
            dt = str(self._h5object[0][self.name].dtype)
        if dt.endswith("_"):
            dt = dt[:-1]
        if dt == "str":
            dt = "string"
        if dt == "object":
            dt = "string"
        if dt.startswith("|S"):
            dt = "string"
        return dt

    @property
    def shape(self):
        """ attribute shape

        :returns: attribute shape
        :rtype: :obj:`list` < :obj:`int` >
        """
        if hasattr(self._h5object[0][self.name], "shape"):
            return self._h5object[0][self.name].shape or (1,)
        else:
            return (1,)

    def reopen(self):
        """ reopen attribute
        """
        self._h5object = (self._tparent.h5object.attrs, self.name)
        FileWriter.FTAttribute.reopen(self)

    def close(self):
        """ close attribute
        """
        FileWriter.FTAttribute.close(self)
        self._h5object = None