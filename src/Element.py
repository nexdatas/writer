#!/usr/bin/env python
"""@package docstring
@file Element.py
"""
                                                                      

class Element:
    """A tag element stored on our stack  """
    def __init__(self,name,attrs):
        """ Constructor """
        ## Stored tag name
        self.tName=name
        self.tAttrs=attrs
        ## Stored tag content
        self.doc=""
        self.content=[]

