#!/usr/bin/env python
## \package ndts SardanaClient
## \file SardanaNexusWriter.py
# Sardana Nexus Writer 
#


import sys
import os
import time
import signal
import taurus

from optparse import OptionParser
import PyTango
import Hasylab

from nexusWriterDoor import nexusDoor
factory = taurus.Factory()
factory.registerDeviceClass('Door',  nexusDoor)


finished = True


def signal_handler(signal, frame):
    if not finished:
        msg = 'Do you what to interrupt the writing?'
        try:
            shall = True if raw_input("%s (y/N) " % msg).lower() == 'y' else False
        except:
            shall = False
    else:
        shall = True
    if shall:    
        print '\nBye !'
        sys.exit(0)


if __name__ == "__main__":
    doorName = "<>"
    door = None
    macroServerName = "<>"
    db = None
    options = None
    usage = "usage: %prog -d <doorName>\n e.g.: %prog -d p09/door/exp.01"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", action="store", type="string",
                      dest="doorName", help="name of a door, e.g. p09/door/exp.01")

    (options, args) = parser.parse_args()
    if options.doorName is None:
        lst = Hasylab.getLocalDoorNames()
        if len(lst) == 1:
            options.doorName = lst[0]
        else:
            parser.print_help()
            sys.exit(255)

    doorName = options.doorName
    door = taurus.Device(doorName)

    env = door.getEnvironment()
    door.setEnvironment("JsonRecorder", "True")
    if not env.has_key('FlagDisplayAll'):
        door.setEnvironment('FlagDisplayAll', 'False')

        
    door.setEnvironment('ScanFinished', 'True')

    i = 0
    for elm in sys.argv:
        if sys.argv[i] == '-d':
            sys.argv.pop(i+1)
            sys.argv.pop(i)
            break
        i += 1 

    try: 
        db = PyTango.Database()
    except:
        print "Can't connect to tango database on", os.getenv('TANGO_HOST')
        sys.exit(255)
    result = db.get_device_property(doorName, ['MacroServerName'])
    macroServerName = result['MacroServerName'][0]


    signal.signal(signal.SIGINT, signal_handler)
    while True:
        env = door.getEnvironment()
        finished = False if str(door.getEnvironment('ScanFinished')).upper() == 'FALSE' else True
#        print "FINISHED", finished

        time.sleep(1)
