#    "$Name:  $";
#    "$Header:  $";
#=============================================================================
#
# file :        NXSDataWriter.py
#
# description : Python source for the NXSDataWriter and its commands.
#                The class is derived from Device. It represents the
#                CORBA servant object which will be accessed from the
#                network. All commands which can be executed on the
#                NXSDataWriter are implemented in this file.
#
# project :     TANGO Device Server
#
# $Author:  $
#
# $Revision:  $
#
# $Log:  $
#
# copyleft :    European Synchrotron Radiation Facility
#               BP 220, Grenoble 38043
#               FRANCE
#
#=============================================================================
#          This file is generated by POGO
#    (Program Obviously used to Generate tango Object)
#
#         (c) - Software Engineering Group - ESRF
#=============================================================================
#
""" Nexus Data Writer - Tango Server """


import PyTango
import sys
from threading import Thread, Lock
from datetime import datetime

from .TangoDataWriter import TangoDataWriter as TDW


#==================================================================
##   CommandThread Class Description:
#
#         thread with server command
#
#==================================================================
class CommandThread(Thread):

#------------------------------------------------------------------
#    constructor
#
#    argin:  server      Device_4Impl    Tango server implementation
#    argin:  command     __callable__    Thread command
#    argin:  finalState  DevState        Final State Code
#    argin:  args        list            List of command arguments
#
#------------------------------------------------------------------
    def __init__(self, server, command, finalState, args=None):
        Thread.__init__(self)
        ## tango server
        self.server = server
        ## command
        self.command = getattr(server.tdw, command)
        ## final state
        self.fstate = finalState
        ## error state
        self.estate = PyTango.DevState.FAULT
        ## command arguments
        self.args = args if isinstance(args, list) else []

#------------------------------------------------------------------
#    runs the given command on the server and changes the state on exit
#------------------------------------------------------------------
    def run(self):
        try:
            self.command(*self.args)
            with self.server.lock:
                self.server.state_flag = self.fstate
        except (PyTango.DevFailed, BaseException):
            self.__failed()
            raise
        except:
            self.__failed()
            PyTango.Except.throw_exception(
                str(sys.exc_info()[0]),
                str(sys.exc_info()[1]),
                str(sys.exc_info()[2])
                )

    def __failed(self):
        with self.server.lock:
            self.server.state_flag = self.estate
        self.server.errors.append(
            str(datetime.now()) + ":\n" + str(sys.exc_info()[1]))


#==================================================================
##   NXSDataWriter Class Description:
#
#         Tango Server to store data in H5 files
#
#==================================================================
#     Device States Description:
#
#   DevState.ON :       NeXuS Data Server is switch on
#   DevState.OFF :      NeXuS Data Writer is switch off
#   DevState.EXTRACT :  H5 file is open
#   DevState.OPEN :     XML configuration is initialzed
#   DevState.RUNNING :  NeXus Data Server is writing
#   DevState.FAULT :    Error state
#==================================================================
class NXSDataWriter(PyTango.Device_4Impl):

#------------------------------------------------------------------
#    Device constructor
#------------------------------------------------------------------
    def __init__(self, cl, name):
        PyTango.Device_4Impl.__init__(self, cl, name)
        ## thread lock
        if not hasattr(self, "lock"):
            self.lock = Lock()
        ## state flag
        self.state_flag = PyTango.DevState.OFF
        ## openentry thread
        self.othread = None
        ## record thread
        self.rthread = None
        ## closentry thread
        self.cthread = None
        ## Tango Data Writer
        self.tdw = TDW(self)
        ## list with errors
        self.errors = []
        ## status messages
        self.__status = {
            PyTango.DevState.OFF: "Not Initialized",
            PyTango.DevState.ON: "Ready",
            PyTango.DevState.OPEN: "File Open",
            PyTango.DevState.EXTRACT: "Entry Open",
            PyTango.DevState.RUNNING: "Writing ...",
            PyTango.DevState.FAULT: "Error",
            }
        NXSDataWriter.init_device(self)

#------------------------------------------------------------------
#    Device destructor
#------------------------------------------------------------------
    def delete_device(self):
        print "[Device delete_device method] for device", self.get_name()
        if hasattr(self, 'tdw') and self.tdw:
            if hasattr(self.tdw, 'closeFile'):
                self.tdw.closeFile()
            del self.tdw
            self.tdw = None
        self.set_state(PyTango.DevState.OFF)

