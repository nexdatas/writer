#!/usr/bin/env python
"""@package docstring
@file NexusXMLHandler.py
An example of SAX Nexus parser
"""
                                                                      
import pni.nx.h5 as nx

from numpy  import * 
from xml import sax

import sys,os
from H5Elements import *

from ThreadPool import *

# A map of NEXUS : pninx types 
mt={"NX_FLOAT32":"float32","NX_FLOAT64":"float64","NX_FLOAT":"float64","NX_NUMBER":"float64","NX_INT":"int64","NX_INT64":"int64","NX_INT32":"int32","NX_UINT64":"uint64","NX_UINT32":"uint32","NX_DATE_TIME":"string","NX_CHAR":"string","NX_BOOLEAN":"int32"}

# A map of tag attribute types 
dA={"signal":"NX_INT","axis":"NX_INT","primary":"NX_INT32","offset":"NX_INT","stride":"NX_INT","vector":"NX_FLOATVECTOR",
       "file_time":"NX_DATE_TIME","file_update_time":"NX_DATE_TIME","restricted":"NX_INT","ignoreExtraGroups":"NX_BOOLEAN",
    "ignoreExtraFields":"NX_BOOLEAN","ignoreExtraAttributes":"NX_BOOLEAN","minOccus":"NX_INT","maxOccus":"NX_INT"
    }


    
class NexusXMLHandler(sax.ContentHandler):
    """A SAX2 parser  """
    def __init__(self,fname):
        """ Constructor """
        sax.ContentHandler.__init__(self)
        ## A map of NXclass : name
        self.groupTypes={"":""}
        ## An H5 file name
        self.fname=fname
        self.nxFile=nx.create_file(self.fname,overwrite=True)
        ## A stack with open tag elements
        self.stack=[EFile("NXfile",[],None,self.nxFile)]


        self.elementClass={'group':EGroup, 'field':EField, 'attribute':EAttribute,
                           'link':ELink, 'doc':EDoc,
                           'symbols':Element, 'symbol':ESymbol, 
                           'dimensions':EDimensions, 
                           'dim':EDim, 'enumeration':Element, 'item':Element,
                           'datasource':DataSourceFactory,'record':ERecord }

#                           'definition':Element, 

        self.symbols={}

        self.initPool=ThreadPool()
        self.stepPool=ThreadPool()
        self.finalPool=ThreadPool()

        self.poolMap={'INIT':self.initPool,'STEP':self.stepPool,'FINAL':self.finalPool}


        
    def nWS(text):
        """  cleans whitespaces  """
        return ' '.join(text.split())
        
    def lastObject(self):
        """  returns an object from the last stack elements """
        if len(self.stack) > 0: 
            return self.stack[-1].fObject
        else:
            return None
        

    def last(self):
        """  returns the last stack elements """
        if len(self.stack) > 0: 
            return self.stack[-1]
        else:
            return None

    def beforeLast(self):
        """  returns the last stack elements """
        if len(self.stack) > 0: 
            return self.stack[-2]
        else:
            return None


    def characters(self, ch):
        """  adds the tag content """
        self.last().content.append(ch)

    def startElement(self, name, attrs):
        """  parses an opening tag"""
        self.content=""
        if name in self.elementClass:
            print "Calling: ", name, attrs.keys()
            print "MYType" , type(self.last())
            self.stack.append(self.elementClass[name](name, attrs, self.last()))
            if hasattr(self.last(),"fetchName"):
                self.last().fetchName(self.groupTypes)
            if hasattr(self.last(),"createLink"):
                self.last().createLink(self.groupTypes)
        else:
            print 'Unsupported tag:', name, attrs.keys()


    def endElement(self, name):
        """  parses an closing tag"""
        print 'End of element:', name , "last:" ,  self.last().tName
        if self.last().tName == name :
            if name in self.elementClass:
                print "Closing: ", name
                strategy=self.last().store(name)
                print "strategy", strategy
                if strategy in self.poolMap.keys():
                    self.poolMap[strategy].append(self.last())
                print 'Content:' , "".join(self.last().content)    
                print "poping"
                self.stack.pop()

    def getNXFile(self):
        return self.nxFile            

    def closeStack(self):
        """  closes the H5 file """
        for s in self.stack:
            if isinstance(s, FElement):
                if hasattr(s.lastObject(),"close"):
                    s.lastObject().close()
        if self.nxFile:
            print "nxClosing"
            self.nxFile.close()


    def closeFile(self):
        """  closes the H5 file """
        self.closeStack()
        if self.nxFile:
            print "nxClosing"
            self.nxFile.close()



if __name__ == "__main__":

    if  len(sys.argv) <3:
        print "usage: simpleXMLtoh5.py  <XMLinput>  <h5output>"
        
    else:
        fi=sys.argv[1]
        if os.path.exists(fi):
            fo=sys.argv[2]

        # Create a parser object
            parser = sax.make_parser()
            
            handler = NexusXMLHandler(fo)
            parser.setContentHandler( handler )

            parser.parse(open(fi))
            handler.closeFile()
    
