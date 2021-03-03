import os
import shutil

import SCons.Action
import SCons.Defaults
import SCons.Scanner
import SCons.Tool
import SCons.Util

SipAction = SCons.Action.Action("$SIPCOM", "$SIPCOMSTR")


def sipSuffixEmitter(env, source):
    return ".sip"


def _sipEmitter(targets, sources, env):
    targets = []
    import tempfile

    tempdir = tempfile.mkdtemp(prefix="scons_sip_")
    sbfFileName = os.path.join(tempdir, "buildinfo.sbf")
    sbfCommand = "${SIP} $SIPFLAGS -s $CXXFILESUFFIX -b '%s' '%s' "
    for s in sources:
        if env.Execute(
            sbfCommand % (sbfFileName, str(s)), "Generating sip dependencies for %s" % s
        ):
            raise RuntimeError("Failed to generate '" + sbfFileName + "'.")
        f = open(sbfFileName)
        outputs = []
        for l in f.readlines():
            if l.startswith("sources"):
                outputs += l.strip().split()[2:]
        f.close()
        os.remove(sbfFileName)
    shutil.rmtree(tempdir)
    targets += ["$SIPOUTPUTDIR/%s" % cfile for cfile in outputs]
    return targets, sources


def generate(env):
    """Add Builders and construction variables for SIP to an Environment."""

    c_file, cxx_file = SCons.Tool.createCFileBuilders(env)

    cxx_file.suffix[".sip"] = sipSuffixEmitter

    cxx_file.add_action(".sip", SipAction)
    cxx_file.add_emitter(".sip", _sipEmitter)
    flags = []
    try:
        from PyQt4 import pyqtconfig

        config = pyqtconfig.Configuration()
        flags = config.pyqt_sip_flags.split() + ["-I" + config.pyqt_sip_dir]
    except ImportError:
        import sipconfig

        config = sipconfig.Configuration()

    env["SIP"] = config.sip_bin
    env["SIPFLAGS"] = flags
    env[
        "SIPCOM"
    ] = '$SIP $SIPFLAGS -s ${TARGET.suffix} -c ${SIPOUTPUTDIR and SIPOUTPUTDIR or "."} -c ${TARGET.dir} $SOURCES'
    env["SIPCOMSTR"] = "$SIPCOM"
    env["BUILDERS"]["Sip"] = cxx_file


def exists(env):
    return env.Detect(["sip"])
