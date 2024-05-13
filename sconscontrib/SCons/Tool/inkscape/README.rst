SCons tool for using Inkscape to convert images
===============================================

A common occurrence when writing is needing to convert an image format
to include in your document.  You will spend valuable (and important)
time adjusting your plot with ``pgfplots`` for LaTeX only to discover
that the journal expects a Word document.  Alternatively, you realize
that you want to use an particular vector graphic from a journal article
you submitted in a conference presentation requiring PowerPoint.  One
way to handle these situations is to simply regenerate the image in an
appropriate format.  However, that is a very manual and time consuming
process and does not sound like fun.  If your image is a high quality
SVG hand crafted in a drawing tool, you could easily reduce the quality
of the image by exporting the wrong format or lose your high quality
professional fonts.

You, on the other hand, are enlightened enough to use a `build tool`_ to
automate away most of this tediousness (otherwise you would not be
here).  This is a :class:`SCons.Tool` for teaching SCons_ how to use
Inkscape_ to convert vector images between formats.  The native format
of Inkscape is SVG, but it is also able to easily export PDF, PDF plus
the boiler plate LaTeX for directly including in a LaTeX document, or
even an PNG for inclusion into Word or PowerPoint document.  (The
inclusion of the last two formats is to facilitate working with Pandoc_
and the `associated tool`_)

.. _SCons: https://scons.org
.. _build tool: SCons_
.. _Inkscape: https://inkscape.org
.. _Pandoc: https://pandoc.org
.. _associated tool: https://github.com/SCons/scons-contrib/tree/master/sconscontrib/SCons/Tool/pandoc

Installation
------------

The tool follows the convention described in the ToolsIndex_.  Simply
clone this repository into your ``site_scons/site_tools`` directory
under the name ``inkscape``.  Then add::

   env = Environment(tools=["inkscape"])

to your ``SConstruct`` and you are ready to go.  Alternatively, you
could just copy the ``__init__.py`` to your tools directory, but why
would you want to do that?

.. _ToolsIndex: https://github.com/SCons/scons/wiki/ToolsIndex

Usage
-----

This tool provides the ``Inkscape`` builder.  The simplest usage is

.. code-block:: python

    png = env.Inkscape("img.png", "img.svg")

If you wish to pass additional flags to the Inkscape invocation, you can
set the ``INKSCAPEFLAGS`` variable.  For example, to generate a PDF and
export all text to LaTeX you can use

.. code-block:: python

    pdf = env.Inkscape("img.pdf", "img.svg", INKSCAPEFLAGS="--export-latex")

.. note:: A prior version (0.0.1_) created convenience Builders for
   common conversions.  However, with Inkscape 1.0.0, these became
   reduentant since Inkscape can now handle these details directly.

License
-------

This is Open Source software under the MIT license. For full details,
see the license statement in the ``__init__.py``.

Changelog
---------

All notable changes to this project will be documented in this section.
The format is based on `Keep a Changelog`_.

Unreleased_
^^^^^^^^^^^

Fixed
'''''

-   Corrected LaTeX annotation in docstring

0.1.0_ 2021-08-08
^^^^^^^^^^^^^^^^^

Changed
'''''''

-   Migrated development to ``trunk``
-   Updated to Inkscape 1+ argument syntax
-   Updated to the SCons preferred syntax of the MIT License

Removed
'''''''

-   Extension specific Builders

0.0.1_ 2021-08-07
^^^^^^^^^^^^^^^^^

-   Initial release that “worked” with Inkscape 0.92

.. _Unreleased: https://github.com/kprussing/scons-inkscape/compare/v0.1.0...HEAD
.. _0.1.0: https://github.com/kprussing/scons-inkscape/compare/v0.0.1..v0.1.0
.. _0.0.1: https://github.com/kprussing/scons-inkscape/releases/tag/v0.0.1
.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
