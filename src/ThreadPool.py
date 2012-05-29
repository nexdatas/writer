#!/usr/bin/env python
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
        
