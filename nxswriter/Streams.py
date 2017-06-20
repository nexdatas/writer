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

#: stream lock
__streamlock = threading.Lock()

#: streams for different ids
__streamids = {}

class StreamCollection(object):

    def __init__(self, server):
        
        #: (:class:`PyTango.log4tango.TangoStream`) Tango fatal log stream
        self.log_fatal = None
        #: (:class:`PyTango.log4tango.TangoStream`) Tango error log stream
        self.log_error = None
        #: (:class:`PyTango.log4tango.TangoStream`) Tango warn log stream
        self.log_warn = None
        #: (:class:`PyTango.log4tango.TangoStream`) Tango info log stream
        self.log_info = None
        #: (:class:`PyTango.log4tango.TangoStream`) Tango debug log stream
        self.log_debug = None
        #: (:obj:`set <:obj:`str` >`) if tango server
        self.available = set()
        if hasattr(server, "log_fatal"):
            self.log_fatal = server.log_fatal
            self.available.add("log_fatal")
        if hasattr(server, "log_error"):
            self.log_error = server.log_error
            self.available.add("log_fatal")
        if hasattr(server, "log_warn"):
            self.log_warn = server.log_warn
            self.available.add("log_fatal")
        if hasattr(server, "log_info"):
            self.log_info = server.log_info
            self.available.add("log_fatal")
        if hasattr(server, "log_debug"):
            self.available.add("log_debug")
            self.log_debug = server.log_debug
        


def setstreams(server):
    """ sets log streams

    :param server: Tango server
    :type server: :class:`PyTango.Device_4Impl`
    """
    with __streamlock:
        if sid not in __streamids:
            __streamids[sid]

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
