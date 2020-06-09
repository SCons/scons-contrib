######################
fastcpp Tool for SCons
######################

This Tool is specialized on speeding up large C/CPP builds, measured in terms
of source files.

**!!Disclaimer!!**: For achieving significant speedups, this Tool uses several shortcuts
that might lead to insecure builds. It may work and your builds get faster, but it might also
give you more trouble than you've asked for.
If in doubt, disable the Tool immediately and get back to relying on SCons' default
behaviour for analyzing signatures and implicit dependencies.

You have been warned!

In particular, what this Tool does is:

 1. It installs a very simplified C/CPP scanner, which might not find all dependencies based
    on file includes.
 2. Switches off implicit dependencies for commands like g++ and ar, such that your
    build will not automatically detect when you install a new C++ compiler for example.
    The same holds for executables that you create during your build, and then generate
    further source files with it.
 3. Pre-expands several prefixes and suffixes for things like object file and libraries.
    This might be a problem if your build description relies on construction variables
    like ``$OBJPREFIX``.
 
Installation
############

With the provided SConstruct, you can install the Tool to your local
SCons configuration folder by calling::

    scons install

Usage
#####

You activate the Tool by adding it to the ``tools=`` list as follows::

    env = Environment(tools=['default','fastcpp'])

. The default set of tracked C/CPP suffixes is::

    '.c', '.cpp', '.h'

and they can be changed by setting the variable ``FAST_CPPSUFFIXES``::

    env = Environment(FAST_CPPSUFFIXES=['.hpp', '.C'],
                      tools=['default','fastcpp'])

