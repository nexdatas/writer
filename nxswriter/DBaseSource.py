#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2017 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

""" Definitions of DB datasource """

from xml.dom import minidom
import sys

from .Types import NTP

from .DataSources import DataSource
from .Errors import (PackageError, DataSourceSetupError)


#: (:obj:`list<str>`) list of available databases
DB_AVAILABLE = []

try:
    import MySQLdb
    DB_AVAILABLE.append("MYSQL")
except ImportError as e:
    pass
    # sys.stdout.write("MYSQL not available: %s\n" % e)

try:
    import psycopg2
    DB_AVAILABLE.append("PGSQL")
except ImportError as e:
    pass
    # sys.stdout.write("PGSQL not available: %s\n" % e)

try:
    import cx_Oracle
    DB_AVAILABLE.append("ORACLE")
except ImportError as e:
    pass
    # sys.stdout.write("ORACLE not available: %s\n" % e)


class DBaseSource(DataSource):

    """ DataBase data source
    """

    def __init__(self, streams=None):
        """ constructor

        :brief: It sets all member variables to None
        :param streams: tango-like steamset class
        :type streams: :class:`StreamSet` or :class:`PyTango.Device_4Impl`
        """
        DataSource.__init__(self, streams=streams)
        #: (:obj:`str`) name of the host with the data source
        self.hostname = None
        #: (:obj:`str`) port related to the host
        self.port = None
        #: (:obj:`str`) database query
        self.query = None
        #: (:obj:`str`) DSN string
        self.dsn = None
        #: (:obj:`str`) database type, i.e. MYSQL, PGSQL, ORACLE
        self.dbtype = None
        #: (:obj:`str`) oracle database mode
        self.mode = None
        #: (:obj:`str`) database name
        self.dbname = None
        #: (:obj:`str`) database user
        self.user = None
        #: (:obj:`str`) database password
        self.passwd = None
        #: (:obj:`str`) mysql database configuration file
        self.mycnf = '/etc/my.cnf'
        #: (:obj:`str`) record format, i.e. `SCALAR`, `SPECTRUM`, `IMAGE`
        self.format = None

        #: (:obj:`dict` <:obj:`str`, :obj:`instancemethod`>) map
        self.__dbConnect = {"MYSQL": self.__connectMYSQL,
                            "PGSQL": self.__connectPGSQL,
                            "ORACLE": self.__connectORACLE}

    def __str__(self):
        """ self-description

        :returns: self-describing string
        :rtype: :obj:`str`
        """
        return " %s DB %s with %s " % (
            self.dbtype, self.dbname if self.dbname else "", self.query)

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml: datasource parameters
        :type xml: :obj:`str`
        :raises: :exc:`nxswriter.Errors.DataSourceSetupError`
            if :obj:`format` or :obj:`query` is not defined
        """
        dom = minidom.parseString(xml)
        query = dom.getElementsByTagName("query")
        if query and len(query) > 0:
            self.format = query[0].getAttribute("format") \
                if query[0].hasAttribute("format") else None
            self.query = self._getText(query[0])

        if not self.format or not self.query:
            if self._streams:
                self._streams.error(
                    "DBaseSource::setup() - "
                    "Database query or its format not defined: %s" % xml,
                    std=False)

            raise DataSourceSetupError(
                "Database query or its format not defined: %s" % xml)

        db = dom.getElementsByTagName("database")
        if db and len(db) > 0:
            self.dbname = db[0].getAttribute("dbname") \
                if db[0].hasAttribute("dbname") else None
            self.dbtype = db[0].getAttribute("dbtype") \
                if db[0].hasAttribute("dbtype") else None
            self.user = db[0].getAttribute("user")  \
                if db[0].hasAttribute("user") else None
            self.passwd = db[0].getAttribute("passwd") \
                if db[0].hasAttribute("passwd") else None
            self.mode = db[0].getAttribute("mode") \
                if db[0].hasAttribute("mode") else None
            mycnf = db[0].getAttribute("mycnf") \
                if db[0].hasAttribute("mycnf") else None
            if mycnf:
                self.mycnf = mycnf
            self.hostname = db[0].getAttribute("hostname") \
                if db[0].hasAttribute("hostname") else None
            self.port = db[0].getAttribute("port") \
                if db[0].hasAttribute("port") else None
            self.dsn = self._getText(db[0])

    def __connectMYSQL(self):
        """ connects to MYSQL database

        :returns: open database object
        :rtype: :class:`MySQLdb.connections.Connection`
        """
        args = {}
        if self.mycnf:
            args["read_default_file"] = self.mycnf
        if self.dbname:
            args["db"] = self.dbname
        if self.user:
            args["user"] = self.user
        if self.passwd:
            args["passwd"] = self.passwd
        if self.hostname:
            args["host"] = self.hostname
        if sys.version_info < (3,):
            for k in list(args.keys()):
                args[k] = args[k].encode()

        if self.port:
            args["port"] = int(self.port)
        return MySQLdb.connect(**args)

    def __connectPGSQL(self):
        """ connects to PGSQL database

        :returns: open database object
        :rtype: :class:`psycopg2._psycopg.connection`
        """
        args = {}

        if self.dbname:
            args["database"] = self.dbname
        if self.user:
            args["user"] = self.user
        if self.passwd:
            args["password"] = self.passwd
        if self.hostname:
            args["host"] = self.hostname
        if sys.version_info < (3,):
            for k in list(args.keys()):
                args[k] = args[k].encode()

        if self.port:
            args["port"] = int(self.port)

        return psycopg2.connect(**args)

    def __connectORACLE(self):
        """ connects to ORACLE database

        :returns: open database object
        :rtype: :class:`cx_Oracle.Connection`
        """
        args = {}
        if self.user:
            args["user"] = self.user.encode()
        if self.passwd:
            args["password"] = self.passwd.encode()
        if self.dsn:
            args["dsn"] = self.dsn.encode()
        if self.mode:
            args["mode"] = self.mode.encode()

        return cx_Oracle.connect(**args)

    def getData(self):
        """ provides access to the data

        :returns: dictionary with collected data
        :rtype: :obj:`dict` <:obj:`str`, any>
        """

        db = None

        if self.dbtype in self.__dbConnect.keys() \
                and self.dbtype in DB_AVAILABLE:
            db = self.__dbConnect[self.dbtype]()
        else:
            if self._streams:
                self._streams.error(
                    "DBaseSource::getData() - "
                    "Support for %s database not available" % self.dbtype,
                    std=False)

            raise PackageError(
                "Support for %s database not available" % self.dbtype)

        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
                #  data = copy.deepcopy(cursor.fetchone())
                data = cursor.fetchone()
                dh = {"rank": "SCALAR",
                      "value": data[0],
                      "tangoDType": (NTP.pTt[type(data[0]).__name__]),
                      "shape": [1, 0]}
            elif self.format == 'SPECTRUM':
                data = cursor.fetchall()
                # data = copy.deepcopy(cursor.fetchall())
                if len(data[0]) == 1:
                    ldata = list(el[0] for el in data)
                else:
                    ldata = list(el for el in data[0])
                dh = {"rank": "SPECTRUM",
                      "value": ldata,
                      "tangoDType": (NTP.pTt[type(ldata[0]).__name__]),
                      "shape": [len(ldata), 0]}
            else:
                data = cursor.fetchall()
                # data = copy.deepcopy(cursor.fetchall())
                ldata = list(list(el) for el in data)
                dh = {"rank": "IMAGE",
                      "value": ldata,
                      "tangoDType": NTP.pTt[type(ldata[0][0]).__name__],
                      "shape": [len(ldata), len(ldata[0])]}
            cursor.close()
            db.close()
        return dh
