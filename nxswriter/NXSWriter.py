#    "$Name:  $";
#    "$Header:  $";
# =============================================================================
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
# =============================================================================
#          This file is generated by POGO
#    (Program Obviously used to Generate tango Object)
#
#         (c) - Software Engineering Group - ESRF
# =============================================================================
#

""" Nexus Data Writer - Tango Server """

import PyTango
import sys
from threading import Thread, Lock
from datetime import datetime

from .TangoDataWriter import TangoDataWriter as TDW


class CommandThread(Thread):
    """ thread with server command
    """

    def __init__(self, server, command, finalState, args=None):
        """constructor

        :param server: Tango server implementation
        :type server: :class:`PyTango.Device_4Impl`
        :param command: Thread command
        :type command: :obj:`str`
        :param finalState: Final State Code
        :type finalState: :class:`PyTango.DevState`
        :param args: List of command arguments
        :type args: :obj:`list` <:obj:`str`>
        """
        Thread.__init__(self)
        #: (:class:`PyTango.Device_4Impl`) tango server
        self.server = server
        #: (:obj:`__callable__`) command
        self.command = getattr(server.tdw, command)
        #: (:class:`PyTango.DevState`) final state
        self.fstate = finalState
        #: (:class:`PyTango.DevState`) error state
        self.estate = PyTango.DevState.FAULT
        #: (:obj:`list` <:obj:`str`>) command arguments
        self.args = args if isinstance(args, list) else []

    def run(self):
        """ runs the given command on the server and changes the state on exit
        """
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


