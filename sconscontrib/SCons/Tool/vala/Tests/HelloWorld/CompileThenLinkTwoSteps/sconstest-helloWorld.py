# -*- coding:utf-8; -*-

#
#   Copyright © 2012 Russel Winder
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
#

#  Author: Russel Winder <russel@winder.org.uk>
#  Date: 2012-07-03T06:33+01:00

import TestSCons


def runProgramAndTestOutput(variant):
    test.run(program=test.workpath('helloWorld{}{}'.format(variant, TestSCons._exe)))
    test.fail_test(test.stdout() != 'Hello World.\n')


test = TestSCons.TestSCons()

test.dir_fixture('Project')
test.file_fixture('../../../vala.py')

if not test.where_is('vala'):
    test.skip_test('Could not find vala tool, skipping test.\n')

test.run()

for item in ['helloWorldFunction', 'helloWorldObject', 'helloWorldWindow']:
    for ext in ['.c', '.o', '']:
        test.must_exist(test.workpath(item + ext))

runProgramAndTestOutput('Function')
runProgramAndTestOutput('Object')

test.pass_test()
