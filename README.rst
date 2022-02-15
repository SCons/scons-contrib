SCons - a Software Construction Tool - Contributed Software
###########################################################


Introduction
============

This repository contains contributed software to use with
`SCons <https://scons.org>`_.
These contributions enable the use of additional tools, builders,
and other components that are not part of mainline SCons.
Many of these were previously (or still are) on the wiki,
but it's harder to extract code snippets from wiki pages,
and the wiki pages arn't always maintained (e.g. support for
Python 3) so some of the popular ones are collected here
for convenience.

The tools in this repository are intended to be used with
Python 3. If necessary, they have been converted with 2to3,
and reformatted with Black.  The original versions of the
tools are available in the ``python27`` branch if you need
versions that worked wtih Python 2.


Contributing
============

Contribute new tools by making a Pull Request on this repository.
Please create a new directory per contribution.
(We may re-organize this it becomes obvious that doing so would
make it easier for users to find useful logic.)
Please include a README file (README.rst or other form)
describing any information about your tool, *including the
license it is released under*. If at all possible, please
use the MIT license that as SCons itself is released under,
for maximum license compatibility, but that is not mandatory
as long as the actual license is clearly indicated.


License and Support
===================

Tools in this repository are available under their listed licence
(see the respective README files).
If no license is called out specifically, the tool is available
under the same MIT license SCons is released under.
If the license is not MIT, make sure you are okay to include
the tool in your project under its terms.

These are not "supported" directly by the SCons project.
For problems/discussion, please file issues and raise PRs against
`this project <https://github.com/SCons/scons-contrib>`_.
Several of the original authors are not hanging around here,
so you may need to be a little patient or propose fixes yourself.


Installation
============

The tools are organized as a collection of individual directories
under ``sconscontrib/SCons/Tool``.  When you activate a tool in
SCons, it pulls it in via Python's import system. This broadly
means any tool you want to use needs to be findable by Python,
in ``sys.path``, which when running SCons includes several
special directories.  For more information on this, see the
SCons Manual page under
`Tools <https://scons.org/doc/production/HTML/scons-man.html#tools>`_
and `site-dir <https://scons.org/doc/production/HTML/scons-man.html#opt-site-dir>`_

You can manually place tools in a findable place, or you can use
``pip`` to install to the same place that version of Python
puts SCons itself.


Installing via pip
------------------

To install using a ``setuptools`` backed method (``pip`` or
``setup.py``), you must be using SCons 4.0 or newer.
If you are using an older version of SCons,
see the `Manual Installation`_ instructions.

For installing via ``pip``, you need to point directly to
the code repostory, as this collection is not available on
the `Python Package Index <https://pypi.org>`_::

    python -m pip install --user git+https://github.com/SCons/scons-contrib.git

This puts all of the tools into the ```Tool``` subdirectory of
the SCons installation, in other words, in the same place
SCons looks for its own built-in tools.  Usually you don't have
permission to write here, so the ``--user`` option is used
to put them into a parallel writable location specific to your account.

The SCons project generally recommends that you use a Python
virtualenv to set up SCons, because you can keep the dependencies
isolated from others. Since many of the contributed tools
use other facilities (for example the Sphinx tools require
Sphinx itself, which requires quite a few other Python packages)
this avoids installing a lot of dependnecies
into your system install of Python
(even if they went into the user location).
Inside an activated virtualenv you can use the somewhat simpler::

    pip install git+https://github.com/SCons/scons-contrib.git

There's an alternate installation style you can perform as well -
clone the scons-contrib repository yourself and then run
setup manually::

    git clone https://github.com/SCons/scons-contrib.git
    cd scons-contrib
    python setup.py install

The Python packaging experts no longer recommend any project
call ``setup.py`` manually, and since the ``pip install``
command pointing to the remote code repository does basically
the same thing behind the covers but more cleanly/safely,
this alternate install is no longer recommended, unless
there's a reason ``pip`` cannot be used to point to a code
repository (company security policy, perhaps?)


Manual Installation
-------------------

`Installing via pip`_ results in all of the contrib tools being
installed at once. If you just want a specific tool or two,
a manual installation may be a better choice.

To do this, clone the repository::

    git clone https://github.com/SCons/scons-contrib.git

and copy the required tool directory into one of the locations
SCons searches for tools. Often the preferred choice is to copy
it to the project's ``site_scons/site_tools``.

Manual Installation Options
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Roughly speaking, there are three (operating system-specific)
locations that are searched by default:
a system-wide location, a user-account location, and a location
insde a specific project (which is the path listed above).
These default locations are listed by operating system in the
`SCons Manual Page <https://scons.org/doc/production/HTML/scons-man.html#opt-site-dir>`_.

In addition to the defaults as places to search,
the project-level site directory can be changed by
supplying the ``--site-dir`` option,
and SCons can also be given additional locations to look for
tools using the ``toolpath`` parameter when creating a
Construction Environment.

The choice of which one of these to use depends on the intended
scope - whether the tool is to be used for many projects
or just for one, etc.


Activating The Tool
-------------------

Once a tool is used, it needs to be activated for actual use.
SCons searches for various default tools, and activates them
if found, but must be asked to look at others, whether built-in
or added later. In most cases this is done by giving a list of
desired tools for a given construction environment when it is created::

    env = Environment(tools=['default', 'mytool'])


Requirements
============

The SCons contrib package requires you to have **scons** installed.
If any individual tool package has dependencies, they will
also be pulled in during an installation using ``pip``.
For manual installation, you will need to satisfy any
Python package requirements manually.

TODOs and known problems
========================

* Implement more commands/builders/tools.
* Set up "subpackage" type installs, so that ``pip install``
  of an individual tool is possible.
