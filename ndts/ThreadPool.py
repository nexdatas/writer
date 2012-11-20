#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012 Jan Kotanski
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
## \file ThreadPool.py
# Thread Pool class

#from threading import *                                                                      
from ElementThread import ElementThread
import Queue

## exception for problems in thread
class ThreadError(Exception): pass

## Pool with threads
class ThreadPool(object):
    ## constructor
    # \brief It cleans the member variables
    def __init__(self, numThreads=10):
        ## maximal number of threads
        self.numThreads = -1
        ## queue of the appended elements
        self._elementQueue = Queue.Queue()
        ## list of the appended elements
        self._elementList = []
        ## list of the threads related to the appended elements
        self._threadList = []

    ## appends the thread element
    # \param elem the thread element
    def append(self, elem):
        self._elementList.append(elem)

    ## sets the JSON string to threads
    # \param globalJSON the static JSON string
    # \param localJSON the dynamic JSON string
    # \returns self object    
    def setJSON(self, globalJSON, localJSON=None):
        for el in self._elementList :
            if hasattr(el.source, "setJSON") and callable(el.source.setJSON):
                el.source.setJSON(globalJSON, localJSON)
        return self


    ## runner
    # \brief It runs the threads from the pool
    def run(self):
        self._threadList = []
        self._elementQueue = Queue.Queue()
        
        for eth in self._elementList:
            self._elementQueue.put(eth)

        if self.numThreads < 1:
            self.numThreads = len(self._elementList)

        for  i in range(min(self.numThreads, len(self._elementList))):
            th = ElementThread(i, self._elementQueue)
            self._threadList.append(th)
            th.start()


    ## waits for all thread from the pool
    # \param timeout the maximal waiting time
    def join(self, timeout=None):
        for th in self._threadList:
            if th.isAlive():
                th.join()

                
    ## runner with waiting
    # \brief It runs and waits the threads from the pool 
    def runAndWait(self):
        self.run()
        self.join()

    ## checks errors from threads
    def checkErrors(self):
        errors = []
        for el in self._elementList:
            if el.error:
                errors.append(el.error)

        if errors:
            raise ThreadError("Problems in storing data: %s" %  str(errors)  )

    ## closer
    # \brief It close the threads from the pool
    def close(self):
        for el in self._elementList:
            el.h5Object.close()
        self._threadList = []
        self._elementList = []
        self._elementQueue = None
