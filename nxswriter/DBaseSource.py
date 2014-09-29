#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2014 DESY, Jan Kotanski <jkotan@mail.desy.de>
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
## \package nxswriter nexdatas
## \file DBaseSource.py
# data-source types

""" Definitions of DB datasource """

import sys
from xml.dom import minidom

from .Types import NTP
from . import Streams

from .DataSources import DataSource
from .Errors import (PackageError, DataSourceSetupError)


## list of available databases
DB_AVAILABLE = []

try:
    import MySQLdb
    DB_AVAILABLE.append("MYSQL")
except ImportError, e:
    print >> sys.stdout, "MYSQL not available: %s" % e
    if Streams.log_info:
        print >> Streams.log_info, "MYSQL not available: %s" % e

try:
    import psycopg2
    DB_AVAILABLE.append("PGSQL")
except ImportError, e:
    print >> sys.stdout, "PGSQL not available: %s" % e
    if Streams.log_info:
        print >> Streams.log_info,  "PGSQL not available: %s" % e

try:
    import cx_Oracle
    DB_AVAILABLE.append("ORACLE")
except ImportError, e:
    print >> sys.stdout, "ORACLE not available: %s" % e
    if Streams.log_info:
        print >> Streams.log_info, "ORACLE not available: %s" % e


## DataBase data source
class DBaseSource(DataSource):
    ## constructor
    # \brief It cleans all member variables
    def __init__(self):
        DataSource.__init__(self)
        ## name of the host with the data source
        self.hostname = None
        ## port related to the host
        self.port = None
        ## database query
        self.query = None
        ## DSN string
        self.dsn = None
        ## database type, i.e. MYSQL, PGSQL, ORACLE
        self.dbtype = None
        ## oracle database mode
        self.mode = None
        ## database name
        self.dbname = None
        ## database user
        self.user = None
        ## database password
        self.passwd = None
        ## mysql database configuration file
        self.mycnf = '/etc/my.cnf'
        ## record format, i.e. SCALAR, SPECTRUM, IMAGE
        self.format = None

        ## map
        self.__dbConnect = {"MYSQL": self.__connectMYSQL,
                            "PGSQL": self.__connectPGSQL,
                            "ORACLE": self.__connectORACLE}

    ## self-description
    # \returns self-describing string
    def __str__(self):
        return " %s DB %s with %s " % (
            self.dbtype, self.dbname if self.dbname else "", self.query)

    ## sets the parrameters up from xml
    # \brief xml  datasource parameters
    def setup(self, xml):
        dom = minidom.parseString(xml)
        query = dom.getElementsByTagName("query")
        if query and len(query) > 0:
            self.format = query[0].getAttribute("format") \
                if query[0].hasAttribute("format") else None
            self.query = self._getText(query[0])

        if not self.format or not self.query:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "DBaseSource::setup() - "\
                    "Database query or its format not defined: %s" % xml
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

    ## connects to MYSQL database
    # \returns open database object
    def __connectMYSQL(self):
        args = {}
        if self.mycnf:
            args["read_default_file"] = self.mycnf.encode()
        if self.dbname:
            args["db"] = self.dbname.encode()
        if self.user:
            args["user"] = self.user.encode()
        if self.passwd:
            args["passwd"] = self.passwd.encode()
        if self.hostname:
            args["host"] = self.hostname.encode()
        if self.port:
            args["port"] = int(self.port)
        return MySQLdb.connect(**args)

    ## connects to PGSQL database
    # \returns open database object
    def __connectPGSQL(self):
        args = {}

        if self.dbname:
            args["database"] = self.dbname.encode()
        if self.user:
            args["user"] = self.user.encode()
        if self.passwd:
            args["password"] = self.passwd.encode()
        if self.hostname:
            args["host"] = self.hostname.encode()
        if self.port:
            args["port"] = int(self.port)

        return psycopg2.connect(**args)

    ## connects to ORACLE database
    # \returns open database object
    def __connectORACLE(self):
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

    ## provides access to the data
    # \returns  dictionary with collected data
    def getData(self):

        db = None

        if self.dbtype in self.__dbConnect.keys() \
                and self.dbtype in DB_AVAILABLE:
            db = self.__dbConnect[self.dbtype]()
        else:
            if Streams.log_error:
                print >> Streams.log_error, \
                    "DBaseSource::getData() - "\
                    "Support for %s database not available" % self.dbtype
            raise PackageError(
                "Support for %s database not available" % self.dbtype)

        if db:
            cursor = db.cursor()
            cursor.execute(self.query)
            if not self.format or self.format == 'SCALAR':
#                data = copy.deepcopy(cursor.fetchone())
                data = cursor.fetchone()
                dh = {"rank": "SCALAR",
                      "value": data[0],
                      "tangoDType": (NTP.pTt[type(data[0]).__name__]),
                      "shape": [1, 0]}
            elif self.format == 'SPECTRUM':
                data = cursor.fetchall()
#                data = copy.deepcopy(cursor.fetchall())
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
#                data = copy.deepcopy(cursor.fetchall())
                ldata = list(list(el) for el in data)
                dh = {"rank": "IMAGE",
                      "value": ldata,
                      "tangoDType": NTP.pTt[type(ldata[0][0]).__name__],
                      "shape": [len(ldata), len(ldata[0])]}
            cursor.close()
            db.close()
        return dh
