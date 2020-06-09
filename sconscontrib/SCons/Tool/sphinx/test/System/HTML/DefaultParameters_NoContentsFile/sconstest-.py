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

'''
A test to show that using the default parameters to the HTML builder works as required.
'''

__author__ = 'Russel Winder <russel@russel.org.uk>'
__date__ = '2011-08-31'

import os
import sys

sys.path.append ( os.path.realpath ( os.path.dirname ( __file__ ) + '/../..' ) )

from common import setUpTest

import TestSCons

test = TestSCons.TestSCons ( )
setUpTest ( test )
#test.run ( )
test.run ( stderr = r'''.*WARNING: master file.*source/contents.rst not found.*
.*build/doctrees/contents.doctree.*''' , match = TestSCons.match_re_dotall , status = 2 )
test.must_exist ( test.workpath ( 'build/doctrees/environment.pickle' ) )
test.must_exist ( test.workpath ( 'build/doctrees/file.doctree' ) )
test.pass_test ( )
