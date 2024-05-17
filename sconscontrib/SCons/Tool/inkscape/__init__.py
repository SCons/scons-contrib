# MIT License
#
# Copyright 2024 The SCons Foundation
# Copyright 2016-2024 Keith F Prussing
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""SCons.Tool.Inkscape

Builders for converting vector graphics using Inkscape.  Specifically,
converting SVG to PDF, PDF + ``LaTeX``, and PNG and PDF to PNG.

There normally shouldn't be any need to import this module directly.  It
will usually be imported through the generic SCons.Tool.Tool() selection
method.

"""

#
# Acknowledgements
# ----------------
#
# The format of this Tool is highly influenced by the JAL Tool on the
# ToolsForFools_ page from the SCons Wiki.
#
# .. ToolsForFools: https://github.com/SCons/scons/wiki/ToolsForFools
#

import SCons.Action
import SCons.Builder
import SCons.Errors
try:
    from SCons.Warnings import SConsWarning as SConsWarning
except ImportError:
    from SCons.Warnings import Warning as SConsWarning

import itertools
import os
import pathlib
import platform
import re

#
# Preliminary details
# ~~~~~~~~~~~~~~~~~~~
#
# Begin by defining local errors

class ToolInkscapeWarning(SConsWarning):
    pass

class InkscapeNotFound(ToolInkscapeWarning):
    pass

SCons.Warnings.enableWarningClass(ToolInkscapeWarning)

#
# Utility functions
# ~~~~~~~~~~~~~~~~~
#
def _detect(env):
    """Try to locate the Inkscape executable
    """
    try:
        # Check if we've already found it
        return env["INKSCAPE"]
    except KeyError:
        pass

    # Next try searching the Path.  This should work on *nix and nicely
    # configured Windows systems.
    inkscape = env.WhereIs("inkscape")
    if inkscape:
        return inkscape

    # That didn't work so Inkscape must not be on the PATH.  As a last
    # resort, we can try to scan "known" installation locations on
    # Windows and Darwin to see if we can locate the binary.
    if platform.system() == "Windows":
        # This assumes proper binary compatibility and considers the
        # user may be running under CygWin.
        prog = os.path.join("PROGRA~1", "Inkscape", "inkscape.com")
        for root in ("C:" + os.sep, os.path.join("/cygdrive", "c")):
            inkscape = env.WhereIs(os.path.join(root, prog))
            if inkscape:
                return inkscape

    elif platform.system() == "Darwin":
        # macOS could have been installed using their installer.
        inkscape = env.WhereIs(os.path.join("/Applications",
                                            "Inkscape.app",
                                            "Contents",
                                            "MacOS",
                                            "inkscape")
                               )
        if inkscape:
            return inkscape

    # And the last ditch failed.  Time to just error out
    raise SCons.Errors.StopError(InkscapeNotFound,
                                 "Could not find Inkscape executable")


#
# Emitters
# ~~~~~~~~
#
def _emitter(target, source, env):
    """Define a generic emitter for the LaTeX exporting"""
    if re.search("--export-latex", env.get("INKSCAPEFLAGS", "")):
        target.extend(
            [str(_) + "_tex" for _ in target
             if pathlib.Path(str(_)).suffix in (".pdf", ".ps", ".eps")
             ]
        )

    return target, source

#
# Builders
# ~~~~~~~~
#

_builder = SCons.Builder.Builder(
    action=SCons.Action.Action("$INKSCAPECOM", "$INKSCAPECOMSTR"),
    emitter=_emitter
)

#
# SCons functions
# ~~~~~~~~~~~~~~~
#

def generate(env):
    """Add the builder to the :class:`SCons.Environment.Environment`
    """
    env["INKSCAPE"] = _detect(env)

    env.SetDefault(
        INKSCAPECOM="$INKSCAPE $INKSCAPEFLAGS --export-filename=$TARGET $SOURCE",
        INKSCAPEFLAGS="",
        INKSCAPECOMSTR="",
    )
    env["BUILDERS"]["Inkscape"] = _builder


def exists(env):
    return _detect(env)
