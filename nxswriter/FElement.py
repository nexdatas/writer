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

""" Definitions of file tag evaluation classes """

import numpy

from .DataHolder import DataHolder
from .Element import Element
from .Types import NTP
from .Errors import (XMLSettingSyntaxError)
from . import Streams


class FElement(Element):
    """ NeXuS runnable tag element
    tag element corresponding to one of H5 objects
    """

    def __init__(self, name, attrs, last, h5object=None):
        """ constructor

        :param name: tag name
        :type name: :obj: `str`
        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param h5object: H5 file object
        :type h5object: :class:`nxswriter.FileWriter.FTObject`
        """
        Element.__init__(self, name, attrs, last)
        #: (:class:`nxswriter.FileWriter.FTObject`) stored H5 file object
        self.h5Object = h5object
        #: (:class:`nxswriter.DataSources.DataSource`) data source
        self.source = None
        #: (:obj:`str`) notification of error in the run method
        self.error = None
        #: (:obj:`bool`) flag for devices for which is allowed to failed
        self.canfail = False
        #: (:obj:`bool`) scalar type
        self._scalar = False

    def run(self):
        """ runner

        :brief: During its thread run it fetches the data from the source
        """
        if self.source:
            self.source.getData()

    @classmethod
    def _reshape(cls, dsShape, rank, extends, extraD, exDim):
        """ recalculates shape

        :param dsShape: origin shape of the object
        :type dsShape: :obj:`list` <:obj:`int` >
        :param rank: rank of the object
        :type rank: : obj:`str` or obj:`int`
        :param extends: If True extends the shape up to rank value
        :type extends: :obj:`bool`
        :param exDim: grows growing dimension + 1
        :type exDim: :obj:`int`
        :param extraD: True if the object grows
        :type extraD: :obj:`bool`
        :returns: shape of the  h5 field
        :rtype: :obj:`list` <:obj:`int` >

        """
        shape = []
        if dsShape:
            for s in dsShape:
                if s and extends:
                    shape.append(s)
                elif not extends and s and s > 0:
                    shape.append(s)

            while extends and len(shape) < int(rank):
                shape.append(0)
            if extraD:
                shape.insert(exDim - 1, 0)
        return shape

    @classmethod
    def __fetchShape(cls, value, rank):
        """ fetches shape from value and rank

        :param rank: rank of the object
        :type rank: : obj:`str` or obj:`int`
        :param value: value of the object
        :type value: : obj:`str`
        :returns: shape of the value
        :rtype: :obj:`list` <:obj:`int` >
        """
        if not rank or int(rank) == 0:
            return [1]
        elif int(rank) == 1:
            spec = value.split()
            return [len(spec)]
        elif int(rank) == 2:
            lines = value.split("\n")
            image = [ln.split() for ln in lines]
            return [len(image), len(image[0])]
        else:
            Streams.error(
                "FElement::__fetchShape() "
                "- Case with not supported rank = %s" % rank,
                std=False)

            raise XMLSettingSyntaxError(
                "Case with not supported rank = %s" % rank)

    @classmethod
    def _getExtra(cls, grows, extraD=False):
        """ provides growing dimension

        :param grows: growing dimension
        :type grows: :obj:`int`
        :param extraD: True if the object grows
        :type extraD: :obj:`bool`
        :returns: growing dimension
        :rtype: :obj:`int`
        """
        if extraD:
            if grows and grows > 1:
                exDim = grows
            else:
                exDim = 1
        else:
            exDim = 0
        return exDim

    def _findShape(self, rank, lengths=None, extraD=False,
                   grows=None, extends=False, checkData=False):
        """ creates shape object from rank and lengths variables
            raises XMLSettingSyntaxError: if shape cannot be found


        :param rank: rank of the object
        :type rank: :obj:`str`
        :param lengths: dictionary with dimensions as a string data ,
                        e.g. {"1":"34","2":"40"}
        :type lengths:  :obj:`dict` <:obj:`str`, :obj:`str`>
        :param extraD: if the object grows
        :type extraD: :obj:`bool`
        :param grows: growing dimension
        :type grows: :obj:`int`
        :param extends: If True extends the shape up to rank value
        :type extends: :obj:`bool`
        :returns shape: of the object
        :rtype: :obj:`list` <:obj:`int` >
        """
        self._scalar = False
        shape = []
        exDim = self._getExtra(grows, extraD)
        if int(rank) > 0:
            try:
                for i in range(int(rank)):
                    si = str(i + 1)
                    if lengths and si in lengths.keys() \
                            and lengths[si] is not None:
                        if int(lengths[si]) > 0:
                            shape.append(int(lengths[si]))
                    else:
                        raise XMLSettingSyntaxError("Dimensions not defined")
                if len(shape) < int(rank):
                    raise XMLSettingSyntaxError("Too small dimension number")

                if extraD:
                    shape.insert(exDim - 1, 0)
            except:
                val = ("".join(self.content)).strip().encode()
                found = False
                if checkData and self.source and self.source.isValid():
                    data = self.source.getData()
                    if isinstance(data, dict):
                        dh = DataHolder(**data)
                        shape = self._reshape(dh.shape, rank, extends,
                                              extraD, exDim)
                        if shape is not None:
                            found = True

                if val and not found:
                    shape = self.__fetchShape(val, rank)
                    if shape is not None:
                        found = True

                if not found:
                    nm = "unnamed"
                    if "name" in self._tagAttrs.keys():
                        nm = self._tagAttrs["name"] + " "
                    raise XMLSettingSyntaxError(
                        "Wrongly defined %s shape: %s" %
                        (nm, str(self.source) if self.source else val))

        elif extraD:
            shape = [0]

        if shape == []:
            self._scalar = True
        return shape

    def setMessage(self, exceptionMessage=None):
        """ creates the error message

        :param exceptionMessage: additional message of exception
        :type  exceptionMessage: :obj:`str`
        :returns: error message
        :rtype: :obj:`str`
        """
        if hasattr(self.h5Object, "path"):
            name = self.h5Object.path
        elif hasattr(self.h5Object, "name"):
            name = self.h5Object.name
        else:
            name = "unnamed object"
        if self.source:
            dsource = str(self.source)
        else:
            dsource = "unknown datasource"

        message = ("Data for %s not found. DATASOURCE:%s"
                   % (name, dsource), exceptionMessage)
        return message


