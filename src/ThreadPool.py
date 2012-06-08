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
## \package ndts nexdatas
## \file ThreadPool.py
# Thread Pool class

from threading import *                                                                      
from ElementThread import *

## Pool with threads
class ThreadPool:
    ## constructor
    # \brief It cleans the member variables
    def __init__(self):
        ## list of the appended elements
        self.elementList=[]
        ## list of the threads related to the appended elements
        self.threadList=[]

    ## appends the thread element
    # \param elem the thread element
    def append(self,elem):
        print "appending: ", elem
        self.elementList.append(elem)

    ## sets the JSON string to threads
    # \param mJSON the JSON string
    def setJSON(self,mJSON):
        for el in self.elementList :
            if hasattr(el.source,"setJSON"):
                el.source.setJSON(mJSON)
        return self

    ## runner
    # \brief It runs the threads from the pool
    def run(self):
        self.threadList=[]
        
        for eth in self.elementList:
            th=ElementThread(eth)
            th.start()
            self.threadList.append(th)
            print "running ", th.name

    ## waits for all thread from the pool
    # \param timeout the maximal waiting time
    def join(self,timeout=None):
        for th in self.threadList:
            if th.isAlive():
                th.join()
                
    ## runner with waiting
    # \brief It runs and waits the threads from the pool 
    def runAndWait(self):
        self.run()
        self.join()

    ## closer
    # \brief It close the threads from the pool
    def close(self):
        for el in self.elementList:
            el.fObject.close()
        self.threadList=[]
        
