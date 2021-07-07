"""
SCons.Tool.ProC

Tool-specific initialization for the Oracle Pro*C pre-compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

Be sure to have ORACLE_HOME= and LD_LIBRARY_PATH=
in your environment set.  SConstruct makes use of these to populate
the build environment so $ORACLE_HOME/bin/proc will have what it
needs to run cleanly.

"""

#
# Dan McNaul 01/12/2016 v1.0
# 		Wrote the builder following/copying the
# 		example found at https://bitbucket.org/scons/scons/wiki/ToolsForFools
# ...
#

import os
import SCons.Action
import SCons.Builder


class ToolProCWarning(SCons.Warnings.SConsWarning):
    pass


class ProCCompilerNotFound(ToolProCWarning):
    pass


SCons.Warnings.enableWarningClass(ToolProCWarning)


def _detect(env):
    """ Try to detect the Pro*C pre-compiler """
    # print("TRACE -- _detect(env) called")

    try:
        return "%s/bin/proc" % (os.environ["ORACLE_HOME"])
    except KeyError:
        pass

    ProC = env.WhereIs("proc")
    if ProC:
        return ProC

    raise SCons.Errors.StopError(
        ProCCompilerNotFound, "Could not detect the Oracle ProC compiler"
    )
    return None


#
# Builders
#
_ProC_builder = SCons.Builder.Builder(
    action="$ProC_COM",
    suffix="$ProC_CSUFFIX",
    src_suffix="$ProC_SUFFIX",
    single_source=1,
)


def ProC(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for the Oracle Pro*C pre-compiler.
        ProC [options]
    """
    # print("TRACE -- ProC(env, target, source, *args) called")

    if not SCons.Util.is_List(target):
        target = [target]
    if not source:
        source = target[:]
    if not SCons.Util.is_List(source):
        source = [source]

    result = []
    ProC_suffix = env.subst("$ProC_SUFFIX")
    ProC_lissuffix = env.subst("$ProC_LISSUFFIX")

    for t, s in zip(target, source):
        src = str(s)
        if src.endswith(ProC_suffix):
            ProC_stem = src[: -len(ProC_suffix)]
        else:
            ProC_stem = src
        ProC_csrc = _ProC_builder.__call__(env, t, s, **kw)
        result.extend(ProC_csrc)
        # Add cleanup files
        env.Clean(ProC_csrc, [ProC_stem + ProC_lissuffix])

    return result


def generate(env):
    """ Add Builders and construction variables to the Environment. """
    # print("TRACE -- generate(env) called")
    env["PRO_C"] = _detect(env)

    env.SetDefault(
        # Suffixes/prefixes
        ProC_SUFFIX=".pc",
        ProC_CSUFFIX=".c",
        ProC_LISSUFFIX=".lis",
        ProC_INCPREFIX="include=",
        ProC_INCSUFFIX="",
        ProC_INCLUDES="$( ${_concat(ProC_INCPREFIX, CPPPATH, ProC_INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)",
        # ProC commands
        ProC_COM="$PRO_C iname=$SOURCE oname=$TARGET lname=${TARGET.base}$ProC_LISSUFFIX $ProC_INCLUDES",
    )

    try:
        env.AddMethod(ProC, "ProC")
    except AttributeError:
        # Looks like we use a pre-0.98 version of SCons...
        from SCons.Script.SConscript import SConsEnvironment

        SConsEnvironment.ProC = ProC


def exists(env):
    #  print("TRACE -- exists(env) called")
    return _detect(env)