#------------------------------------------------------------------
#    Device initialization
#------------------------------------------------------------------
    def init_device(self):
        print "In ", self.get_name(), "::init_device()"
        if not hasattr(self, "lock"):
            self.lock = Lock()
        try:
            self.set_state(PyTango.DevState.RUNNING)
            self.errors = []
            if hasattr(self, 'tdw') and self.tdw:
                if hasattr(self.tdw, 'closeFile'):
                    self.tdw.closeFile()
                del self.tdw
                self.tdw = None
            self.tdw = TDW(self)
            self.set_state(PyTango.DevState.ON)
        except (PyTango.DevFailed, BaseException):
            self.__failed()
            raise
        except:
            self.__failed()
            PyTango.Except.throw_exception(
                str(sys.exc_info()[0]),
                str(sys.exc_info()[1]),
                str(sys.exc_info()[2])
                )

        self.get_device_properties(self.get_device_class())

#------------------------------------------------------------------
#    set_state method
#
#    argin:  DevState    State Code
#------------------------------------------------------------------
    def set_state(self, state):
        with self.lock:
            if state is not None:
                self.state_flag = state
            PyTango.Device_4Impl.set_state(self, self.state_flag)

#------------------------------------------------------------------
#    get_state method
#
#    argout: DevState    State Code
#------------------------------------------------------------------
    def get_state(self):
        with self.lock:
            PyTango.Device_4Impl.set_state(self, self.state_flag)
            PyTango.Device_4Impl.get_state(self)
            return self.state_flag

#------------------------------------------------------------------
#    Always excuted hook method
#------------------------------------------------------------------
    def always_executed_hook(self):
        print "In ", self.get_name(), "::always_excuted_hook()"

#==================================================================
#
#    NXSDataWriter read/write attribute methods
#
#==================================================================
#------------------------------------------------------------------
#    Read Attribute Hardware
#------------------------------------------------------------------
    def read_attr_hardware(self, _):
        print "In ", self.get_name(), "::read_attr_hardware()"

#------------------------------------------------------------------
#    on error
#------------------------------------------------------------------
    def __failed(self):
        self.set_state(PyTango.DevState.FAULT)
        self.errors.append(
            str(datetime.now()) + ":\n" + str(sys.exc_info()[1]))

#------------------------------------------------------------------
#    Read XMLSettings attribute
#------------------------------------------------------------------
    def read_XMLSettings(self, attr):
        print "In ", self.get_name(), "::read_XMLSettings()"
        attr.set_value(self.tdw.xmlsettings)

#------------------------------------------------------------------
#    Write XMLSettings attribute
#------------------------------------------------------------------
    def write_XMLSettings(self, attr):
        print "In ", self.get_name(), "::write_XMLSettings()"
        self.tdw.xmlsettings = attr.get_write_value()
        print "Attribute value = ", self.tdw.xmlsettings

