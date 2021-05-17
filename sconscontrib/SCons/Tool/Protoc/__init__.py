"""
Google's Protoc compiler builder

This builder invokes the protoc compiler to generate C++, Python, and Java
files for both protobuf messages and GRPC services.

Original authors: Peter Cooner, Scott Stafford, Steven Haywood (may be more!)
Modified by Bassem Girgis

"""


import os
import SCons.Util
from SCons.Script import Builder, Action, File, Dir

protocs = ["protoc"]


def _removeAll(arrList, val):
    while val in arrList:
        arrList.remove(val)
    return arrList


def _getJavaTargets(
    filePath, outPath, protoc_suffix, protoc_java_suffix, protoc_grpc_java_suffix
):
    isMultiFile = False
    isJavaPackage = False
    packagePath = ""
    outerClassName = (
        os.path.basename(filePath).replace(protoc_suffix, "").title().replace("_", "")
    )
    messages = []
    services = []

    # search the file for java specific options.
    with open(filePath, "r") as srcfile:
        for line in srcfile:

            # take the non-comment part from the line and strip away any padding
            line_s = line.split("//")[0].strip()

            # the case of empty lines
            if not line_s:
                continue

            # trying to handle:
            # option java_multiple_files = true;
            # in this case the generated files are two files per message and
            # one file for the package
            if all(
                [
                    line_s.startswith("option java_multiple_files"),
                    "true" in line_s,  # value has to be "true".
                    '"' not in line_s,  # literals are
                    "'" not in line_s,  # not allowed.
                    "=" in line_s,  # it has to be
                    ";" in line_s,
                ]
            ):  # a valid statement.
                isMultiFile = True
                continue

            # trying to handle the optional package switch:
            # option java_package = "io.grpc.examples.helloworld";
            # in this case, the path to which the files are generated matches
            # the given dot-notation path. This option overrides the package
            # option
            if all(
                [
                    line_s.startswith("option java_package"),
                    ('"' in line_s or "'" in line_s),  # the path has to be a literal.
                    "=" in line_s,  # it has to be
                    ";" in line_s,
                ]
            ):  # a valid statement.
                packagePath = (
                    line_s.split("=")[1]
                    .replace('"', "")
                    .replace("'", "")
                    .replace(";", "")
                    .replace(".", os.path.sep)
                    .strip()
                )
                isJavaPackage = True
                continue

            # trying to handle the package option only when java_package is not
            # given:
            # package helloworld;
            if all(
                [
                    not isJavaPackage,
                    line_s.startswith("package"),
                    '"' not in line_s,  # package is
                    "'" not in line_s,  # not a literal.
                    "=" not in line_s,  # not a valid
                    ";" in line_s,
                ]
            ):  # assignment statement.
                packagePath = (
                    _removeAll(line_s.split(" "), "")[-1]
                    .replace(";", "")
                    .replace(".", os.path.sep)
                    .strip()
                )
                continue

            # trying to handle the outer class option:
            # option java_outer_classname = "HelloWorldProto";
            # this option overrides the default which is the same as proto
            # file name but with first character capital.
            if all(
                [
                    line_s.startswith("option java_outer_classname"),
                    ('"' in line_s or "'" in line_s),  # the value has to be a literal.
                    "=" in line_s,  # it has to be
                    ";" in line_s,
                ]
            ):  # a valid statement.
                outerClassName = (
                    line_s.split("=")[1]
                    .replace('"', "")
                    .replace("'", "")
                    .replace(";", "")
                    .strip()
                )
                continue

            # collect a list of all defined messages:
            # message HelloRequest {
            if all(
                [
                    line_s.startswith("message "),
                    '"' not in line_s,  # there is
                    "'" not in line_s,  # no literals.
                    "=" not in line_s,  # not a valid
                    ";" not in line_s,
                ]
            ):  # assignment statement.
                messages.append(_removeAll(line_s.split(" "), "")[1])
                continue

            # collect a list of all defined services:
            # service Greeter {
            if all(
                [
                    line_s.startswith("service "),
                    '"' not in line_s,  # there is
                    "'" not in line_s,  # no literals.
                    "=" not in line_s,  # not a valid
                    ";" not in line_s,
                ]
            ):  # assignment statement.
                services.append(_removeAll(line_s.split(" "), "")[1])
                continue

    def _append(listObj, fileName, suffix):
        if packagePath:
            listObj.append(os.path.join(outPath, packagePath, fileName + suffix))
        else:
            listObj.append(os.path.join(outPath, fileName + suffix))

    targets = []
    grpcTargets = []

    if isMultiFile:
        for msg in messages:
            _append(targets, msg, protoc_java_suffix)
            _append(targets, msg + "OrBuilder", protoc_java_suffix)

    for srcv in services:
        _append(grpcTargets, srcv, protoc_grpc_java_suffix)

    _append(targets, outerClassName, protoc_java_suffix)

    return targets, grpcTargets


