"""SCons.Tool.rest

Tool-specific initialization for the ReST builders.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

#
# Copyright (c) 2001-7,2010,2011,2012 The SCons Foundation
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

import os

import SCons.Action
import SCons.Builder
import SCons.Util

try:
    import locale
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

has_docutils = True
try:
    from docutils.core import publish_file
    from docutils.core import publish_cmdline_to_binary
    from docutils.frontend import Values
    from docutils.writers.odf_odt import Writer
    from docutils.writers.odf_odt import Reader
except:
    has_docutils = False


def rst2something(target, source, env, validOptions, writer):
    if not has_docutils:
        return

    # Find variables that can be passed to docutils.
    settings = dict([item for item in env.items() if item[0] in validOptions])

    # stylesheet and stylesheet_path are mutually exclusive
    if 'stylesheet' in settings:
        settings['stylesheet_path'] = None

    for i in range(len(source)):
        publish_file(source_path=source[i].path,
                     destination_path=target[i].path,
                     writer_name=writer,
                     settings_overrides=settings)

#
# Warnings
#
class ToolReSTWarning(SCons.Warnings.Warning):
    pass

class ReSTNotFound(ToolReSTWarning):
    pass

SCons.Warnings.enableWarningClass(ToolReSTWarning)

#
# Detect tool
#
def _detect(env):
    """ Try to detect the ReST command line tools, here rst2html """
    rest = env.WhereIs('rst2html')
    if rest:
        return rest

    raise SCons.Errors.StopError(
        ReSTNotFound,
        "Could not detect ReST builder")
    return None

#
# Actions
#
def rst2latex(target, source, env):
    options = ['stylesheet', 'embed_stylesheet']
    rst2something(target, source, env, options, 'latex')
    return None

def rst2html(target, source, env):
    options = ['stylesheet', 'embed_stylesheet']
    rst2something(target, source, env, options, 'html4css1')
    return None

def rst2odt(target, source, env):
    if not has_docutils:
        return None

    writer = Writer()
    reader = Reader()
    for i in range(len(source)):
        publish_cmdline_to_binary(reader=reader, writer=writer, argv=[str(source[i]), str(target[i])])
    return None

#
# Builders
#
__rest_latexbuilder = SCons.Builder.Builder(
        action = rst2latex,
        suffix = '$REST_LATEXSUFFIX',
        src_suffix = '$REST_SUFFIX')

__rest_htmlbuilder = SCons.Builder.Builder(
        action = rst2html,
        suffix = '$REST_HTMLSUFFIX',
        src_suffix = '$REST_SUFFIX')

__rest_odtbuilder = SCons.Builder.Builder(
        action = rst2odt,
        suffix = '$REST_ODTSUFFIX',
        src_suffix = '$REST_SUFFIX')

def Rst2Latex(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for ReST->LaTeX.
    """
    if not SCons.Util.is_List(target):
        target = [target]
    if not source:
        source = target[:]
        target = []
        for s in source:
            sourceBase, sourceExt = os.path.splitext(SCons.Util.to_String(s))
            target.append(sourceBase)

    if not SCons.Util.is_List(source):
        source = [source]

    result = []
    for t, s in zip(target, source):
        # Call builder
        result.extend(__rest_latexbuilder.__call__(env, t, s, **kw))

    return result

def Rst2Html(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for ReST->HTML.
    """
    if not SCons.Util.is_List(target):
        target = [target]
    if not source:
        source = target[:]
        target = []
        for s in source:
            sourceBase, sourceExt = os.path.splitext(SCons.Util.to_String(s))
            target.append(sourceBase)

    if not SCons.Util.is_List(source):
        source = [source]

    result = []
    for t, s in zip(target, source):
        # Call builder
        result.extend(__rest_htmlbuilder.__call__(env, t, s, **kw))

    return result

def Rst2Odt(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for ReST->Odt.
    """
    if not SCons.Util.is_List(target):
        target = [target]
    if not source:
        source = target[:]
        target = []
        for s in source:
            sourceBase, sourceExt = os.path.splitext(SCons.Util.to_String(s))
            target.append(sourceBase)

    if not SCons.Util.is_List(source):
        source = [source]

    result = []
    for t, s in zip(target, source):
        # Call builder
        result.extend(__rest_odtbuilder.__call__(env, t, s, **kw))

    return result

def generate(env):
    """Add Builders and construction variables to the Environment."""

    env.SetDefault(
        # Suffixes/prefixes
        REST_SUFFIX = '.rst',
        REST_LATEXSUFFIX = '.ltx',
        REST_HTMLSUFFIX = '.html',
        REST_ODTSUFFIX = '.odt',
        )

    try:
        env.AddMethod(Rst2Latex, "Rst2Latex")
        env.AddMethod(Rst2Html, "Rst2Html")
        env.AddMethod(Rst2Odt, "Rst2Odt")
    except AttributeError:
        # Looks like we use a pre-0.98 version of SCons...
        from SCons.Script.SConscript import SConsEnvironment
        SConsEnvironment.Rst2Latex = Rst2Latex
        SConsEnvironment.Rst2Html = Rst2Html
        SConsEnvironment.Rst2Odt = Rst2Odt

def exists(env):
    return _detect(env)

