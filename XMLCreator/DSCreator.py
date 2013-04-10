#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2013 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package ndtstools tools for ndts
## \file simpleXMLScan.py
# test of XML file creator

from simpleXML import *

from optparse import OptionParser
from xml.dom.minidom import parse, parseString


## provides xml content of the node
# \param node DOM node
# \returns xml content string
def getText(node):
    if not node:
        return 
    xml = node.toxml() 
    start = xml.find('>')
    end = xml.rfind('<')
    if start == -1 or end < start:
        return ""
    return xml[start + 1:end].replace("&lt;","<").replace("&gt;","<").replace("&amp;","&")


## the main function
def main2():



    df = XMLFile("scan.xml")
    
    en = NGroup(df, "entry1", "NXentry")

    ## instrument
    ins = NGroup(en, "instrument", "NXinstrument")
#    NXsource    
    dt = NGroup(ins, "detector", "NXdetector")
    f = NField(dt, "counter1", "NX_FLOAT")
    f.setUnits("m")
#    f.setText("0.2")
    f.setStrategy("STEP")
    sr = NDSource(f)

    sr.initClient("exp_c01","exp_c01");


    f = NField(dt, "counter2", "NX_FLOAT")
    f.setUnits("s")
#    f.setText("0.2")
    f.setStrategy("STEP")
    sr = NDSource(f)
    sr.initClient("exp_c02","exp_c02");
    

    f = NField(dt, "mca", "NX_FLOAT")
    f.setUnits("")
    d = NDimensions(f, "1")
    d.dim("1", "2048")
    f.setStrategy("STEP")
    sr = NDSource(f)
    sr.initTango("p09/mca/exp.02","p09/mca/exp.02", "attribute", "Data")
#    sr.initClient("p09/mca/exp.02","p09/mca/exp.02")

        ##    NXdata
    da = NGroup(en, "data", "NXdata")
    ## link
    l = NLink(da, "data", "/NXentry/NXinstrument/NXdetector/mca")
    l.addDoc("Link to mca in /NXentry/NXinstrument/NXdetector")
    l = NLink(da, "counter1", "/NXentry/NXinstrument/NXdetector/counter1")
    l.addDoc("Link to counter1 in /NXentry/NXinstrument/NXdetector")
    l = NLink(da, "counter2", "/NXentry/NXinstrument/NXdetector/counter2")
    l.addDoc("Link to counter2 in /NXentry/NXinstrument/NXdetector")



    df.dump()




def main():
    ## usage example
    usage = "usage: %prog [options] inputFile"
    ## option parser
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--directory", type="string",
                      help="output directory where datasources will be stored",
                      dest="dir", default=".")

    (options, args) = parser.parse_args()
    print "INPUT:", args
    print "OUTPUT DIR:", options.dir
    if not len(args):
        parser.print_help()
        sys.exit(255)


    indom = parse(args[0])
    hw= indom.getElementsByTagName("hw")
    device = hw[0].firstChild

    while device:
        if device.nodeName =='device':
            name = getText(device.getElementsByTagName("name")[0]) \
                if len(device.getElementsByTagName("name")) else None
            dtype = getText(device.getElementsByTagName("type")[0]) \
                if len(device.getElementsByTagName("type")) else None     
            module = getText(device.getElementsByTagName("module")[0]) \
                if len(device.getElementsByTagName("module")) else None
            tdevice = getText(device.getElementsByTagName("device")[0]) \
                if len(device.getElementsByTagName("device")) else None
            hostname = getText(device.getElementsByTagName("hostname")[0]) \
                if len(device.getElementsByTagName("hostname")) else None
            pool = getText(device.getElementsByTagName("pool")[0]) \
                if len(device.getElementsByTagName("pool")) else None
            controller = getText(device.getElementsByTagName("controller")[0]) \
                if len(device.getElementsByTagName("controller")) else None
            channel = getText(device.getElementsByTagName("channel")[0]) \
                if len(device.getElementsByTagName("channel")) else None
            rootdevicename = getText(device.getElementsByTagName("rootdevicename")[0]) \
                if len(device.getElementsByTagName("rootdevicename")) else None
            comment = device.getElementsByTagName("#comment")

            host = hostname.split(":")[0]
            port = hostname.split(":")[1] if len(hostname.split(":")) >1 else None
                

            print name, dtype,module, tdevice, host, port,pool,controller,channel,rootdevicename

            encoding = None
            if tdevice.find("eurotherm") != -1:
                record = "Temperature"
            elif module.find("tip830") != -1:
                record = "Value"
            elif module.find("tip551") != -1:
                record = "Voltage"
            else:
                record = None


            if pool:
                df = XMLFile("%s/%s.ds.xml" %(options.dir, name))
                sr = NDSource(df)
                sr.initClient(name, tdevice)
                df.dump()
            elif record:    
                df = XMLFile("%s/%s.ds.xml" %(options.dir, name))
                sr = NDSource(df)
                sr.initTango(name, tdevice, "attribute", record,host, port, encoding)
                df.dump()
            else:                
                print "WARNING: No record source for ", name ,tdevice 
            if comment:
                print "##", [device.data.strip() for c in comment]
                
            df.dump()
#            pass
        elif device.nodeName =='#comment':
            print "COMMENT:",  "'%s'" % device.data.strip()
        else:
#            print "TEXT:", device.nodeName, "'", device.data.strip(),"'"
            pass
        device = device.nextSibling
        
#    devices = hw.getElementsByTagName("device")


# <name>eh1a_ireg13</name>
# <type>input_register</type>
# <module>sis3610</module>
# <device>p02/register/eh1a.in13</device>
# <control>tango</control>
# <hostname>haspp02oh1:10000</hostname>
# <pool>pool_haspp02ch1a</pool>
# <controller>sis3610in_eh1a</controller>
# <channel>13</channel>
# <rootdevicename>p02/register/eh1a.in</rootdevicename>


#<name>gpib</name>
# <type>type_tango</type>
# <module>module_tango</module>
# <device>p02/gpib/eh1.1</device>
# <control>tango</control>
# <hostname>haspp02oh1:10000</hostname>

# <name>gpib</name>
# <type>type_tango</type>
# <module>module_tango</module>
# <device>p02/gpib/eh1.1</device>
# <control>tango</control>
# <hostname>haspp02oh1:10000</hostname>

#    print len(devices)

#    for dv in devices:
#        name = dv.getElementsByTagName("name")
#        if name:
#            print getText(name[0])
#            continue
#        else:
#            print "No Name:",dv.toxml()
#        df = XMLFile("scan.xml")
#        sr = NDSource(f)
#        sr.initTango("p09/mca/exp.02","p09/mca/exp.02", "attribute", "Data")
        


if __name__ == "__main__":
    main()
