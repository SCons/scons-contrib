#!/usr/bin/python
# -*- coding=utf-8; -*-

# Tests for SCons Doxygen builder.
#
# Copyright © 2013  Richard van der Hoff
# Copyright © 2013  Russel Winder
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 2.1 as published by the Free Software Foundation.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import unittest
import os
import sys
from doxygen import DoxyfileParse


class TestParser(unittest.TestCase):
    test_config_dir = os.path.join(os.path.dirname(__file__), 'test_config')

    def test_simple_parse(self):
        text = """
# comment
INPUT  = test.h
"""
        result = DoxyfileParse(text, self.test_config_dir)
        self.assertEqual(["test.h"], result["INPUT"])

    def test_parse_tag_on_first_line(self):
        text = """INPUT=."""
        result = DoxyfileParse(text, self.test_config_dir)
        self.assertEqual(["."], result["INPUT"])

    def test_include_tag(self):
        text = """@INCLUDE=include_test.cfg"""
        result = DoxyfileParse(text, self.test_config_dir)
        self.assertEqual(["abc"], result["INPUT"])
        self.assertEqual([os.path.join(self.test_config_dir, "include_test.cfg")],
                         result["@INCLUDE"])

    def test_recursive_include_tag(self):
        text = """@INCLUDE=recursive_include_test.cfg"""
        self.assertRaises(Exception, DoxyfileParse, text, self.test_config_dir)


if __name__ == '__main__':
    unittest.main()
