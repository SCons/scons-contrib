Pandoc Support for SCons
========================

Introduction
------------

Pandoc_ is a handy command line tool that can convert plain text markup
files into different formats.  It does this by parsing the given input
files, representing them as an abstract syntax tree (AST), optionally
running the AST through one or more filters, and then writing the AST to
the desired output format.  In the process, Pandoc_ uses a collection of
files specified within the input document(s), via ``Image`` markup or in
a YAML metadata block, and command line flags.  Pandoc_ always process
the inputs to outputs even if the inputs have not changed.  For some
output formats, this is not a problem.  However, for others formats
(like PDF) this can cause unnecessary compilation that can potentially
be long.  Further, Pandoc_ does not know how to generate files from
sources unless it is handled with a filter.

A better solution is to use a build tool that understands dependency
scanning and can be extended to generate implicit dependencies.  SCons_
is a tool that fits this description.  If we can tell SCons_ what files
a Pandoc_ document depends on, we can let SCons_ handle what to build
when a document needs to be updated.  This exposes the full machinery of
SCons_ to generate graphics from raw input files to building a Pandoc_
document.  We could explicitly tell SCons_ the dependencies for each
document, but a more powerful method is to scan the AST itself and
provide the implicit dependency list to SCons_.

The goal of this project is to add support for Pandoc_ to SCons_
through the tool plugin system.

.. _SCons: http://www.scons.org
.. _Pandoc: http://www.pandoc.org

Usage
-----

Once installed, to use the tool simply add::

    env = Environment(tools=["pandoc"])

to your ``SConstruct``.  Then, you specify a document via::

   html = env.Pandoc("example.html", ["page1.md", "page2.md", "head.yaml"])

You can use the ``PANDOCFLAGS`` environment variable to add additional
flags to pass to Pandoc_ like filters, bibliography files, or even
metadata flags.  For an example usage, see the files included in the
aptly named directory.

Manual Installation
-------------------

To manually install, copy this directory to ``site_scons/site_tools`` in
you project or place it in the `appropriate location`_ for your system.
For more details, check the `SCons User Guide`_.

To install using pip with SCons version 4 or later, clone the main
repository and run::

    pip install .

.. note:: This will install directly to the SCons file structure which
   violates the "don't install into someone else's namespace" rule, but
   it works until an official namespace is established by SCons.  This
   does mean installing in editable mode (``pip install -e .``) does not
   work.

.. _`appropriate location`: https://github.com/SCons/scons/wiki/ToolsIndex#Install_and_usage
.. _`SCons User Guide`: http://scons.org/doc/production/HTML/scons-user.html

Requirements
------------

This tool requires Pandoc_ (obviously) 2.11 or newer with panflute_ 2.0
or newer *or* Pandoc 2.7 through 2.9 with panflute pre 2.0.

.. note:: Pandoc 2.10 is not supported because it introduced a breaking
   API change that is not supported by panflute.  The versions supported
   by this tool are those `supported by panflute`_.

.. _panflute: https://pypi.org/project/panflute/
.. _`supported by panflute`: https://github.com/sergiocorreia/panflute#supported-pandoc-versions

Licence
-------

This is Open Source software under the MIT license.  For full details,
see the license statement in the ``__init__.py``.

Changelog
---------

All notable changes to this project will be documented in this section.
The format is based on `Keep a Changelog`_.

1.2.0_ 2021-07-03
^^^^^^^^^^^^^^^^^

Changed
'''''''

-   Moved maintenance to scons-contrib_

1.1.0_ 2021-06-30
^^^^^^^^^^^^^^^^^

Fixed
'''''

-   Corrected version restrictions on Pandoc+panflute
-   Installation details requiring SCons 4 or newer for pip

1.0.0_ 2021-06-21
^^^^^^^^^^^^^^^^^

-   Initial stable release

.. _1.2.0: https://github.com/kprussing/scons-pandoc/compare/v1.1.0..v1.2.0
.. _1.1.0: https://github.com/kprussing/scons-pandoc/compare/v1.0.0..v1.1.0
.. _1.0.0: https://github.com/kprussing/scons-pandoc/releases/tag/v1.0.0
.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _scons-contrib: https://github.com/SCons/scons-contrib
