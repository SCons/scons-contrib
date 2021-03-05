# -*- mode:python; coding:utf-8; -*-

#  A SCons tool to enable compilation of Haskell in SCons.
#
# Copyright © 2005 José Pablo Ezequiel "Pupeno" Fernández Silva
# Copyright © 2009 Russel Winder
#
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU
#  General Public License as published by the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
#  the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public
#  License for more details.
#
#  You should have received a copy of the GNU General Public License along with this program.  If not, see
#  <http://www.gnu.org/licenses/>.
#
#  Original this code was licenced under GPLv2.  This fork is relicenced under GPLv3 as is permitted.

import SCons.Tool
import SCons.Action
from SCons.Scanner import Scanner
from SCons.Defaults import ObjSourceScan, ArAction
import os.path
import string


def generate(env):
    env["HS"] = env.Detect("ghc") or "ghc"
    env["HSLINK"] = "$HS $_LIBS $SOURCES -o $TARGET"
    env["HSCOM"] = "$HS $_IMPORTS $_LIBS -c $SOURCE -o $TARGET"
    env["_IMPORTS"] = "${_concat(IMPORTSPREFIX, LIBPATH, IMPORTSSUFFIX, __env__)}"
    env["IMPORTSPREFIX"] = "-i"
    env["IMPORTSSUFFIX"] = ""
    env["_LIBS"] = "${_concat(LIBSPREFIX, LIBS, LIBSSUFFIX, __env__)}"
    env["LIBSPREFIX"] = "-package "
    env["LIBSSUFFIX"] = ""

    haskellSuffixes = [".hs", ".lhs"]

    compileAction = SCons.Action.Action("$HSCOM")

    linkAction = SCons.Action.Action("$HSLINK")

    def addHaskellInterface(target, source, env):
        """ Add the .hi target with the same name as the object file. """
        targetName = os.path.splitext(str(target[0]))[0]
        return (target + [targetName + ".hi"], source)

    def importedModules(node, env, path):
        """ Use ghc to find all the imported modules. """

        # print("Figuring out dependencies for " + str(node))
        def removeFile(fileName, errmsg=None):
            """ Try to remove fileName, returns true on success, false otherwise. """
            if os.path.exists(fileName):
                try:
                    os.remove(fileName)
                except OSError:
                    print("Unable to remove '%s'." % fileName)
                    return False
            return True

        # Generate the name of the file that is going to contain the dependency mappings.
        fileName = os.path.join(
            os.path.dirname(str(node)), "." + os.path.basename(str(node)) + ".dep"
        )

        # Just in case the file already exist, to avoid the creation of a .bak file, delete it.
        if not removeFile(fileName):
            print("Dependencies will not be calculated.")
            return []

        # Build the command to obtain the dependency mapping from ghc.
        command = ["ghc", "-M", "-optdep-f", "-optdep" + fileName]
        if "LIBPATH" in env._dict:
            command += ["-i" + string.join(env["LIBPATH"], ":")]
        command += [str(node)]
        command = string.join(command)

        commandIn, commandOut = os.popen4(command, "r")
        errorMessage = commandOut.read()
        commandIn.close()
        commandOut.read()
        if errorMessage != "":
            print("An error ocurred running `%s`:" % command)
            for line in string.split(errorMessage, "\n"):
                print(">" + line)
            print("Dependencies will not be calculated.")
            removeFile(fileName)
            return []

        try:
            file = open(fileName, "r")
            fileContents = file.read()
            file.close()
        except:
            print("Unable to open '%s'." % fileName)
            print("Dependencies will not be calculated.")
            removeFile(fileName)
            return []

        fileContents = string.split(fileContents, "\n")

        deps = []
        for line in fileContents:
            # print("deps=%s." % str(deps))
            if len(line) > 0 and line[0] != "#":
                files = string.split(line, ":")
                target = string.strip(files[0])
                source = string.strip(files[1])
                if source != str(node):  # and os.path.splitext(source)[1] != ".hi":
                    deps += [os.path.basename(source)]
                # if os.path.splitext(target)[0] != os.path.splitext(str(node))[0]:
                #    deps += [os.path.basename(target)]
                # print("   %s depends on %s." % (target, source))

        removeFile(fileName)
        # print("%s depends on %s." % (str(node), str(deps)))
        return deps

    haskellScanner = Scanner(
        function=importedModules,
        name="HaskellScanner",
        skeys=haskellSuffixes,
        recursive=False,
    )

    haskellProgram = SCons.Builder.Builder(
        action=linkAction,
        prefix="$PROGPREFIX",
        suffix="$PROGSUFFIX",
        src_suffix="$OBJSUFFIX",
        src_builder="HaskellObject",
    )
    env["BUILDERS"]["HaskellProgram"] = haskellProgram

    haskellLibrary = SCons.Builder.Builder(
        action=SCons.Defaults.ArAction,
        prefix="$LIBPREFIX",
        suffix="$LIBSUFFIX",
        src_suffix="$OBJSUFFIX",
        src_builder="HaskellObject",
    )
    env["BUILDERS"]["HaskellLibrary"] = haskellLibrary

    haskellObject = SCons.Builder.Builder(
        action=compileAction,
        emitter=addHaskellInterface,
        prefix="$OBJPREFIX",
        suffix="$OBJSUFFIX",
        src_suffix=haskellSuffixes,
        source_scanner=haskellScanner,
    )
    env["BUILDERS"]["HaskellObject"] = haskellObject


def exists(env):
    return env.Detect(["ghc"])
