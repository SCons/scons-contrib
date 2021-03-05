.. note:: Installs using pip or setup.py are not presently implemented.
   Suggest manually add a tool to ``site_scons/site_tools`` to use.

SCons - a software construction tool - Contributed Software
###########################################################


Introduction
============

This repository contains contributed software to use with 
`SCons <https://scons.org>`_.
These contributions enable the use of additional tools, builders,
and other components that are not part of mainsline SCons.
Many of these were previously (or still) on the wiki,
but it's harder to extract text from wiki pages, 
so some of those are collected here.

The tools in this repository are intended to be used with
Python 3. If necessary, they have been converted with 2to3,
and reformatted with Black.  The original versions of the
tools are available in the ``python27`` branch if you need
versions that worked wtih Python 2.


Contributing
============

Contribute new tools by making a Pull Request on this repository.
Please create a directory per contribution.
(We may re-organize if it becomes obvious that doing so would 
make it easier for users to find useful logic.)
Please include a README file (README.rst or other form)
describing any information about your tool, including the
license it is released under.


License and Support
===================

Tools in this repository are available under their listed licence.
If no license is called out specifically, the tool is available
under the MIT License, the same one SCons is released under.
If the license is not MIT, make sure you are okay to include
the tool in your project under its terms.

These are not supported directly by the SCons project,
for problems/discussion, please file issues and raise PRs against 
`this project <https://github.com/SCons/scons-contrib>`_.
Several of the original authors are not hanging around here,
so you may need to be a little patient or propose fixes yourself.


Installing
==========

For installing via ``pip``, you have to say

::

    pip install sconscontrib

Your other option is to clone the repository 
``https://github.com/SCons/scons-contrib.git``,
change into its top-level folder,
get root and then run the command

::

    python setup.py install

Manual Installation
===================

You can also copy an individual tool's directory into
your project's ``site_scons/site_tools`` to make it available.

Requirements
============

The SCons contrib package requires you to have **scons** installed.

TODOs and known problems
========================

* Implement more commands/builders/tools.
