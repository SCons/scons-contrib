# MIT License
#
# Copyright The SCons Foundation
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

"""SCons Tool for AVR-GCC.

"""


import os
import SCons
from SCons.Tool import (gcc,gxx,gas,ar,link)

def createRomBuilder(env):
    """This is a utility function that creates the Rom
    Builder in an Environment if it is not there already.

    If it is already there, we return the existing one.
    """

    try:
        program = env['BUILDERS']['Rom']
    except KeyError:
        rom = SCons.Builder.Builder(
                                    action=SCons.Action.Action("$ROMCOM"),
                                    suffix='$ROMSUFFIX',
                                    single_source=1)
        env['BUILDERS']['Rom'] = rom

    return rom


def asm_emitter(target, source, env):
    """This emitter is useful when two files with the same name
    but different suffix exists (file.c and file.S) and you want compile both
    """
    asm_suffix = env.subst("$ASMSUFFIX")
    for s in source:
        src = str(s)
        if src.endswith(asm_suffix):
            target = src[: -len(asm_suffix)]+'_S'+env.subst("$OBJSUFFIX")
    return (target, source)

def SetGccAvrVersion(self, version):
    """This Method is used to set the version of avr gcc toolchain
    """
    self['GCCAVRVER'] = version
    self.PrependUnique(CPPPATH=[
        os.path.join('$GCCAVRDIR','lib','gcc','avr','$GCCAVRVER','include'),
        os.path.join('$GCCAVRDIR','lib','gcc','avr','$GCCAVRVER','include-fixed'),
        os.path.join('$GCCAVRDIR','avr','include')
    ])

def SetGccAvrENVPath(self, gccavr_dir):
    """This Method is used to set the gccavr_dir to the PATH
    """
    self.PrependENVPath('PATH', os.path.join(gccavr_dir, 'bin'))

def generate(env):
    env.AddMethod(SetGccAvrVersion)
    env.AddMethod(SetGccAvrENVPath)

    env.SetGccAvrVersion('7.3.0') #set default toolchain version
    #load support of defaults builders
    SCons.Tool.gcc.generate(env)
    SCons.Tool.gxx.generate(env)
    SCons.Tool.gas.generate(env)
    SCons.Tool.ar.generate(env)
    SCons.Tool.link.generate(env)

    #change some default behaviour to suit the avr-gcc toolchain:
    env['PROGSUFFIX'] = '.elf' #Used in Program Builder
    env['OBJSUFFIX'] = '.o'    #Used in Program Builder
    env['GCCPREFIX'] = 'avr-'  #Used in CC CXX AR LINK Action

    #gcc
    env['CC'] = '${GCCPREFIX}gcc${GCCSUFFIX}'
    env['CCFLAGS'] = SCons.Util.CLVar('-std=gnu11 -pedantic -Wall -Wextra -Wno-unused-parameter')

    #asm
    env['AS'] = env['CC']
    env['ASFLAGS'] = '$CCFLAGS -x assembler-with-cpp $_CCCOMCOM'
    env['ASMSUFFIX'] = '.S'
    env['BUILDERS']['Object'].add_action('.S', SCons.Defaults.ASPPAction) #be sure ASPPAction is used
    env['BUILDERS']['Object'].add_emitter('.S',asm_emitter) #change target name so that file1.c and file1.S can be both exist

    #gxx
    env['CXX'] = '${GCCPREFIX}g++${GCCSUFFIX}'
    env['CXXCOM']     = '$CXX -o $TARGET -c $CXXFLAGS $_CCCOMCOM $SOURCES' #we don't want to use $CCFLAGS here
    env['CXXFLAGS']   = SCons.Util.CLVar('-w -std=gnu++11 -fpermissive -fno-exceptions -fno-threadsafe-statics -Wno-error=narrowing')
    env['CXXFILESUFFIX'] = '.cpp'

    #ar
    env['AR'] = '${GCCPREFIX}gcc-ar${GCCSUFFIX}'
    env['ARFLAGS'] = SCons.Util.CLVar('rcs')
    env['RANLIB'] = '${GCCPREFIX}gcc-ranlib${GCCSUFFIX}'

    #link
    env['LINK'] = '${GCCPREFIX}gcc${GCCSUFFIX}'
    env['LINKERSCRIPT'] = SCons.Util.CLVar('')
    env['MAPFILE'] = True
    env['_MAPFILE'] = ('MAPFILE' in env) and '-Xlinker -Map -Xlinker ${TARGET.base}.map' or ''
    env['_LINKFILE'] = '${LINKERSCRIPT and ("-T%s" % LINKERSCRIPT) or ""}'
    env['LINKFLAGS'] = ' $CCFLAGS $_LINKFILE $_MAPFILE '

    #rom Builder
    env['ROMCOM'] = '${GCCPREFIX}objcopy -O ihex -R .eeprom $SOURCE $TARGET'
    env['ROMFORMAT'] = 'INHX'
    env['ROMSUFFIX'] = '.hex'
    createRomBuilder(env)


def exists(env):
    return env.get('GCCAVRVER','')
