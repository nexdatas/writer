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


""" Tango Data Writer errors """


class ThreadError(Exception):

    """ exception for problems in thread
    """
    pass


class CorruptedFieldArrayError(Exception):

    """ exception for corrupted FieldArray
    """
    pass


class XMLSettingSyntaxError(Exception):

    """ exception for syntax in XML settings
    """
    pass


class DataSourceError(Exception):

    """ exception for fetching data from data source
    """
    pass


class PackageError(Exception):

    """ exception for fetching data from data source
    """
    pass


class DataSourceSetupError(Exception):

    """ exception for setting data source
    """
    pass


class XMLSyntaxError(Exception):

    """ exception for syntax in XML settings
    """
    pass


class UnsupportedTagError(Exception):

    """ unsupported tag exception
    """
    pass
