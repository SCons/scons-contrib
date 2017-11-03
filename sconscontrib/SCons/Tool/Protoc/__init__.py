"""
Google's Protoc compiler builder

This builder invokes the protoc compiler to generate C++, Python, and Java
files for both protobuf messages and GRPC services.

Original authors: Peter Cooner, Scott Stafford, Steven Haywood (may be more!)
Modified by Bassem Girgis

"""

from __future__ import print_function

import os
import SCons.Util
from SCons.Script import Builder, Action

protocs = ['protoc']

def _getJavaTargets(filePath,
                    outPath,
                    protoc_suffix,
                    protoc_java_suffix,
                    protoc_grpc_java_suffix):
    isMultiFile = False
    isJavaPackage = False
    packagePath = ''
    outerClassName = os.path.basename(filePath).replace(protoc_suffix, '').title()
    messages = []
    services = []
    with open(filePath, 'r') as srcfile:
        for line in srcfile:
            if 'option java_multiple_files' in line and 'true' in line:
                isMultiFile=True
                continue
            
            if 'option java_package' in line:
                packagePath = line.split('=')[1].strip().replace('"', '').replace(';', '').replace('.', os.path.sep)
                isJavaPackage = True
                continue
            
            if 'package' in line and not isJavaPackage:
                packagePath = line.split(' ')[1].strip().replace(';', '')
                continue
            
            if 'option java_outer_classname' in line:
                outerClassName = line.split('=')[1].strip().replace('"', '').replace(';', '')
                continue
            
            if 'message' == line.split(' ')[0]:
                messages.append(line.split(' ')[1])
                continue
            
            if 'service' == line.split(' ')[0]:
                services.append(line.split(' ')[1])
                continue
            
    
    def _append(listObj,
                fileName,
                suffix):
        if packagePath:
            listObj.append(os.path.join(outPath, packagePath, fileName + suffix))
        else:
            listObj.append(os.path.join(outPath, fileName + suffix))
    
    targets = []
    grpcTargets = []
    
    if isMultiFile:
        for msg in messages:
            _append(targets, msg, protoc_java_suffix)
            _append(targets, msg + 'OrBuilder', protoc_java_suffix)
    
    for srcv in services:
        _append(grpcTargets, srcv, protoc_grpc_java_suffix)
    
    _append(targets, outerClassName, protoc_java_suffix)
    
    return targets, grpcTargets


