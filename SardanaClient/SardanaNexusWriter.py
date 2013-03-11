#!/usr/bin/env python
 
import sys, os, time
from PyQt4 import QtCore, QtGui
import taurus
#from taurus.qt.qtgui.application import TaurusApplication 

from optparse import OptionParser
import PyTango
import Hasylab

doorName = "<>"
door = None
macroServerName = "<>"
db = None



if __name__ == "__main__":
    from nexusWriterDoor import nexusDoor
    factory = taurus.Factory()
    factory.registerDeviceClass('Door',  nexusDoor)
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

    door.setEnvironment('ScanFinished', 'False')

    i = 0
    for elm in sys.argv:
        if sys.argv[i] == '-d':
            del sys.argv[i+1]
            del sys.argv[i]
            break
        i += 1 
#    app = TaurusApplication(sys.argv)

    try: 
        db = PyTango.Database()
    except:
        print "Can't connect to tango database on", os.getenv('TANGO_HOST')
        sys.exit(255)
    result = db.get_device_property(doorName, ['MacroServerName'])
    macroServerName = result['MacroServerName'][0]

#    dialog = Dialog()
#    dialog = QtGui.QDialog()
#    sys.exit(dialog.exec_())

    finished = False
    while not finished:
        time.sleep(10)
        env = door.getEnvironment()
#        finished = False if str(door.getEnvironment('ScanFinished')).upper() == 'FALSE' else True
#        print "FINISHED", finished
