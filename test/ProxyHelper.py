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
# \package test nexdatas
# \file ProxyTools.py
# unittests for field Tags running Tango Server
#

import PyTango
import time

# test fixture


class ProxyHelper(object):
    # waiting for running server
    # \proxy server proxy
    # \proxy counts number of counts
    # \proxy sec time interval between two counts

    @classmethod
    def wait(cls, proxy, counts=-1, sec=0.01):
        found = False
        cnt = 0
        while not found and cnt != counts:
            try:
                if proxy.state() != PyTango.DevState.RUNNING:
                    found = True
            except Exception as e:
                print(e)
                found = False
                raise
            if cnt:
                time.sleep(sec)
            cnt += 1
        return found
