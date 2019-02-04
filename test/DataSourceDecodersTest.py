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
# \package test nexdatas
# \file DataSourceDecodersTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys
import struct
import json


from nxswriter.DataSourceFactory import DataSourceFactory
from nxswriter import TangoSource
from nxswriter.DataSourcePool import DataSourcePool
from nxswriter.Element import Element
from nxswriter.EField import EField

try:
    import SimpleServerSetUp
except Exception:
    from . import SimpleServerSetUp

from nxswriter.DecoderPool import DecoderPool

# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class DataSourceDecodersTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._simps = SimpleServerSetUp.SimpleServerSetUp()
        self._tfname = "doc"
        self._fname = "test.h5"
        self._nxDoc = None
        self._eDoc = None
        self._fattrs = {"short_name": "test", "units": "m"}
        self._gname = "testDoc"
        self._gtype = "NXentry"

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name": "test", "units": "m"}

    # test starter
    # \brief Common set up
    def setUp(self):
        # file handle
        self._simps.setUp()

    # test closer
    # \brief Common tear down
    def tearDown(self):
        self._simps.tearDown()

    # Exception tester
    # \param exception expected exception
    # \param method called method
    # \param args list with method arguments
    # \param kwargs dictionary with method arguments
    def myAssertRaise(self, exception, method, *args, **kwargs):
        try:
            error = False
            method(*args, **kwargs)
        except Exception:
            error = True
        self.assertEqual(error, True)

    # Data check
    # \brief It check the source Data
    # \param data  tested data
    # \param dformat data format
    # \param value data value
    # \param ttype data Tango type
    # \param shape data shape
    # \param shape data shape
    # \param encoding data encoding
    # \param encoding data encoding
    # \param decoders data decoders
    # \param error data error
    def checkData(self, data, dformat, value, ttype, shape, encoding=None,
                  decoders=None, error=0):
        self.assertEqual(data["rank"], dformat)
        self.assertEqual(data["tangoDType"], ttype)
        self.assertEqual(data["shape"], shape)
        if encoding is not None:
            self.assertEqual(data["encoding"], encoding)
        if decoders is not None:
            self.assertEqual(data["decoders"], decoders)
        if dformat == 'SCALAR':
            if error:
                self.assertTrue(abs(data["value"] - value) <= error)
            else:
                self.assertEqual(data["value"], value)
        elif dformat == 'SPECTRUM':
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                if error:
                    self.assertTrue(abs(data["value"][i] - value[i]) <= error)
                else:
                    self.assertEqual(data["value"][i], value[i])
        else:
            self.assertEqual(len(data["value"]), len(value))
            for i in range(len(value)):
                self.assertEqual(len(data["value"][i]), len(value[i]))
                for j in range(len(value[i])):
                    if error:
                        self.assertTrue(
                            abs(data["value"][i][j] - value[i][j]) <= error)
                    else:
                        self.assertEqual(data["value"][i][j], value[i][j])

    # constructor test
    # \brief It tests default settings
    def test_setDecoders(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        atype = 'attribute'
        # encoding = 'UTF8'
        # decoders =
        DecoderPool()

        atts = {"type": "TANGO"}
        # name = "myRecord"
        # wjson = json.loads(
        #     '{"datasources":{"CL":"ClientSource.ClientSource"}}')
        gjson = json.loads('{"data":{"myRecord":"1"}}')

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8", b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr3:
            print(k)
            el = EField(self._fattrs, None)
            ds = DataSourceFactory(atts, el)
            self.assertTrue(isinstance(ds, Element))
            self.assertEqual(ds.tagName, "datasource")
            self.assertEqual(ds._tagAttrs, atts)
            self.assertEqual(ds.content, [])
            self.assertEqual(ds.doc, "")
            self.assertEqual(ds.last, el)
            self.assertEqual(ds.setDataSources(DataSourcePool()), None)
            self.assertEqual(
                ds.store(
                    ["<datasource type='TANGO'>",
                     "<record name='%s'/> <device name='%s' encoding='%s'/>" %
                     (k, device, arr3[k][2][0]),
                     "</datasource>"],
                    gjson),
                None)
            self.assertEqual(type(ds.last.source), TangoSource.TangoSource)
            self.assertEqual(ds.last.source.member.name, k)
            self.assertEqual(ds.last.source.device, device)
            self.assertEqual(ds.last.source.member.encoding, arr3[k][2][0])
            self.assertEqual(
                ds.last.source.__str__(), " TANGO Device %s : %s (%s)"
                % (device, k, atype))
            self.assertEqual(len(ds.last.tagAttributes), 1)
            self.assertEqual(
                ds.last.tagAttributes["nexdatas_source"],
                ('NX_CHAR', "<datasource type='TANGO'><record name='%s'/> "
                 "<device name='stestp09/testss/s1r228' encoding='%s'/>"
                 "</datasource>" % (k, arr3[k][2][0])))
            dp = DecoderPool()
            self.assertEqual(ds.setDecoders(dp), None)
            dt = ds.last.source.getData()
            self.checkData(
                dt, "SCALAR", arr3[k][2], arr3[k][1], [1, 0],
                arr3[k][2][0], dp)

    # constructor test
    # \brief It tests default settings
    def test_setDecoders_nopool(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        device = 'stestp09/testss/s1r228'
        atype = 'attribute'
        # encoding = 'UTF8'
        # decoders =
        DecoderPool()

        atts = {"type": "TANGO"}
        # name = "myRecord"
        # wjson = json.loads(
        #     '{"datasources":{"CL":"nxswriter.ClientSource.ClientSource"}}')
        gjson = json.loads('{"data":{"myRecord":"1"}}')

        arr3 = {
            "ScalarEncoded": [
                "string", "DevEncoded",
                ("UTF8",
                 b"Hello UTF8! Pr\xc3\xb3ba \xe6\xb5\x8b")],
            "SpectrumEncoded": [
                "string", "DevEncoded",
                ('INT32',
                 b'\xd2\x04\x00\x00.\x16\x00\x00-\x00\x00\x00Y\x01\x00\x00')],
        }

        for k in arr3:

            el = EField(self._fattrs, None)
            ds = DataSourceFactory(atts, el)
            self.assertTrue(isinstance(ds, Element))
            self.assertEqual(ds.tagName, "datasource")
            self.assertEqual(ds._tagAttrs, atts)
            self.assertEqual(ds.content, [])
            self.assertEqual(ds.doc, "")
            self.assertEqual(ds.last, el)
            self.assertEqual(ds.setDataSources(DataSourcePool()), None)
            self.assertEqual(ds.store(
                ["<datasource type='TANGO'>",
                 "<record name='%s'/> <device name='%s' encoding='%s'/>" % (
                     k, device, arr3[k][2][0]),
                 "</datasource>"], gjson), None)
            self.assertEqual(type(ds.last.source), TangoSource.TangoSource)
            self.assertEqual(ds.last.source.member.name, k)
            self.assertEqual(ds.last.source.device, device)
            self.assertEqual(ds.last.source.member.encoding, arr3[k][2][0])
            self.assertEqual(
                ds.last.source.__str__(),
                " TANGO Device %s : %s (%s)" % (device, k, atype))
            self.assertEqual(len(ds.last.tagAttributes), 1)
            self.assertEqual(ds.last.tagAttributes["nexdatas_source"], (
                'NX_CHAR',
                "<datasource type='TANGO'><record name='%s'/> "
                "<device name='stestp09/testss/s1r228' encoding='%s'/>"
                "</datasource>" % (k, arr3[k][2][0])))
            # dp =
            DecoderPool()
            self.assertEqual(ds.setDecoders(None), None)
            dt = ds.last.source.getData()
            self.checkData(dt, "SCALAR", arr3[k][2], arr3[k][1],
                           [1, 0], arr3[k][2][0], None)


if __name__ == '__main__':
    unittest.main()
