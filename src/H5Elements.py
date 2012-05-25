#!/usr/bin/env python
"""@package docstring
@file H5Elements.py
"""
                                                                      
import pni.nx.h5 as nx

from numpy  import * 

from DataSource import *


from Element import *

from threading import Thread

class FElement(Thread,Element):
    """A tag element corresponding to one of H5 objects """

    def __init__(self,obj,name,attrs):
        Thread.__init__(self)
        """ Constructor """
        Element.__init__(self,name,attrs)
        ## Stored tag object 
        self.fObject=obj
        self.source=None

    def run(self):
        if self.source:
            self.source.getData()



class EField(FElement):        
    def __init__(self,obj,name,attrs):
        FElement.__init__(self,obj,name,attrs)
        self.rank="0"
        self.lengths={}
        
class EGroup(FElement):        
    def __init__(self,obj,name,attrs):
        FElement.__init__(self,obj,name,attrs)

class ELink(FElement):        
    def __init__(self,obj,name,attrs):
        FElement.__init__(self,obj,name,attrs)

class EFile(FElement):        
    def __init__(self,obj,name,attrs):
        FElement.__init__(self,obj,name,attrs)





class EDoc(Element):        
    def __init__(self,name,attrs):
        Element.__init__(self,name,attrs)

class EDimensions(Element):        
    def __init__(self,name,attrs):
        Element.__init__(self,name,attrs)

class EDim(Element):        
    def __init__(self,name,attrs):
        Element.__init__(self,name,attrs)

class ERecord(Element):        
    def __init__(self,name,attrs):
        Element.__init__(self,name,attrs)