#---- XMLSettings attribute State Machine -----------------
    def is_XMLSettings_allowed(self, _):
        if self.get_state() in [PyTango.DevState.OFF,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    Read JSONRecord attribute
#------------------------------------------------------------------
    def read_JSONRecord(self, attr):
        print "In ", self.get_name(), "::read_JSONRecord()"

        attr.set_value(self.tdw.jsonrecord)

#------------------------------------------------------------------
#    Write JSONRecord attribute
#------------------------------------------------------------------
    def write_JSONRecord(self, attr):
        print "In ", self.get_name(), "::write_JSONRecord()"
        self.tdw.jsonrecord = attr.get_write_value()
        print "Attribute value = ", self.tdw.jsonrecord

#---- JSONRecord attribute State Machine -----------------
    def is_JSONRecord_allowed(self, _):
        if self.get_state() in [PyTango.DevState.OFF,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    Read FileName attribute
#------------------------------------------------------------------
    def read_FileName(self, attr):
        print "In ", self.get_name(), "::read_FileName()"

        attr.set_value(self.tdw.fileName)

#------------------------------------------------------------------
#    Write FileName attribute
#------------------------------------------------------------------
    def write_FileName(self, attr):
        print "In ", self.get_name(), "::write_FileName()"
        if self.is_FileName_write_allowed():
            self.tdw.fileName = attr.get_write_value()

            print "Attribute value = ", self.tdw.fileName
        else:
            print >> self.log_warn, \
                "To change the file name please close the file."
            raise Exception(
                "To change the file name please close the file.")

#---- FileName attribute Write State Machine -----------------
    def is_FileName_write_allowed(self):
        if self.get_state() in [PyTango.DevState.OFF,
                                 PyTango.DevState.EXTRACT,
                                 PyTango.DevState.OPEN,
                                 PyTango.DevState.RUNNING]:
            return False
        return True

#---- FileName attribute State Machine -----------------
    def is_FileName_allowed(self, _):
        if self.get_state() in [PyTango.DevState.OFF]:
            return False
        return True

#------------------------------------------------------------------
#    Read Errors attribute
#------------------------------------------------------------------
    def read_Errors(self, attr):
        print "In ", self.get_name(), "::read_Errors()"

        attr.set_value(self.errors)
        print self.errors

#==================================================================
#
#    NXSDataWriter command methods
#
#==================================================================

#------------------------------------------------------------------
#    State command:
#
#    Description: This command gets the device state
#        (stored in its <i>device_state</i> data member)
#        and returns it to the caller.
#
#    argout: DevState    State Code
#------------------------------------------------------------------
    def dev_state(self):
        print "In ", self.get_name(), "::dev_state()"
        return self.get_state()

#------------------------------------------------------------------
#    Status command:
#
#    Description: This command gets the device status
#        (stored in its <i>device_status</i> data member)
#        and returns it to the caller.
#
#    argout: ConstDevString    Status description
#------------------------------------------------------------------
    def dev_status(self):
        print "In ", self.get_name(), "::dev_status()"
        self.set_state(None)
        with self.lock:
            state = self.state_flag
        self.set_status(self.__status[state])
        return self.__status[state]

#------------------------------------------------------------------
#    OpenFile command:
#
#    Description: Open the H5 file
#
#------------------------------------------------------------------
    def OpenFile(self):
        print "In ", self.get_name(), "::OpenFile()"

        state = self.get_state()
        if state in [PyTango.DevState.OPEN]:
            self.CloseFile()
        self.set_state(PyTango.DevState.RUNNING)
        self.errors = []
        try:
            self.tdw.openFile()
            self.set_state(PyTango.DevState.OPEN)
        except (PyTango.DevFailed, BaseException):
            self.__failed()
            raise
        except:
            self.__failed()
            PyTango.Except.throw_exception(
                str(sys.exc_info()[0]),
                str(sys.exc_info()[1]),
                str(sys.exc_info()[2])
                )

#---- OpenFile command State Machine -----------------
    def is_OpenFile_allowed(self):
        if self.get_state() in [PyTango.DevState.OFF,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    OpenEntry command:
#
#    Description: Creating the new entry
#
#------------------------------------------------------------------
    def OpenEntry(self):
        print "In ", self.get_name(), "::OpenEntry()"

        self.set_state(PyTango.DevState.RUNNING)
        try:
            self.get_device_properties(self.get_device_class())
            self.tdw.numberOfThreads = self.NumberOfThreads
            self.tdw.openEntry()
            self.set_state(PyTango.DevState.EXTRACT)
        except (PyTango.DevFailed, BaseException):
            self.__failed()
            raise
        except:
            self.__failed()
            PyTango.Except.throw_exception(
                str(sys.exc_info()[0]),
                str(sys.exc_info()[1]),
                str(sys.exc_info()[2])
                )

#---- OpenEntry command State Machine -----------------
    def is_OpenEntry_allowed(self):
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    Record command:
#
#    Description: Record setting for one step
#
#    argin:  DevString    JSON string with data
#------------------------------------------------------------------
    def Record(self, argin):
        print "In ", self.get_name(), "::Record()"
        self.set_state(PyTango.DevState.RUNNING)
        try:
            self.tdw.record(argin)
            self.set_state(PyTango.DevState.EXTRACT)
        except (PyTango.DevFailed, BaseException):
            self.__failed()
            raise
        except:
            self.__failed()
            PyTango.Except.throw_exception(
                str(sys.exc_info()[0]),
                str(sys.exc_info()[1]),
                str(sys.exc_info()[2])
                )

#---- Record command State Machine -----------------
    def is_Record_allowed(self):
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    CloseEntry command:
#
#    Description: Closing the entry
#
#------------------------------------------------------------------
    def CloseEntry(self):
        print "In ", self.get_name(), "::CloseEntry()"
        state = self.get_state()
        if state != PyTango.DevState.FAULT:
            state = PyTango.DevState.OPEN
        self.set_state(PyTango.DevState.RUNNING)
        try:
            self.tdw.closeEntry()
            self.set_state(state)
        except (PyTango.DevFailed, BaseException):
            self.__failed()
            raise
        except:
            self.__failed()
            PyTango.Except.throw_exception(
                str(sys.exc_info()[0]),
                str(sys.exc_info()[1]),
                str(sys.exc_info()[2])
                )

#---- CloseEntry command State Machine -----------------
    def is_CloseEntry_allowed(self):
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    OpenEntryAsynch command:
#
#    Description: Creating the new entry in asynchronous mode
#
#------------------------------------------------------------------
    def OpenEntryAsynch(self):
        print "In ", self.get_name(), "::OpenEntryAsynch()"
        self.set_state(PyTango.DevState.RUNNING)
        self.get_device_properties(self.get_device_class())
        self.tdw.numberOfThreads = self.NumberOfThreads
        self.othread = CommandThread(
            self, "openEntry", PyTango.DevState.EXTRACT)
        self.othread.start()

#---- OpenEntryAsynch command State Machine -----------------
    def is_OpenEntryAsynch_allowed(self):
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    RecordAsynch command:
#
#    Description: Record setting for one step in asynchronous mode
#
#    argin:  DevString    JSON string with data
#------------------------------------------------------------------
    def RecordAsynch(self, argin):
        print "In ", self.get_name(), "::RecordAsynch()"
        self.set_state(PyTango.DevState.RUNNING)
        self.rthread = CommandThread(
            self, "record", PyTango.DevState.EXTRACT, [argin])
        self.rthread.start()

#---- RecordAsynch command State Machine -----------------
    def is_RecordAsynch_allowed(self):
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    CloseEntryAsynch command:
#
#    Description: Closing the entry is asynchronous mode
#
#------------------------------------------------------------------
    def CloseEntryAsynch(self):
        print "In ", self.get_name(), "::CloseEntryAsynch()"
        state = self.get_state()
        if state != PyTango.DevState.FAULT:
            state = PyTango.DevState.OPEN
        self.set_state(PyTango.DevState.RUNNING)
        self.cthread = CommandThread(
            self, "closeEntry", state)
        self.cthread.start()

#---- CloseEntryAsynch command State Machine -----------------
    def is_CloseEntryAsynch_allowed(self):
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.RUNNING]:
            return False
        return True

#------------------------------------------------------------------
#    CloseFile command:
#
#    Description: Close the H5 file
#
#------------------------------------------------------------------
    def CloseFile(self):
        print "In ", self.get_name(), "::CloseFile()"
        state = self.get_state()
        if state in [PyTango.DevState.EXTRACT]:
            self.CloseEntry()
        if state != PyTango.DevState.FAULT:
            state = PyTango.DevState.ON
        self.set_state(PyTango.DevState.RUNNING)
        try:
            self.tdw.closeFile()
            self.set_state(state)
        except (PyTango.DevFailed, BaseException):
            self.__failed()
            raise
        except:
            self.__failed()
            PyTango.Except.throw_exception(
                str(sys.exc_info()[0]),
                str(sys.exc_info()[1]),
                str(sys.exc_info()[2])
                )

#---- CloseFile command State Machine -----------------
    def is_CloseFile_allowed(self):
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.RUNNING]:
            #    End of Generated Code
            #    Re-Start of Generated Code
            return False
        return True


#==================================================================
##    NXSDataWriterClass class definition
#
#==================================================================
class NXSDataWriterClass(PyTango.DeviceClass):

    ##    Class Properties
    class_property_list = {
        }

    ##    Device Properties
    device_property_list = {
        'NumberOfThreads':
            [PyTango.DevLong,
             "maximal number of threads",
             [100]],
        }

    ##    Command definitions
    cmd_list = {
        'OpenFile':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""]],
        'OpenEntry':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""]],
        'Record':
            [[PyTango.DevString, "JSON string with data"],
            [PyTango.DevVoid, ""]],
        'CloseEntry':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""]],
        'OpenEntryAsynch':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""]],
        'RecordAsynch':
            [[PyTango.DevString, "JSON string with data"],
            [PyTango.DevVoid, ""]],
        'CloseEntryAsynch':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""]],
        'CloseFile':
            [[PyTango.DevVoid, ""],
            [PyTango.DevVoid, ""]],
        }

    ##    Attribute definitions
    attr_list = {
        'XMLSettings':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label':"XML Configuration",
                'description':"An XML string with Nexus configuration.",
                'Display level':PyTango.DispLevel.EXPERT,
            }],
        'JSONRecord':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label':"JSON string with client data",
                'description':"A JSON string with global client data.",
                'Display level':PyTango.DispLevel.EXPERT,
            }],
        'FileName':
            [[PyTango.DevString,
            PyTango.SCALAR,
            PyTango.READ_WRITE],
            {
                'label':"Output file with its path",
                'description':"A name of H5 output file with its full path",
            }],
        'Errors':
            [[PyTango.DevString,
            PyTango.SPECTRUM,
            PyTango.READ, 1000],
            {
                'label':"list of errors",
                'description':"list of errors",
            }],
        }

#------------------------------------------------------------------
##    NXSDataWriterClass Constructor
#
#------------------------------------------------------------------
    def __init__(self, name):
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)
        print "In NXSDataWriterClass constructor"

#==================================================================
#
#    NXSDataWriter class main method
#
#==================================================================
if __name__ == '__main__':
    pass
