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

""" labels to Tango Streams """

import sys
import threading

#: (:class:`PyTango.log4tango.TangoStream`) Tango fatal log stream
log_fatal = None
#: (:class:`PyTango.log4tango.TangoStream`) Tango error log stream
log_error = None
#: (:class:`PyTango.log4tango.TangoStream`) Tango warn log stream
log_warn = None
#: (:class:`PyTango.log4tango.TangoStream`) Tango info log stream
log_info = None
#: (:class:`PyTango.log4tango.TangoStream`) Tango debug log stream
log_debug = None

streamlock = threading.Lock()

def setstreams(server):
    """ sets log streams

    :param server: Tango server
    :type server: :class:`PyTango.Device_4Impl`
    """
    with streamlock:
        if hasattr(self.__server, "log_fatal"):
            Streams.log_fatal = server.log_fatal
        if hasattr(self.__server, "log_error"):
            Streams.log_error = server.log_error
        if hasattr(self.__server, "log_warn"):
            Streams.log_warn = server.log_warn
        if hasattr(self.__server, "log_info"):
            Streams.log_info = server.log_info
        if hasattr(self.__server, "log_debug"):
            Streams.log_debug = server.log_debug
    

def fatal(message, std=True):
    """ writes fatal error message

    :param message: error message
    :type message: :obj:`str`
    :param std: True if it writes to sys stream
                when log stream does not exist
    :type std: :obj:`bool`
    """
    if log_fatal:
        try:
            log_fatal.write(message + '\n')
        except:
            sys.stderr.write(message + '\n')
    elif std:
        sys.stderr.write(message + '\n')


def error(message, std=True):
    """ writes error message

    :param message: error message
    :type message: :obj:`str`
    :param std: True if it writes to sys stream
                when log stream does not exist
    :type std: :obj:`bool`
   """
    if log_error:
        try:
            log_error.write(message + '\n')
        except:
            sys.stderr.write(message + '\n')
    elif std:
        sys.stderr.write(message + '\n')


def warn(message, std=True):
    """ writes warning message

    :param message: warning message
    :type message: :obj:`str`
    :param std: True if it writes to sys stream
                when log stream does not exist
    :type std: :obj:`bool`
   """
    if log_warn:
        try:
            log_warn.write(message + '\n')
        except:
            sys.stderr.write(message + '\n')
    elif std:
        sys.stderr.write(message + '\n')


def info(message, std=True):
    """ writes info message

    :param message: info message
    :type message: :obj:`str`
    :param std: True if it writes to sys stream
                when log stream does not exist
    :type std: :obj:`bool`
    """
    if log_info:
        try:
            log_info.write(message + '\n')
        except:
            sys.stdout.write(message + '\n')
    elif std:
        sys.stdout.write(message + '\n')


def debug(message, std=True):
    """ writes debug message

    :param message: debug message
    :type message: :obj:`str`
    :param std: True if it writes to sys stream
                when log stream does not exist
    :type std: :obj:`bool`
   """
    if log_debug:
        try:
            log_debug.write(message + '\n')
        except:
            sys.stdout.write(message + '\n')
    elif std:
        sys.stdout.write(message + '\n')
