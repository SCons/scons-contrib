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
Various code items used by all the tests.
'''

__author__ = 'Russel Winder <russel@russel.org.uk>'
__date__ = '2011-08-31'

import os

thisFilePath = os.path.dirname ( __file__ )

def setUpTest ( test ) :
    '''
    The project containing the SConstruct file is called project by convention for all tests, so set it up
    as a fixture.  The sphinx tool code must be copied over as a fixture.  The code here is dependent on the
    code of the tool.
    '''
    test.dir_fixture ( 'project' )
    test.file_fixture ( thisFilePath + '/../../__init__.py' , 'site_scons/site_tools/sphinx/__init__.py' )
