#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

""" Provides a pool with element threads """

import Queue

from . import Streams
from .ElementThread import ElementThread
from .Errors import ThreadError


class ThreadPool(object):
    """ Pool with threads
    """

    def __init__(self, numberOfThreads=None):
        """ constructor

        :brief: It cleans the member variables
        :param numerOfThreads: number of threads
        """

        #: maximal number of threads
        self.numberOfThreads = numberOfThreads if numberOfThreads >= 1 else -1
        #: queue of the appended elements
        self.__elementQueue = Queue.Queue()
        #: list of the appended elements
        self.__elementList = []
        #: list of the threads related to the appended elements
        self.__threadList = []

    def append(self, elem):
        """ appends the thread element
        :param elem: the thread element
        """
        self.__elementList.append(elem)

    def setJSON(self, globalJSON, localJSON=None):
        """ sets the JSON string to threads
        :param globalJSON: the static JSON string
        :param localJSON: the dynamic JSON string
        :returns: self object
        """

        for el in self.__elementList:
            if hasattr(el.source, "setJSON") and callable(el.source.setJSON):
                el.source.setJSON(globalJSON, localJSON)
        return self

    def run(self):
        """ thread runner

        :brief: It runs the threads from the pool
        """

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

    def join(self, timeout=None):
        """ waits for all thread from the pool
        :param timeout: the maximal waiting time
        """

        for th in self.__threadList:
            if th.isAlive():
                th.join(timeout)

    def runAndWait(self):
        """ runner with waiting

        :brief: It runs and waits the threads from the pool
        """

        self.run()
        self.join()

    def checkErrors(self):
        """ checks errors from threads
        """

        errors = []
        for el in self.__elementList:
            if el.error:
                mess = "ThreadPool::checkErrors() - %s" % str(el.error)
                if hasattr(el, "canfail") and el.canfail:
                    if hasattr(el, "markFailed"):
                        el.markFailed()
                    Streams.warn(mess)
                else:
                    errors.append(el.error)
                    Streams.error(mess, std=False)
        if errors:
            raise ThreadError("Problems in storing data: %s" % str(errors))

    def close(self):
        """ closer

        :brief: It close the threads from the pool
        """

        for el in self.__elementList:
            if hasattr(el.h5Object, "close"):
                el.h5Object.close()
        self.__threadList = []
        self.__elementList = []
        self.__elementQueue = None
