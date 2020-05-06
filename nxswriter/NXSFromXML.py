#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2018 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
#

""" Command-line tool to ascess to Tango Data Server"""

import sys
import json
import time
import pytz
import datetime
import argparse

from . import TangoDataWriter


class CreateFile(object):

    """ Create File runner"""

    def __init__(self, options):
        """ the main program function

        :param options: parser options
        :type options: :class:`argparse.Namespace`
        """
        #: (:obj:`str`) file name
        self.__file = ""
        #: (:obj:`str`) nexus path
        self.__nxpath = ""
        #: (:obj:`str`) xml configuration string
        self.__xml = ""
        #: (:obj:`str`) json data string
        self.__data = options.data
        #: (:obj:`float`) time between records in seconds
        self.__stime = float(options.stime)
        #: (:obj:`int`) number of record steps
        self.__nrecords = int(options.nrecords)
        #: (:obj:`str`) json file
        self.__jsonfile = options.jsonfile
        #: (:obj:`bool`) verbose mode
        self.__verbose = options.verbose or False
        #: (:obj:`bool`) append mode
        self.__append = options.append or False

        lparent = str(options.parent).split(":/")
        if len(lparent) >= 3:
            self.__file = lparent[1]
            self.__nxpath = ":/".join(lparent[2:])
        elif len(lparent) == 2:
            self.__file = lparent[0]
            self.__nxpath = lparent[1]
        elif len(lparent) == 1:
            self.__file = lparent[0]

        if options.args and len(options.args):
            self.__xml = options.args[0].strip()
        else:
            self.__xml = open(options.xmlfile, 'r').read()

    @classmethod
    def currenttime(cls):
        """ returns current time string

        :returns: current time
        :rtype: :obj:`str`
        """
        tzone = time.tzname[0]
        tz = pytz.timezone(tzone)
        fmt = '%Y-%m-%dT%H:%M:%S.%f%z'
        starttime = tz.localize(datetime.datetime.now())
        return str(starttime.strftime(fmt))

    def jsonstring(self):
        """ merges data in json string

        :returns: json string
        :rtype: :obj:`str`
        """
        jsn = {}
        if self.__jsonfile:
            sjsn = open(self.__jsonfile, 'r').read()
            if sjsn.strip():
                jsn = sjsn.loads()
        if "data" not in jsn.keys():
            jsn["data"] = {}
        if "start_time" not in jsn["data"]:
            jsn["data"]["start_time"] = self.currenttime()
        if "end_time" not in jsn["data"]:
            jsn["data"]["end_time"] = self.currenttime()
        data = json.loads(str(self.__data.strip()))
        jsn["data"].update(data)
        return json.dumps(jsn)

    def run(self):
        """ the main program function
        """
        tdw = TangoDataWriter.TangoDataWriter()
        tdw.fileName = str(self.__file)
        tdw.parent = str(self.__nxpath or "")
        if self.__verbose:
            print("opening the %s file" % self.__file)
        tdw.openFile()
        tdw.xmlsettings = self.__xml

        if self.__verbose:
            print("opening the data entry ")
        if self.__data and self.__data.strip():
            tdw.jsonrecord = self.jsonstring()
        tdw.skipacquisition = self.__append
        tdw.openEntry()
        for i in range(self.__nrecords):
            if self.__verbose:
                print("recording the H5 file")
            tdw.jsonrecord = self.jsonstring()
            tdw.record()
            if self.__nrecords > 1:
                if self.__verbose:
                    print("sleeping for 1s")
                time.sleep(self.__stime)
        if self.__verbose:
            print("closing the data entry ")
        tdw.jsonrecord = self.jsonstring()
        tdw.skipacquisition = self.__append
        tdw.closeEntry()

        if self.__verbose:
            print("closing the H5 file")
        tdw.closeFile()


def main():
    """ the main program function
    """

    #: pipe arguments
    pipe = ""
    if not sys.stdin.isatty():
        pp = sys.stdin.readlines()
        #: system pipe
        pipe = "".join(pp)

    description = "Command-line tool for creating NeXus files" \
                  + " from XML template"

    epilog = 'examples:\n' \
        '  nxsfromxml  -x config.xml -p newfile.nxs -j datastring.json\n\n' \
        '    - creates a newfile.nxs file with configuration from config.xml' \
        ' and data from datastring.json\n\n' \
        '  nxsfromxml  -x config.xml -p outputfile.nxs -d'\
        ' \'{"sample_name":"sn", "chemical_formula":"H2O", ' \
        '"beamtime_id":"1234", "title":"Sample"}\'\n\n' \
        '    - creates an outputfile.nxs file with configuration ' \
        'from config.xml and data from given json dictionary\n\n' \
        '  nxsconfig get source mono slit1 mirror2 | ' \
        'nxsfromxml -p basicsetup.nxs\n\n' \
        '    - creates an basicsetup.nxs file with configuration ' \
        'of source mono slit1 mirror2 components ' \
        'created by nxsconfig get \n\n'
    parser = argparse.ArgumentParser(
        description=description, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        'args', metavar='xml_config', type=str, nargs='?',
        help='nexus writer configuration string')
    parser.add_argument(
        "-x", "--xml-file",
        help="optional file with nexus "
        "configuration string",
        dest="xmlfile", default="")
    parser.add_argument(
        "-p", "--parent",
        help="nexus file name",
        dest="parent", default="")
    parser.add_argument(
        "-d", "--data",
        help="json string with data",
        dest="data", default="")
    parser.add_argument(
        "-j", "--json-file",
        help="json data file in a jsonrecord attribute format",
        dest="jsonfile", default="")
    parser.add_argument(
        "-t", "--time",
        help="time between record steps in seconds, default: 1 s",
        dest="stime", default="1")
    parser.add_argument(
        "-n", "--nrecords",
        help="number of performed record steps",
        dest="nrecords", default="1")
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        default=False, dest="verbose",
        help="verbose mode")
    parser.add_argument(
        "-a", "--append", action="store_true",
        default=False, dest="append",
        help="append mode")

    try:
        options = parser.parse_args()
    except Exception as e:
        sys.stderr.write("Error: %s\n" % str(e))
        sys.stderr.flush()
        parser.print_help()
        print("")
        sys.exit(255)

    #: command-line and pipe arguments
    parg = []
    if hasattr(options, "args"):
        parg = [options.args] if options.args else []
    if pipe:
        parg.append(pipe)
    options.args = parg

    if not options.xmlfile and (
            not options.args or len(options.args) < 1):
        parser.print_help()
        sys.exit(255)
    if options.xmlfile and (
            options.args and len(options.args) > 0):
        parser.print_help()
        sys.exit(255)

    if not options.parent:
        parser.print_help()
        sys.exit(255)

    command = CreateFile(options)
    command.run()


if __name__ == "__main__":
    main()