def _checkEnv(env):
    if not env["PROTOC_FLAGS"]:
        flags = SCons.Util.CLVar("")

        ###############
        # C++
        ###############

        # flag --cpp_out
        if env["PROTOC_CCOUT"]:
            env["PROTOC_CCOUT"] = Dir(env["PROTOC_CCOUT"])
            flags.append("--cpp_out=${PROTOC_CCOUT.abspath}")

        # flag --plugin=protoc-gen-grpc-cpp
        if env["PROTOC_GRPC_CC"]:
            env["PROTOC_GRPC_CC"] = File(env["PROTOC_GRPC_CC"])
            flags.append("--plugin=protoc-gen-grpc-cpp=${PROTOC_GRPC_CC.abspath}")
            # flag --grpc-cpp_out
            if env["PROTOC_CCOUT"]:
                flags.append("--grpc-cpp_out=${PROTOC_CCOUT.abspath}")

        ###############
        # Python
        ###############

        # flag --python_out
        if env["PROTOC_PYOUT"]:
            env["PROTOC_PYOUT"] = Dir(env["PROTOC_PYOUT"])
            flags.append("--python_out=${PROTOC_PYOUT.abspath}")

        # flag --plugin=protoc-gen-grpc-python
        if env["PROTOC_GRPC_PY"]:
            env["PROTOC_GRPC_PY"] = File(env["PROTOC_GRPC_PY"])
            flags.append("--plugin=protoc-gen-grpc-python=${PROTOC_GRPC_PY.abspath}")
            # flag --grpc-python_out
            if env["PROTOC_PYOUT"]:
                flags.append("--grpc-python_out=${PROTOC_PYOUT.abspath}")

        ###############
        # Java
        ###############

        # flag --java_out
        if env["PROTOC_JAVAOUT"]:
            env["PROTOC_JAVAOUT"] = Dir(env["PROTOC_JAVAOUT"])
            flags.append("--java_out=${PROTOC_JAVAOUT.abspath}")

        # flag --plugin=protoc-gen-grpc-java
        if env["PROTOC_GRPC_JAVA"]:
            env["PROTOC_GRPC_JAVA"] = File(env["PROTOC_GRPC_JAVA"])
            flags.append("--plugin=protoc-gen-grpc-java=${PROTOC_GRPC_JAVA.abspath}")
            # flag --grpc-java_out
            if env["PROTOC_JAVAOUT"]:
                flags.append("--grpc-java_out=${PROTOC_JAVAOUT.abspath}")

        # updated flags
        env["PROTOC_FLAGS"] = str(flags)

    if not env["PROTOC_PATH_FLAGS"] and env["PROTOC_PATH"]:
        inc = env["PROTOC_PATH"]

        protoPath = []
        if SCons.Util.is_List(inc):
            for path in inc:
                path = Dir(path)
                protoPath.append(path)
        elif SCons.Util.is_Scalar(inc):
            path = Dir(inc)
            protoPath.append(path)

        # flag --proto_path, -I
        flags = SCons.Util.CLVar("")
        for path in protoPath:
            flags.append(
                "--proto_path=" + (path if isinstance(path, str) else str(path.abspath))
            )

        env["PROTOC_PATH_FLAGS"] = str(flags)


def _getIncludes(env):
    if not env["PROTOC_PATH_FLAGS"]:
        return []
    return [path.strip() for path in env["PROTOC_PATH_FLAGS"].split("--proto_path=")]


