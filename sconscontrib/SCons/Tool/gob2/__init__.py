# MIT License
#
# Copyright The SCons Foundation
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

"""SCons.Tool.gob2

Tool-specific initialization for the gob2 GObject builder.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.
"""

import os

import SCons.Action
import SCons.Builder
import SCons.Util


class ToolGob2Warning(SCons.Warnings.SConsWarning):
    pass


class Gob2NotFound(ToolGob2Warning):
    pass


SCons.Warnings.enableWarningClass(ToolGob2Warning)


def _detect(env):
    """ Try to detect the gob2 builder """
    try:
        return env["GOB2"]
    except KeyError:
        pass

    gob2 = env.WhereIs("gob2") or env.WhereIs("gob")
    if gob2:
        return gob2

    raise SCons.Errors.StopError(Gob2NotFound, "Could not detect gob2 builder")
    return None


#
# Emitters
#
def __gob2_emitter(target, source, env):
    sourceBase, sourceExt = os.path.splitext(SCons.Util.to_String(source[0]))
    target.append(sourceBase + env.subst("$GOB2_HSUFFIX"))
    target.append(sourceBase + env.subst("$GOB2_PRIVATESUFFIX"))

    return target, source


#
# Builders
#
__gob2_cbuilder = SCons.Builder.Builder(
    action=SCons.Action.Action("$GOB2_COM", "$GOB2_COMSTR"),
    suffix="$GOB2_CSUFFIX",
    src_suffix="$GOB2_SUFFIX",
    emitter=__gob2_emitter,
)

__gob2_cppbuilder = SCons.Builder.Builder(
    action=SCons.Action.Action("$GOB2_CXXCOM", "$GOB2_CXXCOMSTR"),
    suffix="$GOB2_CXXSUFFIX",
    src_suffix="$GOB2_SUFFIX",
    emitter=__gob2_emitter,
)


def Gob2(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for the gob2 executable, creating C output.
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
        # Set output directory
        env["GOB2_OUTDIR"] = "."
        head, tail = os.path.split(SCons.Util.to_String(s))
        if head:
            env["GOB2_OUTDIR"] = head
        # Call builder
        result.extend(__gob2_cbuilder.__call__(env, t, s, **kw))

    return result


def Gob2Cpp(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for the gob2 executable, creating CPP output.
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
        # Set output directory
        env["GOB2_OUTDIR"] = "."
        head, tail = os.path.split(SCons.Util.to_String(s))
        if head:
            env["GOB2_OUTDIR"] = head
        # Call builder
        result.extend(__gob2_cppbuilder.__call__(env, t, s, **kw))

    return result


def generate(env):
    """Add Builders and construction variables to the Environment."""

    env["GOB2"] = _detect(env)
    env.SetDefault(
        # Additional command-line flags
        GOB2_FLAGS=SCons.Util.CLVar(""),
        # Suffixes/prefixes
        GOB2_SUFFIX=".gob",
        GOB2_CSUFFIX=".c",
        GOB2_CXXSUFFIX=".cc",
        GOB2_HSUFFIX=".h",
        GOB2_PRIVATESUFFIX="-private.h",
        # GOB2 commands
        GOB2_COM="$GOB2 $GOB2_FLAGS -o $GOB2_OUTDIR $SOURCES",
        GOB2_COMSTR="",
        GOB2_CXXCOM="$GOB2 $GOB2_FLAGS --for-cpp -o $GOB2_OUTDIR $SOURCES",
        GOB2_CXXCOMSTR="",
    )

    try:
        env.AddMethod(Gob2, "Gob2")
        env.AddMethod(Gob2Cpp, "Gob2Cpp")
    except AttributeError:
        # Looks like we use a pre-0.98 version of SCons...
        from SCons.Script.SConscript import SConsEnvironment

        SConsEnvironment.Gob2 = Gob2
        SConsEnvironment.Gob2Cpp = Gob2Cpp


def exists(env):
    return _detect(env)
