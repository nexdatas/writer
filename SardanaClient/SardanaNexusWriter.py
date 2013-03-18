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
#from taurus.qt.qtgui.application import TaurusApplication 

from optparse import OptionParser
import PyTango
import Hasylab

from nexusWriterDoor import nexusDoor


## finished flag
finished = True


## checks if writing can be interupted
# \param signal number 
# \frame current stack frame
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
    ## door factory
    factory = taurus.Factory()
    factory.registerDeviceClass('Door',  nexusDoor)
    print "DR", factory.getExistingDevices()

    ## door name
    doorName = "<>"
    ## door instance
    door = None
    ## macroserver name
    macroServerName = "<>"
    ## db instance
    db = None
    ## run options
    options = None
    ## usage example
    usage = "usage: %prog [-d <doorName>] [-n] \n e.g.: %prog -d p09/door/exp.01 -n"
    ## option parser
    parser = OptionParser(usage=usage)
    parser.add_option("-d", action="store", type="string", dest="doorName", 
                      help="name of a door, e.g. p09/door/exp.01")
    parser.add_option("-n","--no-widget", action="store_false", 
                      default=True, dest="widget", help="do not show graphic widget")

    (options, args) = parser.parse_args()
    if options.doorName is None:
        ## local door names
        lst = Hasylab.getLocalDoorNames()
        if len(lst) == 1:
            doorName = lst[0]
        else:
            parser.print_help()
            sys.exit(255)
    else:
        doorName = options.doorName

        

#    print "DOOR", doorName        
    door = taurus.Device(doorName)

    ## environment variables
    env = door.getEnvironment()
    door.setEnvironment("JsonRecorder", "True")
    if not env.has_key('FlagDisplayAll'):
        door.setEnvironment('FlagDisplayAll', 'False')

        
    door.setEnvironment('ScanFinished', 'True')

    i = 0
#    print "SYS", sys.argv
    for elm in sys.argv:
        if sys.argv[i] == '-d':
            sys.argv.pop(i+1)
            sys.argv.pop(i)
            break
        i += 1 
#    print "SYS2", sys.argv
#    app = TaurusApplication(sys.argv)

    try: 
        db = PyTango.Database()
    except:
        print "Can't connect to tango database on", os.getenv('TANGO_HOST')
        sys.exit(255)
    ## MacroServer properties
    msproperties = db.get_device_property(doorName, ['MacroServerName'])
    macroServerName = msproperties['MacroServerName'][0]


    import sys
    from PyQt4.QtGui import QApplication
    from SardanaWriterDlg import SardanaWriterDlg

    env = door.getEnvironment()
    finished = False if str(door.getEnvironment('ScanFinished')).upper() == 'FALSE' else True
    if options.widget:
        ## Qt application
        app = QApplication(sys.argv)
        ## dialog form
        form = SardanaWriterDlg()
        form.createGUI()
#        form.connect(, SIGNAL("updateFile(QString)"), self.updateFile)     
        form.show()
        app.exec_()
 
        env = door.getEnvironment()
        finished = False if str(door.getEnvironment('ScanFinished')).upper() == 'FALSE' else True
        while not finished:
            env = door.getEnvironment()
            finished = False if str(door.getEnvironment('ScanFinished')).upper() == 'FALSE' else True
            time.sleep(1)
#            print "FINISHED", finished

    else:
    
        signal.signal(signal.SIGINT, signal_handler)
        while True:
            env = door.getEnvironment()
            finished = False if str(door.getEnvironment('ScanFinished')).upper() == 'FALSE' else True
            
            time.sleep(1)