def _protoc_emitter(target, source, env):
    """Process target, sources, and flags"""

    isDebug = env.get("PROTOC_DEBUG", False)

    def _print(*prtList):
        if not isDebug:
            return
        print(*prtList)

    _checkEnv(env)

    # always ignore target
    target = []

    # suffix
    protoc_suffix = env.subst("$PROTOC_SUFFIX")

    protoc_h_suffix = env.subst("$PROTOC_HSUFFIX")
    protoc_cc_suffix = env.subst("$PROTOC_CCSUFFIX")
    protoc_grpc_h_suffix = env.subst("$PROTOC_GRPC_HSUFFIX")
    protoc_grpc_cc_suffix = env.subst("$PROTOC_GRPC_CCSUFFIX")

    protoc_py_suffix = env.subst("$PROTOC_PYSUFFIX")
    protoc_grpc_py_suffix = env.subst("$PROTOC_GRPC_PYSUFFIX")

    protoc_java_suffix = env.subst("$PROTOC_JAVASUFFIX")
    protoc_grpc_java_suffix = env.subst("$PROTOC_GRPC_JAVASUFFIX")

    includePath = _getIncludes(env)
    protoPath = []

    # produce proper targets
    for src in source:
        srcPath = os.path.abspath(str(src))
        srcDir = os.path.dirname(srcPath)
        srcName = os.path.basename(srcPath)

        if srcDir not in includePath and srcDir not in protoPath:
            protoPath.append(srcDir)

        # create stem by remove the $PROTOC_SUFFIX or take a guess
        if srcName.endswith(protoc_suffix):
            stem = srcName[: -len(protoc_suffix)]
        else:
            stem = srcName
        _print("stem:", stem)

        ###############
        # C++
        ###############
        if env["PROTOC_CCOUT"]:
            out = env["PROTOC_CCOUT"]
            base = os.path.join(out.abspath, stem)
            target += [File(base + protoc_h_suffix), File(base + protoc_cc_suffix)]
            if env["PROTOC_GRPC_CC"]:
                target += [
                    File(base + protoc_grpc_h_suffix),
                    File(base + protoc_grpc_cc_suffix),
                ]

        ###############
        # Python
        ###############
        if env["PROTOC_PYOUT"]:
            out = env["PROTOC_PYOUT"]
            base = os.path.join(out.abspath, stem)
            target.append(File(base + protoc_py_suffix))
            if env["PROTOC_GRPC_PY"]:
                target.append(File(base + protoc_grpc_py_suffix))

        ###############
        # Java
        ###############
        if env["PROTOC_JAVAOUT"]:
            out = env["PROTOC_JAVAOUT"]
            _1, _2 = _getJavaTargets(
                srcPath,
                out.abspath,
                protoc_suffix,
                protoc_java_suffix,
                protoc_grpc_java_suffix,
            )
            target += _1
            if env["PROTOC_GRPC_JAVA"]:
                target += _2

    # flag --proto_path, -I
    flags = SCons.Util.CLVar("")
    for path in protoPath:
        flags.append(
            "--proto_path=" + (path if isinstance(path, str) else str(path.abspath))
        )

    # updated flags
    env["PROTOC_SOURCES_PATH_FLAGS"] = str(flags)

    _print("-" * 50)
    _print(
        "flags:\n"
        + env.subst("${PROTOC_FLAGS}", target=target, source=source).replace(" ", "\n")
    )
    _print(
        "path flags:\n"
        + env.subst("${PROTOC_PATH_FLAGS}", target=target, source=source).replace(
            " ", "\n"
        )
    )
    _print(
        "source path flags:\n"
        + env.subst(
            "${PROTOC_SOURCES_PATH_FLAGS}", target=target, source=source
        ).replace(" ", "\n")
    )
    _print(
        "targets:\n"
        + env.subst("${TARGETS}", target=target, source=source).replace(" ", "\n")
    )
    _print(
        "sources:\n"
        + env.subst("${SOURCES}", target=target, source=source).replace(" ", "\n")
    )
    _print("-" * 50)

    return target, source


