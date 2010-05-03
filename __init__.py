
"""SCons.Tool.qt4

Tool-specific initialization for Qt4.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

#
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007 The SCons Foundation
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

import os.path
import re

import SCons.Action
import SCons.Builder
import SCons.Defaults
import SCons.Scanner
import SCons.Tool
import SCons.Util

class ToolQt4Warning(SCons.Warnings.Warning):
    pass

class GeneratedMocFileNotIncluded(ToolQt4Warning):
    pass

class QtdirNotFound(ToolQt4Warning):
    pass

SCons.Warnings.enableWarningClass(ToolQt4Warning)

qrcinclude_re = re.compile(r'<file[^>]*>([^<]*)</file>', re.M)

def transformToWinePath(path) :
    return os.popen('winepath -w "%s"'%path).read().strip().replace('\\','/')

header_extensions = [".h", ".hxx", ".hpp", ".hh"]
if SCons.Util.case_sensitive_suffixes('.h', '.H'):
    header_extensions.append('.H')
# TODO: The following two lines will work when integrated back to SCons
# TODO: Meanwhile the third line will do the work
#cplusplus = __import__('c++', globals(), locals(), [])
#cxx_suffixes = cplusplus.CXXSuffixes
cxx_suffixes = [".c", ".cxx", ".cpp", ".cc"]

def checkMocIncluded(target, source, env):
    moc = target[0]
    cpp = source[0]
    # looks like cpp.includes is cleared before the build stage :-(
    # not really sure about the path transformations (moc.cwd? cpp.cwd?) :-/
    path = SCons.Defaults.CScan.path_function(env, moc.cwd)
    includes = SCons.Defaults.CScan(cpp, env, path)
    if not moc in includes:
        SCons.Warnings.warn(
            GeneratedMocFileNotIncluded,
            "Generated moc file '%s' is not included by '%s'" %
            (str(moc), str(cpp)))

def find_file(filename, paths, node_factory):
    for dir in paths:
        node = node_factory(filename, dir)
        if node.rexists():
            return node
    return None

class _Automoc:
    """
    Callable class, which works as an emitter for Programs, SharedLibraries and
    StaticLibraries.
    """

    def __init__(self, objBuilderName):
        self.objBuilderName = objBuilderName
        # some regular expressions:
        # Q_OBJECT detection
        self.qo_search = re.compile(r'[^A-Za-z0-9]Q_OBJECT[^A-Za-z0-9]')
        # cxx and c comment 'eater'
        self.ccomment = re.compile(r'/\*(.*?)\*/')
        self.cxxcomment = re.compile(r'//.*$')
        #     CURRENTLY THERE IS NO TEST CASE FOR THAT
        
        self.auto_scan = True
        self.auto_scan_strategy = 0
        self.gobble_comments = 0
        self.debug = 0
        
    def init_env_vars(self, env):
        """
        Set some class internal variables, based on the current environment.
        Is executed once in the __call__ routine.  
        """
        try:
            if int(env.subst('$QT4_AUTOSCAN')) == 0:
                self.auto_scan = False
        except ValueError:
            pass
        try:
            self.auto_scan_strategy = int(env.subst('$QT4_AUTOSCAN_STRATEGY'))
        except ValueError:
            pass
        try:
            self.gobble_comments = int(env.subst('$QT4_GOBBLECOMMENTS'))
        except ValueError:
            pass
        try:
            self.debug = int(env.subst('$QT4_DEBUG'))
        except ValueError:
            pass

    def __automoc_strategy_simple(self, env, cpp, cpp_contents, out_sources):
        """
        Default Automoc strategy (Q_OBJECT driven): detect a header file
        (alongside the current cpp/cxx) that contains a Q_OBJECT
        macro...and MOC it.
        If a Q_OBJECT macro is also found in the cpp/cxx itself,
        it gets MOCed too.
        """
        
        h=None
        for h_ext in header_extensions:
            # try to find the header file in the corresponding source
            # directory
            hname = self.splitext(cpp.name)[0] + h_ext
            h = find_file(hname, (cpp.get_dir(),), env.File)
            if h:
                if self.debug:
                    print "scons: qt4: Scanning '%s' (header of '%s')" % (str(h), str(cpp))
                h_contents = h.get_contents()
                if self.gobble_comments:
                    h_contents = self.ccomment.sub('', h_contents)
                    h_contents = self.cxxcomment.sub('', h_contents)
                break
        if not h and self.debug:
            print "scons: qt4: no header for '%s'." % (str(cpp))
        if h and self.qo_search.search(h_contents):
            # h file with the Q_OBJECT macro found -> add moc_cpp
            moc_cpp = env.Moc4(h)
            moc_o = self.objBuilder(moc_cpp)
            out_sources.append(moc_o)
            if self.debug:
                print "scons: qt4: found Q_OBJECT macro in '%s', moc'ing to '%s'" % (str(h), str(moc_cpp))
        if cpp and self.qo_search.search(cpp_contents):
            # cpp file with Q_OBJECT macro found -> add moc
            # (to be included in cpp)
            moc = env.Moc4(cpp)
            env.Ignore(moc, moc)
            if self.debug:
                print "scons: qt4: found Q_OBJECT macro in '%s', moc'ing to '%s'" % (str(cpp), str(moc))

    def __automoc_strategy_include_driven(self, env, cpp, cpp_contents, out_sources):
        """
        Automoc strategy #1 (include driven): searches for "include"
        statements of MOCed files in the current cpp/cxx file.
        This strategy tries to add support for the compilation
        of the qtsolutions...
        """
        if self.splitext(str(cpp))[1] in cxx_suffixes:
            added = False
            h_moc = "%s%s%s" % (env.subst('$QT4_XMOCHPREFIX'),
                                self.splitext(cpp.name)[0],
                                env.subst('$QT4_XMOCHSUFFIX'))
            cxx_moc = "%s%s%s" % (env.subst('$QT4_XMOCCXXPREFIX'),
                                  self.splitext(cpp.name)[0],
                                  env.subst('$QT4_XMOCCXXSUFFIX'))
            inc_h_moc = r'#include\s+"%s"' % h_moc
            inc_cxx_moc = r'#include\s+"%s"' % cxx_moc
            
            # Search for special includes in qtsolutions style
            if cpp and re.search(inc_h_moc, cpp_contents):
                # cpp file with #include directive for a MOCed header found -> add moc
                
                # Try to find header file                    
                h=None
                hname=""
                for h_ext in header_extensions:
                    # Try to find the header file in the
                    # corresponding source directory
                    hname = self.splitext(cpp.name)[0] + h_ext
                    h = find_file(hname, (cpp.get_dir(),), env.File)
                    if h:
                        if self.debug:
                            print "scons: qt4: Scanning '%s' (header of '%s')" % (str(h), str(cpp))
                        h_contents = h.get_contents()
                        if self.gobble_comments:
                            h_contents = self.ccomment.sub('', h_contents)
                            h_contents = self.cxxcomment.sub('', h_contents)
                        break
                if not h and self.debug:
                    print "scons: qt4: no header for '%s'." % (str(cpp))
                if h and self.qo_search.search(h_contents):
                    # h file with the Q_OBJECT macro found -> add moc_cpp
                    moc_cpp = env.XMoc4(h)
                    env.Ignore(moc_cpp, moc_cpp)
                    added = True
                    # Removing file from list of sources, because it is not to be
                    # compiled but simply included by the cpp/cxx file.
                    for idx, s in enumerate(out_sources):
                        if hasattr(s, "sources") and len(s.sources) > 0:
                            if str(s.sources[0]) == h_moc:
                                out_sources.pop(idx)
                                break
                    if self.debug:
                        print "scons: qt4: found Q_OBJECT macro in '%s', moc'ing to '%s'" % (str(h), str(h_moc))
                else:
                    if self.debug:
                        print "scons: qt4: found no Q_OBJECT macro in '%s', but a moc'ed version '%s' gets included in '%s'" % (str(h), inc_h_moc, cpp.name)

            if cpp and re.search(inc_cxx_moc, cpp_contents):
                # cpp file with #include directive for a MOCed cxx file found -> add moc
                if self.qo_search.search(cpp_contents):
                    moc = env.XMoc4(target=cxx_moc, source=cpp)
                    env.Ignore(moc, moc)
                    added = True
                    if self.debug:
                        print "scons: qt4: found Q_OBJECT macro in '%s', moc'ing to '%s'" % (str(cpp), str(moc))
                else:
                    if self.debug:
                        print "scons: qt4: found no Q_OBJECT macro in '%s', although a moc'ed version '%s' of itself gets included" % (cpp.name, inc_cxx_moc)

            if not added:
                # Fallback to default Automoc strategy (Q_OBJECT driven)
               self.__automoc_strategy_simple(env, cpp, cpp_contents, out_sources)
        
    def __call__(self, target, source, env):
        """
        Smart autoscan function. Gets the list of objects for the Program
        or Lib. Adds objects and builders for the special qt4 files.
        """
        self.init_env_vars(env)
        
        # some shortcuts used in the scanner
        self.splitext = SCons.Util.splitext
        self.objBuilder = getattr(env, self.objBuilderName)

        # The following is kind of hacky to get builders working properly (FIXME)
        objBuilderEnv = self.objBuilder.env
        self.objBuilder.env = env
        mocBuilderEnv = env.Moc4.env
        env.Moc4.env = env
        xMocBuilderEnv = env.XMoc4.env
        env.XMoc4.env = env
        
        # make a deep copy for the result; MocH objects will be appended
        out_sources = source[:]

        for obj in source:
            if isinstance(obj,basestring):  # big kludge!
                print "scons: qt4: '%s' MAYBE USING AN OLD SCONS VERSION AND NOT CONVERTED TO 'File'. Discarded." % str(obj)
                continue
            if not obj.has_builder():
                # binary obj file provided
                if self.debug:
                    print "scons: qt4: '%s' seems to be a binary. Discarded." % str(obj)
                continue
            cpp = obj.sources[0]
            if not self.splitext(str(cpp))[1] in cxx_suffixes:
                if self.debug:
                    print "scons: qt4: '%s' is no cxx file. Discarded." % str(cpp) 
                # c or fortran source
                continue
            try:
                cpp_contents = cpp.get_contents()
                if self.gobble_comments:
                    cpp_contents = self.ccomment.sub('', cpp_contents)
                    cpp_contents = self.cxxcomment.sub('', cpp_contents)
            except: continue # may be an still not generated source
            
            if self.auto_scan_strategy == 0:
                # Default Automoc strategy (Q_OBJECT driven)
                self.__automoc_strategy_simple(env, cpp, cpp_contents, out_sources)
            else:
                # Automoc strategy #1 (include driven)
                self.__automoc_strategy_include_driven(env, cpp, cpp_contents, out_sources)

        # restore the original env attributes (FIXME)
        self.objBuilder.env = objBuilderEnv
        env.Moc4.env = mocBuilderEnv
        env.XMoc4.env = xMocBuilderEnv

        return (target, out_sources)

AutomocShared = _Automoc('SharedObject')
AutomocStatic = _Automoc('StaticObject')

def _detect(env):
    """Not really safe, but fast method to detect the Qt4 library"""
    # TODO: check output of "moc -v" for correct version >= 4.0.0
    try: return env['QTDIR']
    except KeyError: pass

    try: return os.environ['QTDIR']
    except KeyError: pass

    moc = env.WhereIs('moc-qt4') or env.WhereIs('moc4') or env.WhereIs('moc')
    if moc:
        QTDIR = os.path.dirname(os.path.dirname(moc))
        SCons.Warnings.warn(
            QtdirNotFound,
            "QTDIR variable is not defined, using moc executable as a hint (QTDIR=%s)" % QTDIR)
        return QTDIR

    raise SCons.Errors.StopError(
        QtdirNotFound,
        "Could not detect Qt 4 installation")
    return None

def generate(env):
    """Add Builders and construction variables for qt4 to an Environment."""

    def locateQt4Command(env, command, qtdir) :
        suffixes = [
            '-qt4',
            '-qt4.exe',
            '4',
            '4.exe',
            '',
            '.exe',
        ]
        triedPaths = []
        for suffix in suffixes :
            fullpath = os.path.join(qtdir,'bin',command + suffix)
            if os.access(fullpath, os.X_OK) :
                return fullpath
            triedPaths.append(fullpath)

        fullpath = env.Detect([command+'-qt4', command+'4', command])
        if not (fullpath is None) : return fullpath

        raise Exception("Qt4 command '" + command + "' not found. Tried: " + ', '.join(triedPaths))

    CLVar = SCons.Util.CLVar
    Action = SCons.Action.Action
    Builder = SCons.Builder.Builder

    env['QTDIR']  = _detect(env)
    # TODO: 'Replace' should be 'SetDefault'
#    env.SetDefault(
    env.Replace(
        QTDIR  = _detect(env),
        QT4_BINPATH = os.path.join('$QTDIR', 'bin'),
        # TODO: This is not reliable to QTDIR value changes but needed in order to support '-qt4' variants
        QT4_MOC = locateQt4Command(env,'moc', env['QTDIR']),
        QT4_UIC = locateQt4Command(env,'uic', env['QTDIR']),
        QT4_RCC = locateQt4Command(env,'rcc', env['QTDIR']),
        QT4_LUPDATE = locateQt4Command(env,'lupdate', env['QTDIR']),
        QT4_LRELEASE = locateQt4Command(env,'lrelease', env['QTDIR']),

        QT4_AUTOSCAN = 1, # Should the qt4 tool try to figure out, which sources are to be moc'ed?
        QT4_AUTOSCAN_STRATEGY = 0, # While scanning for files to moc, should we search for includes in qtsolutions style?
        QT4_GOBBLECOMMENTS = 0, # If set to 1, comments are removed before scanning cxx/h files.
        
        # Some Qt4 specific flags. I don't expect someone wants to
        # manipulate those ...
        QT4_UICFLAGS = CLVar(''),
        QT4_MOCFROMHFLAGS = CLVar(''),
        QT4_MOCFROMCXXFLAGS = CLVar('-i'),
        QT4_QRCFLAGS = '',

        # suffixes/prefixes for the headers / sources to generate
        QT4_UISUFFIX = '.ui',
        QT4_UICDECLPREFIX = 'ui_',
        QT4_UICDECLSUFFIX = '.h',
        QT4_MOCINCPREFIX = '-I',
        QT4_MOCHPREFIX = 'moc_',
        QT4_MOCHSUFFIX = '$CXXFILESUFFIX',
        QT4_MOCCXXPREFIX = '',
        QT4_MOCCXXSUFFIX = '.moc',
        QT4_QRCSUFFIX = '.qrc',
        QT4_QRCCXXSUFFIX = '$CXXFILESUFFIX',
        QT4_QRCCXXPREFIX = 'qrc_',
        QT4_MOCDEFPREFIX = '-D',
        QT4_MOCDEFSUFFIX = '',
        QT4_MOCDEFINES = '${_defines(QT4_MOCDEFPREFIX, CPPDEFINES, QT4_MOCDEFSUFFIX, __env__)}',
        QT4_MOCCPPPATH = [],
        QT4_MOCINCFLAGS = '$( ${_concat(QT4_MOCINCPREFIX, QT4_MOCCPPPATH, INCSUFFIX, __env__, RDirs)} $)',

        # Commands for the qt4 support ...
        QT4_UICCOM = '$QT4_UIC $QT4_UICFLAGS -o $TARGET $SOURCE',
        QT4_MOCFROMHCOM = '$QT4_MOC $QT4_MOCDEFINES $QT4_MOCFROMHFLAGS $QT4_MOCINCFLAGS -o $TARGET $SOURCE',
        QT4_MOCFROMCXXCOM = [
            '$QT4_MOC $QT4_MOCDEFINES $QT4_MOCFROMCXXFLAGS $QT4_MOCINCFLAGS -o $TARGET $SOURCE',
            Action(checkMocIncluded,None)],
        QT4_LUPDATECOM = '$QT4_LUPDATE $SOURCE -ts $TARGET',
        QT4_LRELEASECOM = '$QT4_LRELEASE $SOURCE',
        QT4_RCCCOM = '$QT4_RCC $QT4_QRCFLAGS $SOURCE -o $TARGET',
        
        # Specialized variables for the Extended Automoc support
        # (Strategy #1 for qtsolutions)
        QT4_XMOCHPREFIX = 'moc_',
        QT4_XMOCHSUFFIX = '.cpp',
        QT4_XMOCCXXPREFIX = '',
        QT4_XMOCCXXSUFFIX = '.moc',
        QT4_XMOCFROMHCOM = '$QT4_MOC $QT4_MOCFROMHFLAGS $QT4_MOCINCFLAGS -o $TARGET $SOURCE',
        QT4_XMOCFROMCXXCOM = '$QT4_MOC $QT4_MOCFROMCXXFLAGS $QT4_MOCINCFLAGS -o $TARGET $SOURCE'
                
        )

    # Translation builder
    tsbuilder = Builder(
        action = SCons.Action.Action('$QT4_LUPDATECOM'), #,'$QT4_LUPDATECOMSTR'),
        multi=1
        )
    env.Append( BUILDERS = { 'Ts': tsbuilder } )
    qmbuilder = Builder(
        action = SCons.Action.Action('$QT4_LRELEASECOM'),# , '$QT4_LRELEASECOMSTR'),
        src_suffix = '.ts',
        suffix = '.qm',
        single_source = True
        )
    env.Append( BUILDERS = { 'Qm': qmbuilder } )

    # Resource builder
    def scanResources(node, env, path, arg):
        # I've been careful on providing names relative to the qrc file
        # If that was not needed this code could be simplified a lot
        def recursiveFiles(basepath, path) :
            result = []
            for item in os.listdir(os.path.join(basepath, path)) :
                itemPath = os.path.join(path, item)
                if os.path.isdir(os.path.join(basepath, itemPath)) :
                    result += recursiveFiles(basepath, itemPath)
                else:
                    result.append(itemPath)
            return result
        contents = node.get_contents()
        includes = qrcinclude_re.findall(contents)
        qrcpath = os.path.dirname(node.path)
        dirs = [included for included in includes if os.path.isdir(os.path.join(qrcpath,included))]
        # dirs need to include files recursively
        for dir in dirs :
            includes.remove(dir)
            includes+=recursiveFiles(qrcpath,dir)
        return includes
    qrcscanner = SCons.Scanner.Scanner(name = 'qrcfile',
        function = scanResources,
        argument = None,
        skeys = ['.qrc'])
    qrcbuilder = Builder(
        action = SCons.Action.Action('$QT4_RCCCOM', '$QT4_RCCCOMSTR'),
        source_scanner = qrcscanner,
        src_suffix = '$QT4_QRCSUFFIX',
        suffix = '$QT4_QRCCXXSUFFIX',
        prefix = '$QT4_QRCCXXPREFIX',
        single_source = True
        )
    env.Append( BUILDERS = { 'Qrc': qrcbuilder } )

    # Interface builder
    uic4builder = Builder(
        action = SCons.Action.Action('$QT4_UICCOM', '$QT4_UICCOMSTR'),
        src_suffix='$QT4_UISUFFIX',
        suffix='$QT4_UICDECLSUFFIX',
        prefix='$QT4_UICDECLPREFIX',
        single_source = True
        #TODO: Consider the uiscanner on new scons version
        )
    env['BUILDERS']['Uic4'] = uic4builder

    # Metaobject builder
    mocBld = Builder(action={}, prefix={}, suffix={})
    for h in header_extensions:
        act = SCons.Action.Action('$QT4_MOCFROMHCOM', '$QT4_MOCFROMHCOMSTR')
        mocBld.add_action(h, act)
        mocBld.prefix[h] = '$QT4_MOCHPREFIX'
        mocBld.suffix[h] = '$QT4_MOCHSUFFIX'
    for cxx in cxx_suffixes:
        act = SCons.Action.Action('$QT4_MOCFROMCXXCOM', '$QT4_MOCFROMCXXCOMSTR')
        mocBld.add_action(cxx, act)
        mocBld.prefix[cxx] = '$QT4_MOCCXXPREFIX'
        mocBld.suffix[cxx] = '$QT4_MOCCXXSUFFIX'
    env['BUILDERS']['Moc4'] = mocBld

    # Metaobject builder for the extended auto scan feature 
    # (Strategy #1 for qtsolutions)
    xMocBld = Builder(action={}, prefix={}, suffix={})
    for h in header_extensions:
        act = SCons.Action.Action('$QT4_XMOCFROMHCOM', '$QT4_XMOCFROMHCOMSTR')
        xMocBld.add_action(h, act)
        xMocBld.prefix[h] = '$QT4_XMOCHPREFIX'
        xMocBld.suffix[h] = '$QT4_XMOCHSUFFIX'
    for cxx in cxx_suffixes:
        act = SCons.Action.Action('$QT4_XMOCFROMCXXCOM', '$QT4_XMOCFROMCXXCOMSTR')
        xMocBld.add_action(cxx, act)
        xMocBld.prefix[cxx] = '$QT4_XMOCCXXPREFIX'
        xMocBld.suffix[cxx] = '$QT4_XMOCCXXSUFFIX'
    env['BUILDERS']['XMoc4'] = xMocBld

    # Add the Uic4 Builder to the list of src_builders (registers the
    # *.ui extension with the Environment)     
    static_obj, shared_obj = SCons.Tool.createObjBuilders(env)
    static_obj.src_builder.append('Uic4')
    shared_obj.src_builder.append('Uic4')

    # We use the emitters of Program / StaticLibrary / SharedLibrary
    # to scan for moc'able files
    # We can't refer to the builders directly, we have to fetch them
    # as Environment attributes because that sets them up to be called
    # correctly later by our emitter.
    env.AppendUnique(PROGEMITTER =[AutomocStatic],
                     SHLIBEMITTER=[AutomocShared],
                     LIBEMITTER  =[AutomocStatic],
                    )

    # TODO: Does dbusxml2cpp need an adapter
    env.AddMethod(enable_modules, "EnableQt4Modules")

def enable_modules(self, modules, debug=False, crosscompiling=False) :
    import sys

    validModules = [
        'QtCore',
        'QtGui',
        'QtOpenGL',
        'Qt3Support',
        'QtAssistant', # deprecated
        'QtAssistantClient',
        'QtScript',
        'QtDBus',
        'QtSql',
        'QtSvg',
        # The next modules have not been tested yet so, please
        # maybe they require additional work on non Linux platforms
        'QtNetwork',
        'QtTest',
        'QtXml',
        'QtXmlPatterns',
        'QtUiTools',
        'QtDesigner',
        'QtDesignerComponents',
        'QtWebKit',
        'QtHelp',
        'QtScript',
        'QtScriptTools',
        'QtMultimedia',
        ]
    pclessModules = [
# in qt <= 4.3 designer and designerComponents are pcless, on qt4.4 they are not, so removed.    
#        'QtDesigner',
#        'QtDesignerComponents',
    ]
    staticModules = [
        'QtUiTools',
    ]
    invalidModules=[]
    for module in modules:
        if module not in validModules :
            invalidModules.append(module)
    if invalidModules :
        raise Exception("Modules %s are not Qt4 modules. Valid Qt4 modules are: %s"% (
            str(invalidModules),str(validModules)))

    moduleDefines = {
        'QtScript'   : ['QT_SCRIPT_LIB'],
        'QtSvg'      : ['QT_SVG_LIB'],
        'Qt3Support' : ['QT_QT3SUPPORT_LIB','QT3_SUPPORT'],
        'QtSql'      : ['QT_SQL_LIB'],
        'QtXml'      : ['QT_XML_LIB'],
        'QtOpenGL'   : ['QT_OPENGL_LIB'],
        'QtGui'      : ['QT_GUI_LIB'],
        'QtNetwork'  : ['QT_NETWORK_LIB'],
        'QtCore'     : ['QT_CORE_LIB'],
    }
    for module in modules :
        try : self.AppendUnique(CPPDEFINES=moduleDefines[module])
        except: pass
    debugSuffix = ''
    if sys.platform in ["darwin", "linux2"] and not crosscompiling :
        if debug : debugSuffix = '_debug'
        for module in modules :
            if module not in pclessModules : continue
            self.AppendUnique(LIBS=[module+debugSuffix])
            self.AppendUnique(LIBPATH=[os.path.join("$QTDIR","lib")])
            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include","qt4")])
            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include","qt4",module)])
        pcmodules = [module+debugSuffix for module in modules if module not in pclessModules ]
        if 'QtDBus' in pcmodules:
            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include","qt4","QtDBus")])
        if "QtAssistant" in pcmodules:
            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include","qt4","QtAssistant")])
            pcmodules.remove("QtAssistant")
            pcmodules.append("QtAssistantClient")
        self.ParseConfig('pkg-config %s --libs --cflags'% ' '.join(pcmodules))
        self["QT4_MOCCPPPATH"] = self["CPPPATH"]
        return
    if sys.platform == "win32" or crosscompiling :
        if crosscompiling:
            transformedQtdir = transformToWinePath(self['QTDIR'])
            self['QT4_MOC'] = "QTDIR=%s %s"%( transformedQtdir, self['QT4_MOC'])
        self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include")])
        try: modules.remove("QtDBus")
        except: pass
        if debug : debugSuffix = 'd'
        if "QtAssistant" in modules:
            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include","QtAssistant")])
            modules.remove("QtAssistant")
            modules.append("QtAssistantClient")
        self.AppendUnique(LIBS=[lib+'4'+debugSuffix for lib in modules if lib not in staticModules])
        self.PrependUnique(LIBS=[lib+debugSuffix for lib in modules if lib in staticModules])
        if 'QtOpenGL' in modules:
            self.AppendUnique(LIBS=['opengl32'])
        self.AppendUnique(CPPPATH=[ '$QTDIR/include/'])
        self.AppendUnique(CPPPATH=[ '$QTDIR/include/'+module for module in modules])
        if crosscompiling :
            self["QT4_MOCCPPPATH"] = [
                path.replace('$QTDIR', transformedQtdir)
                    for path in self['CPPPATH'] ]
        else :
            self["QT4_MOCCPPPATH"] = self["CPPPATH"]
        self.AppendUnique(LIBPATH=[os.path.join('$QTDIR','lib')])
        return
    """
    if sys.platform=="darwin" :
        # TODO: Test debug version on Mac
        self.AppendUnique(LIBPATH=[os.path.join('$QTDIR','lib')])
        self.AppendUnique(LINKFLAGS="-F$QTDIR/lib")
        self.AppendUnique(LINKFLAGS="-L$QTDIR/lib") #TODO clean!
        if debug : debugSuffix = 'd'
        for module in modules :
#            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include")])
#            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include",module)])
# port qt4-mac:
            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include", "qt4")])
            self.AppendUnique(CPPPATH=[os.path.join("$QTDIR","include", "qt4", module)])
            if module in staticModules :
                self.AppendUnique(LIBS=[module+debugSuffix]) # TODO: Add the debug suffix
                self.AppendUnique(LIBPATH=[os.path.join("$QTDIR","lib")])
            else :
#                self.Append(LINKFLAGS=['-framework', module])
# port qt4-mac:
                self.Append(LIBS=module)
        if 'QtOpenGL' in modules:
            self.AppendUnique(LINKFLAGS="-F/System/Library/Frameworks")
            self.Append(LINKFLAGS=['-framework', 'AGL']) #TODO ughly kludge to avoid quotes
            self.Append(LINKFLAGS=['-framework', 'OpenGL'])
        self["QT4_MOCCPPPATH"] = self["CPPPATH"]
        return
# This should work for mac but doesn't
#    env.AppendUnique(FRAMEWORKPATH=[os.path.join(env['QTDIR'],'lib')])
#    env.AppendUnique(FRAMEWORKS=['QtCore','QtGui','QtOpenGL', 'AGL'])
    """


def exists(env):
    return _detect(env)
