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

"""SCons.Tool.jal

Tool-specific initialization for the JALv2 compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

import SCons.Action
import SCons.Builder
import SCons.Util


class ToolJalWarning(SCons.Warnings.Warning):
    pass


class JalCompilerNotFound(ToolJalWarning):
    pass


SCons.Warnings.enableWarningClass(ToolJalWarning)


def _detect(env):
    """ Try to detect the JAL compiler """
    try:
        return env["JAL"]
    except KeyError:
        pass

    jal = env.WhereIs("jalv2") or env.WhereIs("jal")
    if jal:
        return jal

    raise SCons.Errors.StopError(JalCompilerNotFound, "Could not detect JAL compiler")
    return None


#
# Builders
#
__jal_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$JAL_COM", "$JAL_COMSTR"),
    suffix="$JAL_ASMSUFFIX",
    src_suffix="$JAL_SUFFIX",
    single_source=1,
)

__jal_asm_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$JAL_ASMCOM", "$JAL_ASMCOMSTR"),
    suffix="$JAL_ASMSUFFIX",
    src_suffix="$JAL_SUFFIX",
    single_source=1,
)

__jal_cod_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$JAL_CODCOM", "$JAL_CODCOMSTR"),
    suffix="$JAL_CODSUFFIX",
    src_suffix="$JAL_SUFFIX",
    single_source=1,
)

__jal_hex_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$JAL_HEXCOM", "$JAL_HEXCOMSTR"),
    suffix="$JAL_HEXSUFFIX",
    src_suffix="$JAL_SUFFIX",
    single_source=1,
)


def Jal(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for the JALv2 executable.
        jalv2 [options] file
    """
    if not SCons.Util.is_List(target):
        target = [target]
    if not source:
        source = target[:]
    if not SCons.Util.is_List(source):
        source = [source]

    result = []
    jal_suffix = env.subst("$JAL_SUFFIX")
    jal_codsuffix = env.subst("$JAL_CODSUFFIX")
    jal_hexsuffix = env.subst("$JAL_HEXSUFFIX")
    for t, s in zip(target, source):
        # Call builder
        jal_asm = __jal_builder.__call__(env, t, s, **kw)
        result.extend(jal_asm)
        # Add cleanup files
        src = str(s)
        if src.endswith(jal_suffix):
            jal_stem = src[: -len(jal_suffix)]
        else:
            jal_stem = src
        env.Clean(jal_asm, [jal_stem + jal_codsuffix, jal_stem + jal_hexsuffix])

    return result


def generate(env):
    """Add Builders and construction variables to the Environment."""

    env["JAL"] = _detect(env)
    env.SetDefault(
        # Additional command-line flags
        JAL_FLAGS=SCons.Util.CLVar("-quiet"),
        # Suffixes/prefixes
        JAL_SUFFIX=".jal",
        JAL_ASMSUFFIX=".asm",
        JAL_CODSUFFIX=".cod",
        JAL_HEXSUFFIX=".hex",
        # JAL commands
        JAL_COM="$JAL $JAL_FLAGS $SOURCES",
        JAL_COMSTR="",
        JAL_ASMCOM="$JAL $JAL_FLAGS -no-codfile -no-hex -asm $TARGET $SOURCE",
        JAL_ASMCOMSTR="",
        JAL_CODCOM="$JAL $JAL_FLAGS -no-asm -no-hex -codfile $TARGET $SOURCE",
        JAL_CODCOMSTR="",
        JAL_HEXCOM="$JAL $JAL_FLAGS -no-asm -no-codfile -hex $TARGET $SOURCE",
        JAL_HEXCOMSTR="",
    )

    try:
        env.AddMethod(Jal, "Jal")
    except AttributeError:
        # Looks like we use a pre-0.98 version of SCons...
        from SCons.Script.SConscript import SConsEnvironment

        SConsEnvironment.Jal = Jal

    env["BUILDERS"]["JalAsm"] = __jal_asm_builder
    env["BUILDERS"]["JalCod"] = __jal_cod_builder
    env["BUILDERS"]["JalHex"] = __jal_hex_builder


def exists(env):
    return _detect(env)