_protoc_builder = Builder(
    action=Action("$PROTOC_COM", "$PROTOC_COMSTR"),
    suffix="$PROTOC_CCSUFFIX",
    src_suffix="$PROTOC_SUFFIX",
    emitter=_protoc_emitter,
)


def _multiGet(kwd, defaultVal, kwargs, env):
    return kwargs.get(kwd) or env.get(kwd) or defaultVal


def _detect(env, kwargs):
    """Try to find the Protoc compiler"""
    return _multiGet("PROTOC", "", env, kwargs) or env.Detect(protocs)


def generate(env, **kwargs):
    """Add Builders and construction variables."""
    env.SetDefault(
        PROTOC=_detect(env, kwargs),
        # Additional command-line flags
        PROTOC_FLAGS=_multiGet("PROTOC_FLAGS", SCons.Util.CLVar(""), env, kwargs),
        # Source path(s)
        PROTOC_PATH_FLAGS=_multiGet(
            "PROTOC_PATH_FLAGS", SCons.Util.CLVar(""), env, kwargs
        ),
        PROTOC_SOURCES_PATH_FLAGS=_multiGet(
            "PROTOC_SOURCES_PATH_FLAGS", SCons.Util.CLVar(""), env, kwargs
        ),
        PROTOC_PATH=_multiGet("PROTOC_PATH", SCons.Util.CLVar(""), env, kwargs),
        # Suffixies / prefixes
        PROTOC_SUFFIX=_multiGet("PROTOC_SUFFIX", ".proto", env, kwargs),
        # Protoc command
        PROTOC_COM="$PROTOC $PROTOC_FLAGS $PROTOC_PATH_FLAGS $PROTOC_SOURCES_PATH_FLAGS $SOURCES.abspath",
        PROTOC_COMSTR="$PROTOC $PROTOC_FLAGS $PROTOC_PATH_FLAGS $PROTOC_SOURCES_PATH_FLAGS $SOURCES.abspath",
        ###############
        # C++
        ###############
        # suffixes
        PROTOC_HSUFFIX=_multiGet("PROTOC_HSUFFIX", ".pb.h", env, kwargs),
        PROTOC_CCSUFFIX=_multiGet("PROTOC_CCSUFFIX", ".pb.cc", env, kwargs),
        PROTOC_GRPC_HSUFFIX=_multiGet("PROTOC_GRPC_HSUFFIX", ".grpc.pb.h", env, kwargs),
        PROTOC_GRPC_CCSUFFIX=_multiGet(
            "PROTOC_GRPC_CCSUFFIX", ".grpc.pb.cc", env, kwargs
        ),
        # plug-in
        PROTOC_GRPC_CC=_multiGet("PROTOC_GRPC_CC", "", env, kwargs),
        # output
        PROTOC_CCOUT=_multiGet("PROTOC_CCOUT", "", env, kwargs),
        ###############
        # Python
        ###############
        # suffixes
        PROTOC_PYSUFFIX=_multiGet("PROTOC_PYSUFFIX", "_pb2.py", env, kwargs),
        PROTOC_GRPC_PYSUFFIX=_multiGet(
            "PROTOC_GRPC_PYSUFFIX", "_pb2_grpc.py", env, kwargs
        ),
        # plug-in
        PROTOC_GRPC_PY=_multiGet("PROTOC_GRPC_PY", "", env, kwargs),
        # output
        PROTOC_PYOUT=_multiGet("PROTOC_PYOUT", "", env, kwargs),
        ###############
        # Java
        ###############
        # suffixes
        PROTOC_JAVASUFFIX=_multiGet("PROTOC_JAVASUFFIX", ".java", env, kwargs),
        PROTOC_GRPC_JAVASUFFIX=_multiGet(
            "PROTOC_GRPC_JAVASUFFIX", "Grpc.java", env, kwargs
        ),
        # plug-in
        PROTOC_GRPC_JAVA=_multiGet("PROTOC_GRPC_JAVA", "", env, kwargs),
        # output
        PROTOC_JAVAOUT=_multiGet("PROTOC_JAVAOUT", "", env, kwargs),
    )

    env["BUILDERS"]["Protoc"] = _protoc_builder


def exists(env):
    return _detect(env, {})
