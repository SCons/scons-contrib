SCons-Xcode
===========

A tool for SCons to enable the generation of Xcode project files.  Unlike
CMake, the idea here is to get Xcode to run ``scons``, so that the
``SConstruct`` file is still the master project file.

Loading the tool
----------------

To use the tool, copy ``__init__.py`` in this directory to a directory
``xcode`` in your tool path.  See `the SCons documentation`_ for more
information on where you can install the file.

You can also clone the repository directly into your ``site_tools`` directory
with::

  hg clone https://bitbucket.org/al45tair/scons-xcode xcode

Next, add the tool to your environment with something like the following:

.. code:: python

  env = Environment(tools=['default', 'xcode'])

.. note:: You need to include ``default`` so that the built-in tools remain
          available.

.. _`the Scons documentation`:
   http://scons.org/doc/production/HTML/scons-user.html#idp1397517020

Usage
-----

To generate an Xcode project file, simply add a call to ``env.XCodeProject``
to your ``SConstruct`` file:

.. code:: python

  env = Environment(tools=['default', 'xcode'])

  myprog = env.Program('build/MyProg', ['src/main.cc'])

  env.XcodeProject('MyProject.xcodeproj',
                   products=myprog)

The resulting Xcode project file will contain only a single group, "Products",
in which you will see the ``MyProg`` program.  It will also contain two legacy
build system targets named "Everything" and "MyProg"; the former will run
``scons`` without specifying a target, while the latter will explicitly
specify ``MyProg``.  The Xcode project will also have a shared build scheme
defined for ``MyProg`` that will cause it to run ``MyProg`` if asked to
run/debug (this only happens for ``env.Program`` at present).

Obviously that project file is very minimal; you will probably want to include
your own groups and source files in practice, which you can do by passing a
dictionary into the ``XcodeProject`` builder, e.g.:

.. code:: python

  env.XcodeProject('MyProject.xcodeproj',
                   groups={ 'Headers': [ 'src/MyProg.h' ],
                            'Sources': [ 'src/main.cc', 'src/utils.cc' ],
                            'Documentation': [ 'doc/README.rst' ] },
                   products=myprog)

Note also that ``products`` accepts a list, so you can provide multiple
products, in which case you will end up with additional targets in your Xcode
project file.

Using the ``XcodeProject`` builder also adds a couple of options to your
SConstruct file, namely

  --xcode-action=ACTION    Specifies the action Xcode was trying to take when it
                           ran ``scons``
  --xcode-variant=VARIANT  Specifies the build configuration Xcode was using
                           when it ran ``scons``

These options are used by the legacy build targets automatically.

The ``Clean`` action is handled automatically by the builder; if you wish to
use variants, you can do so, for instance:

.. code:: python

  variant = 'Debug'
  if GetOption('xcode_variant') == 'Release':
      variant = 'Release'

  if variant == 'Debug':
      env.Append(CCFLAGS=['-g'])
  else:
      env.Append(CCFLAGS=['-Os'])

  ...

  env.XcodeProject(...,
                   variants=['Debug', 'Release'],
                   ...)

Take care if you do something like this:

.. code:: python

  myprog = env.Program(os.path.join('build', variant, 'MyProg'),
                       ['src/main.cc'])

as you will find that the automatically generated build scheme will use the
setting of ``variant`` that was active when you generated the Xcode project
file (in this case, most likely the default in your ``scons`` file).  You
probably want to make sure the default is "Debug", or at least make sure it
has some symbols.
