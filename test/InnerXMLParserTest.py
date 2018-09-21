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
# \file InnerXMLParserTest.py
# unittests for field Tags running Tango Server
#
import unittest
import sys
import struct

from xml import sax

from nxswriter.InnerXMLParser import InnerXMLHandler


try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO


# if 64-bit machione
IS64BIT = (struct.calcsize("P") == 8)


# test fixture
class InnerXMLParserTest(unittest.TestCase):

    # constructor
    # \param methodName name of the test method

    def __init__(self, methodName):
        unittest.TestCase.__init__(self, methodName)

        self._tfname = "field"
        self._tfname = "group"
        self._fattrs = {"short_name": "test", "units": "m"}

        self._bint = "int64" if IS64BIT else "int32"
        self._buint = "uint64" if IS64BIT else "uint32"
        self._bfloat = "float64" if IS64BIT else "float32"

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

    # test starter
    # \brief Common set up
    def setUp(self):
        print("\nsetting up...")

    # test closer
    # \brief Common tear down
    def tearDown(self):
        print("tearing down ...")

    # constructor test
    # \brief It tests default settings
    def test_constructor(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        name = "datasource"
        attrs = {"type": "TANGO"}
        el = InnerXMLHandler(parser, handler, name, attrs)
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO('<device> Something</device>'))
        parser.parse(inpsrc)

        self.assertEqual(parser.getContentHandler(), el)

        self.assertEqual(el.endElement("datasource"), None)
        self.assertEqual(len(el.xml), 3)
        self.assertEqual(el.xml[0], '<datasource type="TANGO">')
        self.assertEqual(el.xml[1], '<device> Something</device>')
        self.assertEqual(el.xml[2], '</datasource>')

        self.assertEqual(parser.getContentHandler(), handler)

    # constructor test
    # \brief It tests default settings
    def test_group_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        name = "datasource"
        attrs = {}
        el = InnerXMLHandler(parser, handler, name, attrs)
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)
        self.assertTrue(isinstance(el, sax.ContentHandler))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("datasource"), None)
        self.assertTrue(
            (
                el.xml ==
                ('<datasource>',
                 '<group type="NXentry" name="entry"></group>',
                 '</datasource>')
            ) or
            (
                el.xml ==
                ('<datasource>',
                 '<group name="entry" type="NXentry"></group>',
                 '</datasource>')
            )
        )

    # constructor test
    # \brief It tests default settings
    def test_group_names(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "instrument", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        name = "group"
        attrs = {}
        el = InnerXMLHandler(parser, handler, name, attrs)
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)
        self.assertTrue(isinstance(el, sax.ContentHandler))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.startElement("field", attr2), None)
        self.assertEqual(el.endElement("field"), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(len(el.xml), 3)
        self.assertEqual(el.xml[0], '<group>')
        self.assertTrue(
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1"></group>'
                '<field type="NXinstrument" name="instrument"></field>'
            ) or
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1"></group>'
                '<field name="instrument" type="NXinstrument"></field>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry"></group>'
                '<field type="NXinstrument" name="instrument"></field>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry"></group>'
                '<field name="instrument" type="NXinstrument"></field>'
            )
        )
        self.assertEqual(el.xml[2], '</group>')

    # constructor test
    # \brief It tests default settings
    def test_group_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "instrument", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        name = "group"
        attrs = {"type": "NXentry"}
        el = InnerXMLHandler(parser, handler, name, attrs)
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)
        self.assertTrue(isinstance(el, sax.ContentHandler))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.startElement("group", attr2), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(len(el.xml), 3)
        self.assertEqual(el.xml[0], '<group type="NXentry">')
        self.assertTrue(
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1">'
                '<group type="NXinstrument" name="instrument"></group></group>'
            ) or
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1">'
                '<group name="instrument" type="NXinstrument"></group></group>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry">'
                '<group type="NXinstrument" name="instrument"></group></group>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry">'
                '<group name="instrument" type="NXinstrument"></group></group>'
            )
        )
        self.assertEqual(el.xml[2], '</group>')

    # constructor test
    # \brief It tests default settings
    def test_group_field(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        attr1 = {"name": "entry1", "type": "NXentry"}
        # sattr1 = {attr1["type"]: attr1["name"]}

        attr2 = {"name": "instrument", "type": "NXinstrument"}
        # sattr2 = {attr2["type"]: attr2["name"]}

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        name = "group"
        attrs = {}
        el = InnerXMLHandler(parser, handler, name, attrs)
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)
        self.assertTrue(isinstance(el, sax.ContentHandler))
        self.assertEqual(el.startElement("group", attr1), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(el.startElement("attribute", attr2), None)
        self.assertEqual(el.endElement("attribute"), None)
        self.assertEqual(el.endElement("group"), None)
        self.assertEqual(len(el.xml), 3)
        self.assertEqual(el.xml[0], '<group>')
        self.assertTrue(
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1"></group>'
                '<attribute type="NXinstrument" name="instrument"></attribute>'
            ) or
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1"></group>'
                '<attribute name="instrument" type="NXinstrument"></attribute>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry"></group>'
                '<attribute type="NXinstrument" name="instrument"></attribute>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry"></group>'
                '<attribute name="instrument" type="NXinstrument"></attribute>'
            )
        )
        self.assertEqual(el.xml[2], '</group>')

    # constructor test
    # \brief It tests default settings
    def test_XML_group_name(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        name = "datasource"

        el = InnerXMLHandler(parser, handler, name, {})
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(
            StringIO('<group type="NXentry" name="entry"></group>'))
        parser.parse(inpsrc)

        self.assertEqual(parser.getContentHandler(), el)

        self.assertEqual(el.endElement("datasource"), None)

        self.assertTrue(
            (
                el.xml ==
                ('<datasource>',
                 '<group type="NXentry" name="entry"></group>',
                 '</datasource>')
            ) or
            (
                el.xml ==
                ('<datasource>',
                 '<group name="entry" type="NXentry"></group>',
                 '</datasource>')
            )
        )

        self.assertEqual(parser.getContentHandler(), handler)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_names(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        name = "group"
        xml = '<group type="NXentry" name="entry1">' + \
              '<field type="NXinstrument" name="instrument"></field></group>'
#        xml = '<group type="NXentry" name="entry1"></group>'

        el = InnerXMLHandler(parser, handler, name, {})
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO(xml))
        parser.parse(inpsrc)

        self.assertEqual(parser.getContentHandler(), el)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(len(el.xml), 3)
        self.assertEqual(el.xml[0], '<group>')
        self.assertTrue(
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1">'
                '<field type="NXinstrument" name="instrument"></field></group>'
            ) or
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1">'
                '<field name="instrument" type="NXinstrument"></field></group>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry">'
                '<field type="NXinstrument" name="instrument"></field></group>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry">'
                '<field name="instrument" type="NXinstrument"></field></group>'
            )
        )
        self.assertEqual(el.xml[2], '</group>')

        self.assertEqual(parser.getContentHandler(), handler)

    # constructor test
    # \brief It tests default settings
    def test_XML_group_group(self):
        fun = sys._getframe().f_code.co_name
        print("Run: %s.%s() " % (self.__class__.__name__, fun))

        parser = sax.make_parser()
        handler = sax.ContentHandler()
        attrs = {"type": "NXentry"}

        name = "group"
        xml = '<group type="NXentry" name="entry1">' + \
              '<group type="NXinstrument" name="instrument"></group></group>'

        el = InnerXMLHandler(parser, handler, name, attrs)
        parser.setContentHandler(el)
        self.assertEqual(el.xml, None)

        inpsrc = sax.InputSource()
        inpsrc.setByteStream(StringIO(xml))
        parser.parse(inpsrc)

        self.assertEqual(parser.getContentHandler(), el)
        self.assertEqual(el.endElement("group"), None)

        self.assertEqual(len(el.xml), 3)
        self.assertEqual(el.xml[0], '<group type="NXentry">')
        self.assertTrue(
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1">'
                '<group type="NXinstrument" name="instrument"></group></group>'
            ) or
            (
                el.xml[1] ==
                '<group type="NXentry" name="entry1">'
                '<group name="instrument" type="NXinstrument"></group></group>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry">'
                '<group type="NXinstrument" name="instrument"></group></group>'
            ) or
            (
                el.xml[1] ==
                '<group name="entry1" type="NXentry">'
                '<group name="instrument" type="NXinstrument"></group></group>'
            )
        )
        self.assertEqual(el.xml[2], '</group>')

        self.assertEqual(parser.getContentHandler(), handler)


if __name__ == '__main__':
    unittest.main()