def _protoc_emitter(target, source, env):
    """Process target, sources, and flags"""
    from SCons.Script import File, Dir
    
    isDebug = env.get('PROTOC_DEBUG', False)
    def _print(*prtList):
        if not isDebug:
            return
        print(*prtList)
    
    # always ignore target
    target = []
    
    # suffix
    protoc_suffix = env.subst('$PROTOC_SUFFIX')
    
    # fetch all protoc flags
    if env['PROTOC_FLAGS']:
        protocflags = env.subst("$PROTOC_FLAGS",
                                target=target,
                                source=source)
        flags = SCons.Util.CLVar(protocflags)
    else:
        flags = SCons.Util.CLVar('')
    
    ###############
    # C++
    ###############
    
    protoc_h_suffix = env.subst('$PROTOC_HSUFFIX')
    protoc_cc_suffix = env.subst('$PROTOC_CCSUFFIX')
    protoc_grpc_h_suffix = env.subst('$PROTOC_GRPC_HSUFFIX')
    protoc_grpc_cc_suffix = env.subst('$PROTOC_GRPC_CCSUFFIX')
    
    # flag --cpp_out
    if env['PROTOC_CCOUT']:
        env['PROTOC_CCOUT'] = Dir(env['PROTOC_CCOUT'])
        flags.append('--cpp_out=${PROTOC_CCOUT.abspath}')
    
    # flag --plugin=protoc-gen-grpc-cpp
    if env['PROTOC_GRPC_CC']:
        env['PROTOC_GRPC_CC'] = File(env['PROTOC_GRPC_CC'])
        flags.append('--plugin=protoc-gen-grpc-cpp=${PROTOC_GRPC_CC.abspath}')
        # flag --grpc-cpp_out
        if env['PROTOC_CCOUT']:
            flags.append('--grpc-cpp_out=${PROTOC_CCOUT.abspath}')
    
    ###############
    # Python
    ###############
    
    protoc_py_suffix = env.subst('$PROTOC_PYSUFFIX')
    protoc_grpc_py_suffix = env.subst('$PROTOC_GRPC_PYSUFFIX')
    
    # flag --python_out
    if env['PROTOC_PYOUT']:
        env['PROTOC_PYOUT'] = Dir(env['PROTOC_PYOUT'])
        flags.append('--python_out=${PROTOC_PYOUT.abspath}')
    
    # flag --plugin=protoc-gen-grpc-python
    if env['PROTOC_GRPC_PY']:
        env['PROTOC_GRPC_PY'] = File(env['PROTOC_GRPC_PY'])
        flags.append('--plugin=protoc-gen-grpc-python=${PROTOC_GRPC_PY.abspath}')
        # flag --grpc-python_out
        if env['PROTOC_PYOUT']:
            flags.append('--grpc-python_out=${PROTOC_PYOUT.abspath}')
    
    ###############
    # Java
    ###############
    
    protoc_java_suffix = env.subst('$PROTOC_JAVASUFFIX')
    protoc_grpc_java_suffix = env.subst('$PROTOC_GRPC_JAVASUFFIX')
    
    # flag --java_out
    if env['PROTOC_JAVAOUT']:
        env['PROTOC_JAVAOUT'] = Dir(env['PROTOC_JAVAOUT'])
        flags.append('--java_out=${PROTOC_JAVAOUT.abspath}')
    
    # flag --plugin=protoc-gen-grpc-java
    if env['PROTOC_GRPC_JAVA']:
        env['PROTOC_GRPC_JAVA'] = File(env['PROTOC_GRPC_JAVA'])
        flags.append('--plugin=protoc-gen-grpc-java=${PROTOC_GRPC_JAVA.abspath}')
        # flag --grpc-java_out
        if env['PROTOC_JAVAOUT']:
            flags.append('--grpc-java_out=${PROTOC_JAVAOUT.abspath}')
    
    # flag --proto_path, -I
    proto_path = []
    if env['PROTOC_PATH']:
        inc = env['PROTOC_PATH']
        if SCons.Util.is_List(inc):
            for path in inc:
                path = Dir(path)
                _print("path:", path)
                proto_path.append(path)
        elif SCons.Util.is_Scalar(inc):
            path = Dir(inc)
            _print("path:", path)
            proto_path.append(path)
    
    # produce proper targets
    for src in source:
        srcPath = os.path.abspath(str(src))
        srcDir = os.path.dirname(srcPath)
        srcName = os.path.basename(srcPath)
        
        if srcDir not in proto_path:
            proto_path.append(srcDir)
        
        # create stem by remove the $PROTOC_SUFFIX or take a guess
        if srcName.endswith(protoc_suffix):
            stem = srcName[:-len(protoc_suffix)]
        else:
            stem = srcName
        _print("stem:", stem)
        
        #
        # C++
        #
        if env['PROTOC_CCOUT']:
            out = env['PROTOC_CCOUT']
            base = os.path.join(out.abspath, stem)
            target += [File(base + protoc_h_suffix),
                       File(base + protoc_cc_suffix)]
            if env['PROTOC_GRPC_CC']:
                target += [File(base + protoc_grpc_h_suffix),
                           File(base + protoc_grpc_cc_suffix)]
        
        #
        # Python
        #
        if env['PROTOC_PYOUT']:
            out = env['PROTOC_PYOUT']
            base = os.path.join(out.abspath, stem)
            target.append(File(base + protoc_py_suffix))
            if env['PROTOC_GRPC_PY']:
                target.append(File(base + protoc_grpc_py_suffix))
        
        #
        # Java
        #
        if env['PROTOC_JAVAOUT']:
            out = env['PROTOC_JAVAOUT']
            _1, _2 = _getJavaTargets(srcPath,
                                     out.abspath,
                                     protoc_suffix,
                                     protoc_java_suffix,
                                     protoc_grpc_java_suffix)
            target += _1
            if env['PROTOC_GRPC_JAVA']:
                target += _2
        
    
    for path in proto_path:
        flags.append('--proto_path=' + \
                     path if isinstance(path, str) else \
                    str(path.abspath))
    
    # updated flags
    env['PROTOC_FLAGS'] = str(flags)
    
    _print("flags:", flags)
    _print("targets:",
           env.subst("${TARGETS}",
                     target=target,
                     source=source))
    _print("sources:",
           env.subst("${SOURCES}",
                     target=target,
                     source=source))
    
    return target, source

