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

#  A SCons tool inspired by Glenn Hutchings' <zondo42@googlemail.com> Sphinx-Scons
#  https://bitbucket.org/zondo/sphinx-scons/.  It is almost certain there are some bits of cut-and-paste
#  from that project to this one.  Sphinx-Scons is licenced under the BSD licence.

"""
A SCons tool for supporting Sphinx processing.
"""

__author__ = "Russel Winder <russel@russel.org.uk>"
__date__ = "2011-08-31"

import os

from SCons.Script import WhereIs
from SCons.Util import CLVar, is_List

defaultSourceDirectory = "source"
defaultBuildDirectory = "build"


def Source(env, source=[defaultSourceDirectory], target=None, *args, **kwargs):
    buildDirectory = defaultBuildDirectory
    if not is_List(source):
        source = [source]
    if len(source) < 1:
        raise ValueError("Must have at least one source directory.")
    sources = []
    if target != None:
        if not isinstance(target, str):
            raise ValueError("target must be a string value.")
        buildDirectory = target
    targets = []
    for directoryName in source:
        sourceList = []
        targetList = []
        for root, directories, files in os.walk(directoryName):
            for name in files:
                base, ext = os.path.splitext(name)
                if ext == ".rst":
                    sourceList.append(root + "/" + name)
                    targetList.append(
                        os.path.join(
                            buildDirectory,
                            root.replace(directoryName, "html"),
                            base + ".html",
                        )
                    )
        sources.append(sourceList)
        targets.append(targetList)
    return []


def HTML(env, source=[defaultSourceDirectory], target=None, *args, **kwargs):
    buildDirectory = defaultBuildDirectory
    if not is_List(source):
        source = [source]
    if len(source) < 1:
        raise ValueError("Must have at least one source directory.")
    sources = []
    if target != None:
        if not isinstance(target, str):
            raise ValueError("target must be a string value.")
        buildDirectory = target
    targets = []
    for directoryName in source:
        sourceList = []
        targetList = []
        for root, directories, files in os.walk(directoryName):
            for name in files:
                base, ext = os.path.splitext(name)
                if ext == ".rst":
                    sourceList.append(root + "/" + name)
                    targetList.append(
                        os.path.join(
                            buildDirectory,
                            root.replace(directoryName, "html"),
                            base + ".html",
                        )
                    )
        sources.append(sourceList)
        targets.append(targetList)
    knownExtraFiles = [
        "doctrees/environment.pickle",
        "doctrees/index.doctree",
        "html/.buildinfo",
        "html/genindex.html",
        "html/objects.inv",
        "html/search.html",
        "html/searchindex.js",
        "html/_sources/index.txt",
        "html/_static/basic.css",
        "html/_static/default.css",
        "html/_static/doctools.js",
        "html/_static/file.png",
        "html/_static/jquery.js",
        "html/_static/minus.png",
        "html/_static/plus.png",
        "html/_static/pygments.css",
        "html/_static/searchtools.js",
        "html/_static/sidebar.js",
        "html/_static/underscore.js",
    ]
    constructedKnownExtraFiles = [
        buildDirectory + "/" + name for name in knownExtraFiles
    ]
    env.Precious(constructedKnownExtraFiles)
    returnValue = []
    for i in range(len(source)):
        env.SideEffect(constructedKnownExtraFiles, targets[i])
        returnValue += env.Command(
            targets[i],
            sources[i],
            "{0} {1} -b html -d {2}/doctrees {3} {2}/html".format(
                env["SPHINX"], env["SPHINXFLAGS"], buildDirectory, source[i]
            ),
        )
    return returnValue


def exists(env):
    return WhereIs("sphinx-build")


def generate(env):
    env["SPHINX"] = env.Detect("sphinx-build") or "sphinx-build"
    env["SPHINXFLAGS"] = CLVar("")
    env.AddMethod(Source)
    env.AddMethod(HTML)