class NXSDataWriter(PyTango.Device_4Impl):
    """ Tango Server to store data in H5 files

    :brief: Device States Description:
            DevState.ON :       NeXuS Data Server is switch on
            DevState.OFF :      NeXuS Data Writer is switch off
            DevState.EXTRACT :  H5 file is open
            DevState.OPEN :     XML configuration is initialzed
            DevState.RUNNING :  NeXus Data Server is writing
            DevState.FAULT :    Error state
    """

    def __init__(self, cl, name):
        """ Device constructor

        :param cl: class name
        :type cl: :obj:`str`
        :param name: device name
        :type name: :obj:`str`
        """
        PyTango.Device_4Impl.__init__(self, cl, name)
        self.debug_stream("In __init__()")
        if not hasattr(self, "lock"):
            #: (:class:`threading.Lock`) thread lock
            self.lock = Lock()
        #: (:class:`PyTango.DevState`) state flag
        self.state_flag = PyTango.DevState.OFF
        #: (:class:`CommandThread`) openentry thread
        self.othread = None
        #: (:class:`CommandThread`) record thread
        self.rthread = None
        #: (:class:`CommandThread`) closentry thread
        self.cthread = None
        #: (:class:`nxswriter.TangoDataWriter.TangoDataWriter`) \
        #:       Tango Data Writer
        self.tdw = TDW(self)
        #: (:obj:`list`<:obj:`str`>) list with errors
        self.errors = []
        #: (:obj:`dict` < :class:`PyTango.DevState`, :obj:`str`> ) \
        #:      status messages
        self.__status = {
            PyTango.DevState.OFF: "Not Initialized",
            PyTango.DevState.ON: "Ready",
            PyTango.DevState.OPEN: "File Open",
            PyTango.DevState.EXTRACT: "Entry Open",
            PyTango.DevState.RUNNING: "Writing ...",
            PyTango.DevState.FAULT: "Error",
        }
        NXSDataWriter.init_device(self)

    def delete_device(self):
        """ Device destructor
        """
        self.debug_stream("In delete_device()")
        if hasattr(self, 'tdw') and self.tdw:
            if hasattr(self.tdw, 'closeFile'):
                try:
                    self.tdw.closeFile()
                    del self.tdw
                except:
                    pass
            self.tdw = None
        self.set_state(PyTango.DevState.OFF)

    def init_device(self):
        """ Device initialization
        """
        self.debug_stream("In init_device()")
        if not hasattr(self, "lock"):
            self.lock = Lock()
        try:
            self.set_state(PyTango.DevState.RUNNING)
            with self.lock:
                self.errors = []
            if hasattr(self, 'tdw') and self.tdw:
                if hasattr(self.tdw, 'closeFile'):
                    try:
                        self.tdw.closeFile()
                        del self.tdw
                    except:
                        pass
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

    def set_state(self, state):
        """set_state method

        :param state: State Code
        :type state: :class:`PyTango.DevState`
        """
        with self.lock:
            if state is not None:
                self.state_flag = state
            PyTango.Device_4Impl.set_state(self, self.state_flag)

    def get_state(self):
        """ get_state method

        :returns: State Code
        :rtype: :class:`PyTango.DevState`
        """
        with self.lock:
            PyTango.Device_4Impl.set_state(self, self.state_flag)
            PyTango.Device_4Impl.get_state(self)
            return self.state_flag

    def always_executed_hook(self):
        """ Always excuted hook method
        """
        self.debug_stream("In always_excuted_hook()")

    # ==================================================================
    #
    #    NXSDataWriter read/write attribute methods
    #
    # ==================================================================
    def read_attr_hardware(self, _):
        """ Read Attribute Hardware
        """
        self.debug_stream("In read_attr_hardware()")

    def __failed(self):
        """ on error
        """
        self.set_state(PyTango.DevState.FAULT)
        with self.lock:
            self.errors.append(
                str(datetime.now()) + ":\n" + str(sys.exc_info()[1]))

    def read_XMLSettings(self, attr):
        """ Read XMLSettings attribute

        :param attr: attribute object
        :type attr: :class:`PyTango.Attribute`
        """
        self.debug_stream("In read_XMLSettings()")
        attr.set_value(self.tdw.xmlsettings)

    def write_XMLSettings(self, attr):
        """ Write XMLSettings attribute

        :param attr: attribute object
        :type attr: :class:`PyTango.Attribute`
        """
        self.debug_stream("In write_XMLSettings()")
        self.tdw.xmlsettings = attr.get_write_value()

    def is_XMLSettings_allowed(self, _):
        """XMLSettings attribute State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.OFF,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def read_JSONRecord(self, attr):
        """ Read JSONRecord attribute

        :param attr: attribute object
        :type attr: :class:`PyTango.Attribute`
        """
        self.debug_stream("In read_JSONRecord()")

        attr.set_value(self.tdw.jsonrecord)

    def write_JSONRecord(self, attr):
        """ Write JSONRecord attribute

        :param attr: attribute object
        :type attr: :class:`PyTango.Attribute`
        """
        self.debug_stream("In write_JSONRecord()")
        self.tdw.jsonrecord = attr.get_write_value()

    def is_JSONRecord_allowed(self, _):
        """ JSONRecord attribute State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.OFF,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def read_FileName(self, attr):
        """ Read FileName attribute

        :param attr: attribute object
        :type attr: :class:`PyTango.Attribute`
        """
        self.debug_stream("In read_FileName()")

        attr.set_value(self.tdw.fileName)

    def write_FileName(self, attr):
        """ Write FileName attribute

        :param attr: attribute object
        :type attr: :class:`PyTango.Attribute`
        """
        self.debug_stream("In write_FileName()")
        if self.is_FileName_write_allowed():
            self.tdw.fileName = attr.get_write_value()
        else:
            self.warn_stream("To change the file name please close the file.")
            raise Exception(
                "To change the file name please close the file.")

    def is_FileName_write_allowed(self):
        """ FileName attribute Write State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.OFF,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def is_FileName_allowed(self, _):
        """FileName attribute State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.OFF]:
            return False
        return True

    def read_Errors(self, attr):
        """ Read Errors attribute

        :param attr: attribute object
        :type attr: :class:`PyTango.Attribute`
        """
        self.debug_stream("In read_Errors()")

        with self.lock:
            attr.set_value(self.errors)

    # ==================================================================
    #
    #    NXSDataWriter command methods
    #
    # ==================================================================

    def dev_state(self):
        """ State command

        :brief: This command gets the device state
                (stored in its <i>device_state</i> data member)
                and returns it to the caller.
        :returns: State Code
        :rtype: :class:`PyTango.DevState`
        """
        self.debug_stream("In dev_state()")
        return self.get_state()

    def dev_status(self):
        """ Status command

        :brief: This command gets the device status
                (stored in its <i>device_status</i> data member)
                and returns it to the caller.

        :returns: Status description
        :rtype: :obj:`str`
        """
        self.debug_stream("In dev_status()")
        self.set_state(None)
        with self.lock:
            state = self.state_flag
        self.set_status(self.__status[state])
        return self.__status[state]

    def OpenFile(self):
        """OpenFile command

        :brief: Open the H5 file
        """
        self.debug_stream("In OpenFile()")

        state = self.get_state()
        if state in [PyTango.DevState.OPEN]:
            self.CloseFile()
        self.set_state(PyTango.DevState.RUNNING)
        with self.lock:
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

    def is_OpenFile_allowed(self):
        """ OpenFile command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.OFF,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def OpenEntry(self):
        """ OpenEntry command

        :brief: Creating the new entry
        """
        self.debug_stream("In OpenEntry()")

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

    def is_OpenEntry_allowed(self):
        """ OpenEntry command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def Record(self, argin):
        """ Record command

        :brief: Record setting for one step
        :param argin: JSON string with data
        :type argin: :class:`PyTango.DevString`
        """
        self.debug_stream("In Record()")
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

    def is_Record_allowed(self):
        """ Record command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def CloseEntry(self):
        """ CloseEntry command

        :brief: Closing the entry
        """
        self.debug_stream("In CloseEntry()")
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

    def is_CloseEntry_allowed(self):
        """ CloseEntry command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def OpenEntryAsynch(self):
        """ OpenEntryAsynch command

        :brief: Creating the new entry in asynchronous mode
        """
        self.debug_stream("In OpenEntryAsynch()")
        self.set_state(PyTango.DevState.RUNNING)
        self.get_device_properties(self.get_device_class())
        self.tdw.numberOfThreads = self.NumberOfThreads
        self.othread = CommandThread(
            self, "openEntry", PyTango.DevState.EXTRACT)
        self.othread.start()

    def is_OpenEntryAsynch_allowed(self):
        """ OpenEntryAsynch command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.EXTRACT,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def RecordAsynch(self, argin):
        """ RecordAsynch command

        :brief: Record setting for one step in asynchronous mode
        :param argin:  DevString    JSON string with data
        """
        self.debug_stream("In RecordAsynch()")
        self.set_state(PyTango.DevState.RUNNING)
        self.rthread = CommandThread(
            self, "record", PyTango.DevState.EXTRACT, [argin])
        self.rthread.start()

    def is_RecordAsynch_allowed(self):
        """ RecordAsynch command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.FAULT,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def CloseEntryAsynch(self):
        """CloseEntryAsynch command

        :brief: Closing the entry is asynchronous mode
        """
        self.debug_stream("In CloseEntryAsynch()")
        state = self.get_state()
        if state != PyTango.DevState.FAULT:
            state = PyTango.DevState.OPEN
        self.set_state(PyTango.DevState.RUNNING)
        self.cthread = CommandThread(
            self, "closeEntry", state)
        self.cthread.start()

    def is_CloseEntryAsynch_allowed(self):
        """ CloseEntryAsynch command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.OPEN,
                                PyTango.DevState.RUNNING]:
            return False
        return True

    def CloseFile(self):
        """CloseFile command

        :brief: Close the H5 file
        """
        self.debug_stream("In CloseFile()")
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

    def is_CloseFile_allowed(self):
        """ CloseFile command State Machine

        :returns: True if the operation allowed
        :rtype: :obj:`bool`
        """
        if self.get_state() in [PyTango.DevState.ON,
                                PyTango.DevState.OFF,
                                PyTango.DevState.RUNNING]:
            return False
        return True


class NXSDataWriterClass(PyTango.DeviceClass):
    """ NXSDataWriterClass class definition
    """

    #: (:obj:`dict` <:obj:`str`, \
    #:       [ :obj:`str`, :class:`PyTango._PyTango.CmdArgType`, \
    #:       [ :obj:`list`<:obj:`int`> ] ] > ) Class Properties
    class_property_list = {
    }

    #: (:obj:`dict` <:obj:`str`, \
    #:       [ :obj:`str`, :class:`PyTango._PyTango.CmdArgType`, \
    #:       [ :obj:`list`<:obj:`int`> ] ] > ) Device Properties
    device_property_list = {
        'NumberOfThreads':
        [PyTango.DevLong,
         "maximal number of threads",
         [100]],
    }

    #: (:obj:`dict` <:obj:`str`, \
    #:       [[ :class:`PyTango._PyTango.CmdArgType`, :obj:`str`]] >)
    #:       Command definitions
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

    #: (:obj:`dict` <:obj:`str`, \
    #:       [[ :class:`PyTango._PyTango.CmdArgType`, \
    #:          :class:`PyTango._PyTango.AttrDataFormat`, \
    #:          :class:`PyTango._PyTango.AttrWriteType` ], \
    #:          :obj:`dict` <:obj:`str` , any> ] > ) Attribute definitions
    attr_list = {
        'XMLSettings':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label': "XML Configuration",
             'description': "An XML string with Nexus configuration.",
             'Display level': PyTango.DispLevel.EXPERT,
        }],
        'JSONRecord':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label': "JSON string with client data",
             'description': "A JSON string with global client data.",
             'Display level': PyTango.DispLevel.EXPERT,
        }],
        'FileName':
        [[PyTango.DevString,
          PyTango.SCALAR,
          PyTango.READ_WRITE],
         {
             'label': "Output file with its path",
             'description': "A name of H5 output file with its full path",
        }],
        'Errors':
        [[PyTango.DevString,
          PyTango.SPECTRUM,
          PyTango.READ, 1000],
         {
             'label': "list of errors",
             'description': "list of errors",
        }],
    }

    def __init__(self, name):
        """  NXSDataWriterClass Constructor
        """
        PyTango.DeviceClass.__init__(self, name)
        self.set_type(name)
        print("In NXSDataWriterClass constructor")


# NXSDataWriter class main method
if __name__ == '__main__':
    pass