class FElementWithAttr(FElement):
    """ NeXuS runnable tag element with attributes
        tag element corresponding to one of H5 objects with attributes
    """

    def __init__(self, name, attrs, last, h5object=None):
        """ constructor

        :param name: tag name
        :type name: :obj:`str`
        :param attrs: dictionary of the tag attributes
        :type attrs: :obj:`dict` <:obj:`str`, :obj:`str`>
        :param last: the last element from the stack
        :type last: :class:`nxswriter.Element.Element`
        :param h5object: H5 file object
        :type h5object: :class:`nxswriter.FileWriter.FTObject`
        """

        FElement.__init__(self, name, attrs, last, h5object)
        #: (:obj:`dict` <:obj:`str`, (:obj:`str`, :obj:`str`, :obj:`tuple`)>  \
        #:     or :obj:`dict` <:obj:`str`, (:obj:`str`, :obj:`str`) > ) \
        #:     dictionary with attribures from sepatare attribute tags
        #:     written as (name, value, shape)
        self.tagAttributes = {}
        #: (:obj:`dict` <:obj:`str`, h5object>) h5 instances
        self.__h5Instances = {}

    @classmethod
    def _setValue(cls, rank, val):
        """ creates DataHolder with given rank and value

        :param rank: data rank
        :type rank: :obj:`int`
        :param val: data value
        :type value: any
        :returns: data holder
        :rtype: :class:`nxswriter.DataHolder.DataHolder`
        """
        dh = None
        if not rank or rank == 0:
            dh = DataHolder("SCALAR", val, "DevString", [1, 0])
        elif rank == 1:
            spec = val.split()
            dh = DataHolder("SPECTRUM", spec, "DevString",
                            [len(spec), 0])
        elif rank == 2:
            lines = val.split("\n")
            image = [ln.split() for ln in lines]
            dh = DataHolder("IMAGE", image, "DevString",
                            [len(image), len(image[0])])
        else:
            Streams.error(
                "FElement::_createAttributes() - "
                "Case with not supported rank = %s" % rank,
                std=False)

            raise XMLSettingSyntaxError(
                "Case with not supported rank = %s", rank)
        return dh

    def _createAttributes(self):
        """ creates h5 attributes

        :brief: It creates attributes instances which have been
                stored in tagAttributes dictionary
        """
        for key in self.tagAttributes.keys():
            if key not in ["name", "type"]:
                if len(self.tagAttributes[key]) < 3:
                    if key.encode() not in self.__h5Instances:
                        self.__h5Instances[key.encode()] \
                            = self.h5Object.attributes.create(
                                key.encode(),
                                NTP.nTnp[self.tagAttributes[key][0]].encode())
                    dh = DataHolder(
                        "SCALAR", self.tagAttributes[key][1].strip().encode(),
                        "DevString", [1, 0])
                    self.__h5Instances[key.encode()][...] = \
                        dh.cast(self.__h5Instances[key.encode()].dtype)
                else:
                    shape = self.tagAttributes[key][2]
                    if key.encode() not in self.__h5Instances:
                        self.__h5Instances[key.encode()] \
                            = self.h5Object.attributes.create(
                                key.encode(),
                                NTP.nTnp[self.tagAttributes[key][0]].encode(),
                                shape)
                    val = self.tagAttributes[key][1].strip().encode()
                    if val:
                        rank = len(shape)
                        hsp = self.__h5Instances[key.encode()].shape
                        if hsp and set(hsp) == set([1]) and \
                           self.__h5Instances[key.encode()].dtype == 'string':
                            dh = self._setValue(0, val)
                        else:
                            dh = self._setValue(rank, val)
                        self.__h5Instances[key.encode()][...] = dh.cast(
                            self.__h5Instances[key.encode()].dtype)

    def _setAttributes(self, excluded=None):
        """ creates attributes

        :brief: It creates attributes in h5Object

        :param excluded: names of excluded attributes
        :type excluded: :obj:`list` <:obj:`str`>
        """
        excluded = excluded or []
        for key in self._tagAttrs.keys():
            if key not in excluded:
                if key in NTP.aTn.keys():
                    h5att = self.h5Object.attributes.create(
                        key.encode(),
                        NTP.nTnp[NTP.aTn[key]].encode(),
                        overwrite=True
                    )
                    if hasattr(self._tagAttrs[key], "encode"):
                        try:
                            h5att[...] = NTP.convert[
                                str(self.h5Object.attributes[
                                    key.encode()].dtype)
                            ](self._tagAttrs[key].strip().encode())
                        except:
                            h5att[...] = self._tagAttrs[key].strip().encode()
                    else:
                        try:
                            h5att[...] = NTP.convert[
                                str(self.h5Object.attributes[
                                    key.encode()].dtype)
                            ](self._tagAttrs[key])
                        except:
                            h5att[...] = self._tagAttrs[key]

                elif key in NTP.aTnv.keys():
                    try:
                        dh = self._setValue(1, self._tagAttrs[key])
                        shape = (dh.shape[0],)
                        self.h5Object.attributes.create(
                            key.encode(),
                            NTP.nTnp[NTP.aTnv[key]].encode(),
                            shape,
                            overwrite=True
                        )[...] = dh.cast(NTP.nTnp[NTP.aTnv[key]].encode())
                    except:
                        sarr = self._tagAttrs[key].split()
                        self.h5Object.attributes.create(
                            key.encode(),
                            NTP.nTnp[NTP.aTnv[key]].encode(),
                            (len(sarr),),
                            overwrite=True
                        )[...] = numpy.array(sarr)
                else:
                    self.h5Object.attributes.create(
                        key.encode(), "string", overwrite=True)[...] \
                        = self._tagAttrs[key].strip().encode()

    def h5Attribute(self, name):
        """ provides attribute h5 object

        :param name: attribute name
        :type name: :obj:`str`
        :returns: instance of the attribute object if created
        :rtype: :class:`nxswriter.FileWriter.FTObject`
        """
        return self.__h5Instances.get(name)
