#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package ndts nexdatas
## \file Errors.py
# Error classes


## exception for problems in thread
class ThreadError(Exception): pass


## exception for corrupted FieldArray
class CorruptedFieldArrayError(Exception): pass


## exception for syntax in XML settings
class XMLSettingSyntaxError(Exception): pass

## exception for fetching data from data source
class DataSourceError(Exception): pass


## exception for fetching data from data source
class PackageError(Exception): pass

## exception for setting data source
class DataSourceSetupError(Exception): pass


## exception for syntax in XML settings
class XMLSyntaxError(Exception): pass

## unsupported tag exception
class UnsupportedTagError(Exception): pass

## exception for problems in thread
class ThreadError(Exception): pass
