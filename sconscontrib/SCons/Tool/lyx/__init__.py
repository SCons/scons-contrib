"""SCons.Tool.lyx

Tool-specific initialization for Lyx.

"""

#
# Copyright (c) 2016 The SCons Foundation
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

#
# Credits: The initial version of this Tool was contributed to the SCons wiki
#          at https://bitbucket.org/scons/scons/wiki/LyxBuilder by ?.
#

import SCons.Action
import SCons.Builder

#
# Scanners
#

#
# Emitters
#
def namelyxtarget(target, source, env):
    '''The name of the output tex file is the same as the input.'''
    assert len(source) == 1, 'Lyx is single_source only.'
    s = str(source[0])
    if s.endswith('.lyx'): 
        target[0] = s[0:-4] +'.tex'
    return target, source

#
# Builders
#
lyx_builder = SCons.Builder.Builder(
        action = SCons.Action.Action('$LYX_PDFCOM','$LYX_PDFCOMSTR'),
                                     suffix = '.tex', src_suffix='.lyx', 
                                     single_source=True, # file by file
                                     emitter = namelyxtarget)


def generate(env):
    """Add Builders and construction variables for lyx to an Environment."""
    env.SetDefault(
        LYX = 'lyx',
        LYXSRCSUFFIX = '.lyx',
        LYXTEXSUFFIX = '.tex',
        LYXFLAGS = '--export pdflatex',
        LYX_PDFCOM = '$LYX $LYXFLAGS $SOURCE',
        )

    env.Append(BUILDERS = {'Lyx' : lyx_builder})

    # Teach PDF to understand lyx
    env['BUILDERS']['PDF'].add_src_builder(lyx_builder)

        
def exists(env):
    return env.Detect('lyx')
