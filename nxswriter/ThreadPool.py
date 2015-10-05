#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2015 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxswriter nexdatas
## \file ThreadPool.py
# Thread Pool class

""" Provides a pool with element threads """

from __future__ import print_function

import Queue
import sys

from . import Streams
from .ElementThread import ElementThread
from .Errors import ThreadError


## Pool with threads
class ThreadPool(object):
    ## constructor
    # \brief It cleans the member variables
    def __init__(self, numberOfThreads=None):
        ## maximal number of threads
        self.numberOfThreads = numberOfThreads if numberOfThreads >= 1 else -1
        ## queue of the appended elements
        self.__elementQueue = Queue.Queue()
        ## list of the appended elements
        self.__elementList = []
        ## list of the threads related to the appended elements
        self.__threadList = []

    ## appends the thread element
    # \param elem the thread element
    def append(self, elem):
        self.__elementList.append(elem)

    ## sets the JSON string to threads
    # \param globalJSON the static JSON string
    # \param localJSON the dynamic JSON string
    # \returns self object
    def setJSON(self, globalJSON, localJSON=None):
        for el in self.__elementList:
            if hasattr(el.source, "setJSON") and callable(el.source.setJSON):
                el.source.setJSON(globalJSON, localJSON)
        return self

    ## runner
    # \brief It runs the threads from the pool
    def run(self):
        self.__threadList = []
        self.__elementQueue = Queue.Queue()

        for eth in self.__elementList:
            self.__elementQueue.put(eth)

        if self.numberOfThreads < 1:
            self.numberOfThreads = len(self.__elementList)

        for i in range(min(self.numberOfThreads, len(self.__elementList))):
            th = ElementThread(i, self.__elementQueue)
            self.__threadList.append(th)
            th.start()

    ## waits for all thread from the pool
    # \param timeout the maximal waiting time
    def join(self, timeout=None):
        for th in self.__threadList:
            if th.isAlive():
                th.join(timeout)

    ## runner with waiting
    # \brief It runs and waits the threads from the pool
    def runAndWait(self):
        self.run()
        self.join()

    ## checks errors from threads
    def checkErrors(self):
        errors = []
        for el in self.__elementList:
            if el.error:
                mess = "ThreadPool::checkErrors() - %s" % str(el.error) 
                if hasattr(el, "canfail") and el.canfail:
                    if Streams.warn_stream:
                        Streams.warn_stream(mess)
                        
                    else:
                        print(mess, file=sys.stderr)
                    if hasattr(el, "markFailed"):
                        el.markFailed()
                else:
                    errors.append(el.error)
                    if Streams.log_error:
                        print(mess, file=Streams.log_error)
        if errors:
            raise ThreadError("Problems in storing data: %s" % str(errors))

    ## closer
    # \brief It close the threads from the pool
    def close(self):
        for el in self.__elementList:
            if hasattr(el.h5Object, "close"):
                el.h5Object.close()
        self.__threadList = []
        self.__elementList = []
        self.__elementQueue = None
