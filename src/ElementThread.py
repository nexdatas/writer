#!/usr/bin/env python
"""@package docstring
@file ElementThread.py
"""

from threading import *                                                                       

class ElementThread(Thread):
    """ Pool of Threads """
    def __init__(self,elem):
        Thread.__init__(self)
        """ Constructor """
        self.elem=elem

    def run(self):
        self.elem.run()

