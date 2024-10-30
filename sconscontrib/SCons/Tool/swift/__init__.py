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

"""SCons.Tool.swift

Tool-specific initialization for Swift.
"""
import SCons.Action
import SCons.Builder
import SCons.Util


class ToolSwiftWarning(SCons.Warnings.SConsWarning):
    pass


class SwiftNotFound(ToolSwiftWarning):
    pass


SCons.Warnings.enableWarningClass(ToolSwiftWarning)


def _detect(env):
    """ Try to detect the swiftc binary """
    try:
        return env["swiftc"]
    except KeyError:
        pass

    swift = env.WhereIs("swiftc")
    if swift:
        return swift

    raise SCons.Errors.StopError(SwiftNotFound, "Could not detect swiftc executable")
    return None

#
# Builders
#
swiftc_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$SWIFTCCOM", "$SWIFTCCOMSTR"),
    src_suffix="$SWIFTSUFFIX",
    single_source=True,
)  # file by file

def Swift(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for the swiftc executable.
        swiftc [options] file
    """
    if not SCons.Util.is_List(target):
        target = [target]
    if not source:
        source = target[:]
    if not SCons.Util.is_List(source):
        source = [source]

    result = []
    for t, s in zip(target, source):
        # Call builder
        swift_src = swiftc_builder.__call__(env, t, s, **kw)
        result.extend(swift_src)

    return result

def generate(env):
    """ Add Builders and construction variables to the Environment. """
    env["SWIFTC"] = _detect(env)

    env.SetDefault(
        SWIFTC="swiftc",
        SWIFTSUFFIX=".swift",
        SWIFTCFLAGS=SCons.Util.CLVar("-c"),
        SWIFTCCOM="$SWIFTC $SWIFTCFLAGS $SOURCE",
    )

    env.AddMethod(Swift, "Swift")


def exists(env):
    return _detect(env)
