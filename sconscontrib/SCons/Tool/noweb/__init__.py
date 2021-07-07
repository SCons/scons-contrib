"""SCons.Tool.noweb

Tool-specific initialization for Noweb.

"""

#
# Copyright (c) 2020 The SCons Foundation
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

import SCons.Action
import SCons.Builder
import SCons.Util


class ToolNowebWarning(SCons.Warnings.SConsWarning):
    pass


class NowebNotFound(ToolNowebWarning):
    pass


SCons.Warnings.enableWarningClass(ToolNowebWarning)

noweb_env = {"noweave": "NOWEAVE", "notangle": "NOTANGLE"}


def _detect(env, key):
    """ Try to detect the noweave/notangle binary """
    try:
        return env[noweb_env[key]]
    except KeyError:
        pass

    noweb = env.WhereIs(key)
    if noweb:
        return noweb

    raise SCons.Errors.StopError(
        NowebNotFound, "Could not detect noweave/notangle executable"
    )
    return None


#
# Builders
#
noweave_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$NOWEAVECOM", "$NOWEAVECOMSTR"),
    src_suffix=".nw",
    single_source=True,
)  # file by file

noweave_html_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$NOWEAVEHTMLCOM", "$NOWEAVEHTMLCOMSTR"),
    src_suffix=".nw",
    single_source=True,
)  # file by file

notangle_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$NOTANGLECOM", "$NOTANGLECOMSTR"),
    src_suffix=".nw",
    single_source=True,
)  # file by file


def generate(env):
    """Add Builders and construction variables for noweb to an Environment."""

    env["NOTANGLE"] = _detect(env, "notangle")
    env["NOWEAVE"] = _detect(env, "noweave")

    env.SetDefault(
        NOWEAVE="noweave",
        NOTANGLE="notangle",
        NOWEAVEFLAGS=SCons.Util.CLVar(),
        NOWEAVEHTMLFLAGS=SCons.Util.CLVar(["-filter", "l2h", "-index", "-html"]),
        NOTANGLEFLAGS=SCons.Util.CLVar(),
        NOWEAVECOM="$NOWEAVE $NOWEAVEFLAGS $SOURCE > $TARGET",
        NOWEAVECOMSTR="",
        NOWEAVEHTMLCOM="$NOWEAVE $NOWEAVEHTMLFLAGS $SOURCE > $TARGET",
        NOWEAVEHTMLCOMSTR="",
        NOTANGLECOM="$NOTANGLE $NOTANGLEFLAGS -R$TARGET $SOURCE > $TARGET",
        NOTANGLECOMSTR="",
    )

    env.Append(
        BUILDERS={
            "Noweave": noweave_builder,
            "NoweaveHtml": noweave_html_builder,
            "Notangle": notangle_builder,
        }
    )


def exists(env):
    return _detect(env, "noweave")
