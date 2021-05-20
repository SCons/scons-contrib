"""SCons.Tool.xetex

Tool-specific initialization for xelatex.
Generates .pdf files from .latex or .ltx files

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

#
# __COPYRIGHT__
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

import os
import SCons.Action
import SCons.Util
import SCons.Tool.pdf
import SCons.Tool.tex
import platform

XeTeXAction = None
XETEXBuilder = None

XeLaTeXAction = None
XELATEXBuilder = None


def XeLaTeXAuxFunction(target=None, source=None, env=None):
    result = SCons.Tool.tex.InternalLaTeXAuxAction(XeLaTeXAction, target, source, env)
    if result != 0:
        SCons.Tool.tex.check_file_error_message(env['XELATEX'])
    return result


XeLaTeXAuxAction = None


def XeTeXLaTeXStrFunction(target=None, source=None, env=None):
    """A strfunction for TeX and LaTeX that scans the source file to
    decide the "flavor" of the source and then returns the appropriate
    command string."""
    if env.GetOption("no_exec"):

        # find these paths for use in is_LaTeX to search for included files
        basedir = os.path.split(str(source[0]))[0]
        abspath = os.path.abspath(basedir)

        if is_LaTeX(source, env, abspath):
            result = env.subst('$XELATEXCOM', 0, target, source) + " ..."
        else:
            result = env.subst("$XETEXCOM", 0, target, source) + " ..."
    else:
        result = ''
    return result


def XeTeXLaTeXFunction(target=None, source=None, env=None):
    """A builder for XeTeX and XeLaTeX that scans the source file to
    decide the "flavor" of the source and then executes the appropriate
    program."""
    basedir = os.path.split(str(source[0]))[0]
    abspath = os.path.abspath(basedir)

    if SCons.Tool.tex.is_LaTeX(source, env, abspath):
        result = XeLaTeXAuxAction(target, source, env)
        if result != 0:
            SCons.Tool.tex.check_file_error_message(env['XELATEX'])
    else:
        result = XeTeXAction(target, source, env)
        if result != 0:
            SCons.Tool.tex.check_file_error_message(env['XETEX'])
    return result


XeTeXLaTeXAction = None


def generate(env):
    """Add Builders and construction variables for latex to an Environment."""
    global XeTeXAction
    if XeTeXAction is None:
        XeTeXAction = SCons.Action.Action('$XETEXCOM', '$XETEXCOMSTR')

    global XeTeXLaTeXAction
    if XeTeXLaTeXAction is None:
        XeTeXLaTeXAction = SCons.Action.Action(
            XeTeXLaTeXFunction, strfunction=XeTeXLaTeXStrFunction
        )

    global XeLaTeXAction
    if XeLaTeXAction is None:
        XeLaTeXAction = SCons.Action.Action('$XELATEXCOM', '$XELATEXCOMSTR')

    global XeLaTeXAuxAction
    if XeLaTeXAuxAction is None:
        XeLaTeXAuxAction = SCons.Action.Action(
            XeLaTeXAuxFunction, strfunction=XeTeXLaTeXStrFunction
        )

    env.AppendUnique(LATEXSUFFIXES=SCons.Tool.LaTeXSuffixes)

    try:
        env['BUILDERS']['XETEX']
    except KeyError:
        global XETEXBuilder
        if XETEXBuilder is None:
            XETEXBuilder = SCons.Builder.Builder(
                action={},
                source_scanner=SCons.Tool.PDFLaTeXScanner,
                prefix='$XETEXPREFIX',
                suffix='$XETEXSUFFIX',
                emitter={},
                source_ext_match=None,
                single_source=True,
            )
        env['BUILDERS']['XETEX'] = XETEXBuilder

    try:
        env['BUILDERS']['XELATEX']
    except KeyError:
        global XELATEXBuilder
        if XELATEXBuilder is None:
            XELATEXBuilder = SCons.Builder.Builder(
                action={},
                source_scanner=SCons.Tool.PDFLaTeXScanner,
                prefix='$XELATEXPREFIX',
                suffix='$XELATEXSUFFIX',
                emitter={},
                source_ext_match=None,
                single_source=True,
            )
        env['BUILDERS']['XELATEX'] = XELATEXBuilder

    env['XETEXPREFIX'] = ''
    env['XETEXSUFFIX'] = '.pdf'
    env['PDFSUFFIX'] = '.pdf'
    bld = env['BUILDERS']['XETEX']
    bld.add_action('.tex', XeTeXLaTeXAction)
    bld.add_emitter('.tex', SCons.Tool.tex.tex_pdf_emitter)

    env['XELATEXPREFIX'] = ''
    env['XELATEXSUFFIX'] = '.pdf'
    bld = env['BUILDERS']['XELATEX']
    bld.add_action('.ltx', XeLaTeXAuxAction)
    bld.add_action('.latex', XeLaTeXAuxAction)
    bld.add_emitter('.ltx', SCons.Tool.tex.tex_pdf_emitter)
    bld.add_emitter('.latex', SCons.Tool.tex.tex_pdf_emitter)

    SCons.Tool.tex.generate_common(env)

    CDCOM = 'cd '
    if platform.system() == 'Windows':
        # allow cd command to change drives on Windows
        CDCOM = 'cd /D '

    env['XETEX'] = 'xetex'
    env['XETEXFLAGS'] = SCons.Util.CLVar('-interaction=nonstopmode -recorder')
    env['XETEXCOM'] = CDCOM + '${TARGET.dir} && $XETEX $XETEXFLAGS ${SOURCE.file}'

    env['XELATEX'] = 'xelatex'
    env['XELATEXFLAGS'] = SCons.Util.CLVar('-interaction=nonstopmode -recorder')
    env['XELATEXCOM'] = CDCOM + '${TARGET.dir} && $XELATEX $XELATEXFLAGS ${SOURCE.file}'


def exists(env):
    return env.Detect(['xelatex', 'xetex'])


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
