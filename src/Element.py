#!/usr/bin/env python
"""@package docstring
@file Element.py
"""
                                                                      

class Element:
    """A tag element stored on our stack  """
    def __init__(self,name,attrs,last=None):
        """ Constructor """
        ## Stored tag name
        self.tName=name
        self.tAttrs=attrs
        ## Stored tag content
        self.doc=""
        self.content=[]
        self.last=last


    def lastObject(self):
        if hasattr(self.last,"fObject"):
            return self.last.fObject
        else:
            print "H5 Object not found  "
            None

    def beforeLast(self):
        if self.last:
            return self.last.last
        else:
            return None

        
    def store(self,name):
        pass
