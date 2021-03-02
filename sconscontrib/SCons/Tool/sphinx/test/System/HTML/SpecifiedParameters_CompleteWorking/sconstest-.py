# -*- mode:python; coding:utf-8 -*-

#  A SCons tool to enable Sphinx processing.
#
#  Copyright © 2011 Russel Winder
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
A test to show that specifying source and target parameters to the HTML builder works as required.
"""

__author__ = "Russel Winder <russel@russel.org.uk>"
__date__ = "2011-09-01"

import os
import sys

sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../.."))

from common import setUpTest

import TestSCons

test = TestSCons.TestSCons()
setUpTest(test)
# test.run ( )
test.run(
    stderr=r""".*WARNING: document isn't included in any toctree""",
    match=TestSCons.match_re_dotall,
)
for item in ["environment.pickle", "file.doctree", "contents.doctree"]:
    test.must_exist(test.workpath("flobadob/doctrees/" + item))
for item in (
    [
        "contents.html",
        "file.html",
        "genindex.html",
        "objects.inv",
        "search.html",
        "searchindex.js",
    ]
    + ["_sources/" + i for i in ["contents.txt", "file.txt"]]
    + [
        "_static/" + i
        for i in [
            "basic.css",
            "default.css",
            "doctools.js",
            "file.png",
            "jquery.js",
            "minus.png",
            "plus.png",
            "pygments.css",
            "searchtools.js",
            "sidebar.js",
            "underscore.js",
        ]
    ]
):
    test.must_exist(test.workpath("flobadob/html/" + item))


test.pass_test()
