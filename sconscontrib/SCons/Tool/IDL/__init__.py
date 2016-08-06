"""
SCons.Tool.IDL

Tool-specific initialization for the Orbix idl pre-compiler.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

Be sure to have all the necessary environment variables set

ORACLE_HOME= and LD_LIBRARY_PATH=
SConstruct makes use of these to populate
the build environment so $ORBIX_ROOT/bin/idl will have what it 
needs to run cleanly.

"""

#
# Dan McNaul 03/01/2016 v1.0
#		Wrote the builder following/copying the 
#		example found at https://bitbucket.org/scons/scons/wiki/ToolsForFools
# ...
#

import os
import SCons.Action
import SCons.Builder

class ToolIDLWarning(SCons.Warnings.Warning):
    pass

class IDLCompilerNotFound(ToolIDLWarning):
    pass

SCons.Warnings.enableWarningClass(ToolIDLWarning)


def _detect(env):
    """ Try to detect the idl pre-compiler """
#    print "TRACE -- _detect(env) called"

    try: 
        return "%s/bin/idl" % (os.environ['ORBIX_ROOT'])
    except KeyError: 
        pass

    IDL = env.WhereIs('idl')
    if IDL:
        return IDL

    raise SCons.Errors.StopError(
        IDLCompilerNotFound,
        "Could not detect the Orbix idl compiler")
    return None

#
# Builders
#
_IDL_builder = SCons.Builder.Builder(
        action = '$IDL_COM',
        suffix = '$IDL_HHSUFFIX',
        src_suffix = '$IDL_SUFFIX',
        single_source = 1)

def IDL(env, target, source=None, *args, **kw):
    """
    A pseudo-Builder wrapper for the Orbix idl pre-compiler.
        IDL [options]
    """
#    print "TRACE -- IDL(env, target, source, *args) called"

    if not SCons.Util.is_List(target):
        target = [target]
    if not source:
        source = target[:]
    if not SCons.Util.is_List(source):
        source = [source]

    result = []
    IDL_suffix = env.subst('$IDL_SUFFIX')
    IDL_hhsuffix = env.subst('$IDL_HHSUFFIX')
    IDL_ccsuffix = env.subst('$IDL_CCSUFFIX')


    for t, s in zip(target, source):
        src = str(s)
        if src.endswith(IDL_suffix):
            IDL_stem = src[:-len(IDL_suffix)]
        else:
            IDL_stem = src
        IDL_csrc = _IDL_builder.__call__(env, t, s, **kw)
        result.extend(IDL_csrc)
        # Add cleanup files
        env.Clean(IDL_csrc, [IDL_stem+IDL_hhsuffix])
        env.Clean(IDL_csrc, [IDL_stem+"S"+IDL_ccsuffix])
        env.Clean(IDL_csrc, [IDL_stem+"C"+IDL_ccsuffix])

    return result

def generate(env):
    """ Add Builders and construction variables to the Environment. """

#    print "TRACE -- generate(env) called"

    env['IDL'] = _detect(env)

    env.SetDefault(
        # Suffixes/prefixes
        IDL_SUFFIX = '.idl',
        IDL_CCSUFFIX = '.cc',
        IDL_HHSUFFIX = '.hh',
#        IDL_INCPREFIX = "include=",
#        IDL_INCSUFFIX = "",
#        IDL_INCLUDES = "$( ${_concat(IDL_INCPREFIX, CPPPATH, IDL_INCSUFFIX, __env__, RDirs, TARGET, SOURCE)} $)",
        # IDL commands
        IDL_COM = "$IDL -out $TARGET.dir -B $SOURCE ",
        )

    try:
        env.AddMethod(IDL, "IDL")
    except AttributeError:
        # Looks like we use a pre-0.98 version of SCons...
        from SCons.Script.SConscript import SConsEnvironment
        SConsEnvironment.IDL = IDL

def exists(env):
#    print "TRACE -- exists(env) called"
    return _detect(env)
