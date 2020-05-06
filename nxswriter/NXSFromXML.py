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
        self.file = ""
        #: (:obj:`str`) nexus path
        self.nxspath = ""
        #: (:obj:`str`) xml configuration string
        self.xml = ""
        #: (:obj:`str`) json data string
        self.data = options.data
        #: (:obj:`float`) time between records in seconds
        self.stime = float(options.stime)
        #: (:obj:`int`) number of record steps
        self.nrecords = int(options.nrecords)
        #: (:obj:`str`) json file
        self.jsonfile = options.jsonfile

        lparent = str(options.parent).split(":/")
        if len(lparent) >= 3:
            self.file = lparent[1]
            self.nxspath = ":/".join(lparent[2:])
        elif len(lparent) == 2:
            self.file = lparent[0]
            self.nxspath = lparent[1]
        elif len(lparent) == 1:
            self.file = lparent[0]

        if options.args and len(options.args):
            self.xml = options.args[0].strip()
        else:
            self.xml = open(options.xmlfile, 'r').read()

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
        if self.jsonfile:
            sjsn = open(self.jsonfile, 'r').read()
            if sjsn.strip():
                jsn = sjsn.loads()
        if "data" not in jsn.keys():
            jsn["data"] = {}
        if "start_time" not in jsn["data"]:
            jsn["data"]["start_time"] = self.currenttime()
        if "end_time" not in jsn["data"]:
            jsn["data"]["end_time"] = self.currenttime()
        data = json.loads(str(self.data.strip()))
        jsn["data"].update(data)
        return json.dumps(jsn)

    def run(self):
        """ the main program function
        """
        tdw = TangoDataWriter.TangoDataWriter()
        tdw.fileName = str(self.file)
        print("opening the %s file" % self.file)
        tdw.openFile()
        tdw.xmlsettings = self.xml

        print("opening the data entry ")
        if self.data and self.data.strip():
            tdw.jsonrecord = self.jsonstring()
        tdw.openEntry()
        for i in range(self.nrecords):
            print("recording the H5 file")
            tdw.jsonrecord = self.jsonstring()
            tdw.record()
            if self.nrecords > 1:
                print("sleeping for 1s")
                time.sleep(self.stime)
        print("closing the data entry ")
        tdw.jsonrecord = self.jsonstring()
        tdw.closeEntry()

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

    epilog = 'For more help:\n  nxsdata <sub-command> -h'
    parser = argparse.ArgumentParser(
        description=description, epilog=epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        'args', metavar='xml_config', type=str, nargs='?',
        help='nexus writer configuration string')
    parser.add_argument("-x", "--xml-file",
                        help="optional file with nexus "
                        "configuration string",
                        dest="xmlfile", default="")
    parser.add_argument("-p", "--parent",
                        help="nexus file name",
                        dest="parent", default="")
    parser.add_argument("-d", "--data",
                        help="json string with data",
                        dest="data", default="")
    parser.add_argument("-j", "--json-file",
                        help="json data file",
                        dest="jsonfile", default="")
    parser.add_argument(
        "-t", "--time",
        help="time between record steps in seconds, default: 1 s",
        dest="stime", default="1")
    parser.add_argument(
        "-n", "--nrecords",
        help="number of performed record steps",
        dest="nrecords", default="1")

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
    # result = runners[options.subparser].run(options)
    # if result and str(result).strip():
    #     print(result)


if __name__ == "__main__":
    main()
