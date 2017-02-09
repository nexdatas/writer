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

""" Provides abstraction for file writer """

#: writer module
writer = None


def open_file(filename, readonly=False):
    """ open the new file

    :param filename: file name 
    :type filename: :obj:`str`
    :param readonly: readonly flag
    :type readonly: :obj:`bool`
    :returns: file object
    :rtype : :class:`FTObject`
    """
    return writer.open_file(filename, readonly)


def create_file(filename, overwrite=False):
    """ create a new file

    :param filename: file name 
    :type filename: :obj:`str`
    :param overwrite: overwrite flag
    :type overwrite: :obj:`bool`
    :returns: file object
    :rtype : :class:`FTObject`
    """
    return writer.create_file(filename, overwrite)


def link(target, parent, name):
    """ create link

    :param target: file name 
    :type target: :obj:`str`
    :param parent: parent object
    :type parent: :class:`FTObject`
    :param name: link name 
    :type name: :obj:`str`
    :returns: link object
    :rtype : :class:`FTObject`
    """
    return writer.link(target, parent, name)


def deflate_filter():
    """ create deflate filter

    :returns: deflate filter object
    :rtype : :class:`FTObject`
    """
    return writer.deflate_filter()


class FTObject(object):
    """ file tree object
    """
