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

class FileWriter(object):
    """ File Writer abstraction
    """

    def __init__(self, writer):
        """ constructor
        """
        self.writer = writer()

        #: object class
        self.nxobject = None
        #: attribute class
        self.nxattribute = None
        #: field class
        self.nxfield = None
        #: file class
        self.nxfile = None
        #: group class
        self.nxgroup = None
        #: link class
        self.nxlink = None
        #: root class
        self.nxroot = None
        #: nxsdeflate class
        self.nxdeflate = None


    def open_file(self, filename, overwrite=False):
        """ open the new file
        """

    def deflate_filter(self):
        """ create deflate filter
        """

    def create_file(self, filename, overwrite=False):
        """ create a new file
        """

    def link(self, target, parent, name):
        """ create link
        """

class FTObject(object):
    """ file tree object
    """


class FTAttribute(FTObject):
    """ file tree attribute
    """


class FTGroup(FTObject):
    """ file tree group
    """


class FTFile(FTObject):
    """ file tree file
    """


class FTLink(FTObject):
    """ file tree link
    """

class FTRoot(FTObject):
    """ file tree root
    """

class FTDeflate(FTObject):
    """ file tree deflate
    """