_protoc_builder = Builder(
    action = Action('$PROTOC_COM', '$PROTOC_COMSTR'),
    suffix = '$PROTOC_CCSUFFIX',
    src_suffix = '$PROTOC_SUFFIX',
    emitter = _protoc_emitter,
)

def _multiGet(kwd,
              defaultVal,
              kwargs,
              env):
  return kwargs.get(kwd) or \
         env.get(kwd) or \
         defaultVal

def _detect(env,
            kwargs):
    """Try to find the Protoc compiler"""
    protoc = _multiGet('PROTOC',
                       '',
                       env,
                       kwargs) or \
             env.Detect(protocs)
    if protoc:
        return protoc
    raise SCons.Errors.StopError(
        "Could not detect protoc Compiler")
    

def generate(env,
             **kwargs):
    """Add Builders and construction variables."""
    env.SetDefault(
        
        PROTOC = _detect(env, kwargs),
        
        # Additional command-line flags
        PROTOC_FLAGS = _multiGet('PROTOC_FLAGS',
                                 SCons.Util.CLVar(''),
                                 env,
                                 kwargs),
        
        # Source path(s)
        PROTOC_PATH = _multiGet('PROTOC_PATH',
                                SCons.Util.CLVar(''),
                                env,
                                kwargs),
        
        # Suffixies / prefixes
        PROTOC_SUFFIX = _multiGet('PROTOC_SUFFIX',
                                  '.proto',
                                  env,
                                  kwargs),
        
        # Protoc command
        PROTOC_COM = '$PROTOC $PROTOC_FLAGS $SOURCES.abspath',
        PROTOC_COMSTR = '$PROTOC $PROTOC_FLAGS $SOURCES.abspath',
        
        #
        # C++
        #
        
        # suffixes
        PROTOC_HSUFFIX  = _multiGet('PROTOC_HSUFFIX',
                                    '.pb.h',
                                    env,
                                    kwargs),
        PROTOC_CCSUFFIX = _multiGet('PROTOC_CCSUFFIX',
                                    '.pb.cc',
                                    env,
                                    kwargs),
        
        PROTOC_GRPC_HSUFFIX  = _multiGet('PROTOC_GRPC_HSUFFIX',
                                         '.grpc.pb.h',
                                         env,
                                         kwargs),
        PROTOC_GRPC_CCSUFFIX = _multiGet('PROTOC_GRPC_CCSUFFIX',
                                         '.grpc.pb.cc',
                                         env,
                                         kwargs),
        
        # plug-in
        PROTOC_GRPC_CC = _multiGet('PROTOC_GRPC_CC',
                                   '',
                                   env,
                                   kwargs),
        
        # output
        PROTOC_CCOUT = _multiGet('PROTOC_CCOUT',
                                 '',
                                 env,
                                 kwargs),
        
        #
        # Python
        #
        
        # suffixes
        PROTOC_PYSUFFIX      = _multiGet('PROTOC_PYSUFFIX',
                                         '_pb2.py',
                                         env,
                                         kwargs),
        PROTOC_GRPC_PYSUFFIX = _multiGet('PROTOC_GRPC_PYSUFFIX',
                                         '_pb2_grpc.py',
                                         env,
                                         kwargs),
        
        # plug-in
        PROTOC_GRPC_PY   = _multiGet('PROTOC_GRPC_PY',
                                     '',
                                     env,
                                     kwargs),
        
        # output
        PROTOC_PYOUT = _multiGet('PROTOC_PYOUT',
                                 '',
                                 env,
                                 kwargs),
        
        #
        # Java
        #
        
        # suffixes
        PROTOC_JAVASUFFIX      = _multiGet('PROTOC_JAVASUFFIX',
                                           '.java',
                                           env,
                                           kwargs),
        PROTOC_GRPC_JAVASUFFIX = _multiGet('PROTOC_GRPC_JAVASUFFIX',
                                           'Grpc.java',
                                           env,
                                           kwargs),
        
        # plug-in
        PROTOC_GRPC_JAVA = _multiGet('PROTOC_GRPC_JAVA',
                                     '',
                                     env,
                                     kwargs),
        
        # output
        PROTOC_JAVAOUT = _multiGet('PROTOC_JAVAOUT',
                                   '',
                                   env,
                                   kwargs),
        
    )
    
    env['BUILDERS']['Protoc'] = _protoc_builder
    

def exists(env):
    return _detect(env, {})
