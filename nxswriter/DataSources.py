#!/usr/bin/env python
#   This file is part of nexdatas - Tango Server for NeXus data writer
#
#    Copyright (C) 2012-2016 DESY, Jan Kotanski <jkotan@mail.desy.de>
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

""" Definitions of various datasources """

from .Types import NTP


class DataSource(object):
    """ Data source
    """
    def __init__(self):
        """ constructor

        :brief: It cleans all member variables
        """
        pass

    def setup(self, xml):
        """ sets the parrameters up from xml

        :param xml:  datasource parameters
        """
        pass

    def getData(self):
        """ access to data

        :brief: It is an abstract method providing data
        """
        pass

    def isValid(self):
        """ checks if the data is valid

        :returns: if the data is valid
        """
        return True

    def __str__(self):
        """ self-description

        :returns: self-describing string
        """
        return "unknown DataSource"

    @classmethod
    def _getText(cls, node):
        """ provides xml content of the node

        :param node: DOM node
        :returns: xml content string
        """
        xml = node.toxml()
        start = xml.find('>')
        end = xml.rfind('<')
        if start == -1 or end < start:
            return ""
        return xml[start + 1:end].replace("&lt;", "<").\
            replace("&gt;", ">").replace("&quot;", "\"").\
            replace("&amp;", "&")

    @classmethod
    def _getJSONData(cls, name, globalJSON, localJSON):
        """ provides access to the data

        :returns: dictionary with collected data
        """
        if globalJSON and 'data' not in globalJSON.keys():
            globalJSON = None

        if localJSON and 'data' not in localJSON.keys():
            localJSON = None

        rec = None
        if localJSON and 'data' in localJSON \
                and name in localJSON['data']:
            rec = localJSON['data'][str(name)]
        elif globalJSON and 'data' in globalJSON \
                and name in globalJSON['data']:
            rec = globalJSON['data'][str(name)]
        else:
            return
        ntp = NTP()
        rank, shape, pythonDType = ntp.arrayRankShape(rec)

        if rank in NTP.rTf:
            if shape is None:
                shape = [1, 0]
            return {"rank": NTP.rTf[rank],
                    "value": rec,
                    "tangoDType": NTP.pTt[pythonDType.__name__],
                    "shape": shape}
