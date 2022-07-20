######################
gccavr Tool for SCons
######################

This Tool enable the use ov avr-gcc toolchain for SCons.

Usage
#####

You activate the Tool by adding it to the ``tools`` list, for example:
.. code:: python

    cc = env.Clone(tools=['gccavr'])

Then you have to provide the base path of your toolchain and its version:
.. code:: python

    cc.SetGccAvrENVPath(gccavr_dir)
    cc.SetGccAvrVersion('7.3.0')

**Note:**
    1. ``gccavr_dir`` is the directory containing bin/ folder (which has the executable avr-gcc, avr-g++, ecc..)
    2. ``'7.3.0'`` is the folder name (i.e. the version) in lib/gcc/avr/<VERSION>/include

That's it, now you can use the default Builders Object, Program, StaticLibrary (and Rom) to build your project:
The following Sconcript builds a ``main.c`` file used to create an executable for Arduino Uno
.. code:: python

    import os

    def build_program(env):
        return env.Program(
            target='helloworld',
            source=[
                env.File("main.c"),
            ],
        )


    Import('env')
    gccavr_dir = r"C:\Program Files (x86)\Arduino\hardware\tools\avr"

    cc = env.Clone(tools=['gccavr'])
    cc.SetGccAvrVersion('7.3.0')
    cc.SetGccAvrENVPath(gccavr_dir)
    cc.Prepend(LINKFLAGS='-Wl,-gc-sections -fuse-linker-plugin -lm')
    cc.Prepend(CCFLAGS='-mmcu=atmega328p '
                    '-Os -fdata-sections -ffunction-sections -flto')
    cc.Prepend(CPPDEFINES={'F_CPU': '16000000L',
                            'ARDUINO': 10819,
                            'ARDUINO_AVR_UNO':1,
                            'ARDUINO_ARCH_MEGAAVR': 1,
                            'ARDUINO_ARCH_AVR':1,
                            })
    app = build_program(cc)
    hex = cc.Rom(app)

