#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
#
#    Foobar is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
"""@package docstring
@file ThreadPool.py
"""

from threading import *                                                                      
from ElementThread import *


class ThreadPool:
    """ Pool of Threads """
    def __init__(self):
        """ Constructor """
        self.elementList=[]
        self.threadList=[]

    def append(self,elem):
        self.elementList.append(elem)
        pass

    def run(self):
        self.threadList=[]
        
        for eth in self.elementList:
            th=ElementThread(eth)
            th.start()
            self.threadList.append(th)
            print "running ", th.name

    def join(self,timeout=None):
        for th in self.threadList:
            if th.isAlive():
                th.join()

    def runAndWait(self):
        self.run()
        self.join()

    def close(self):
        for el in self.elementList:
            el.fObject.close()
        self.threadList=[]
        
