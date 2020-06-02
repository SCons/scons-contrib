Introduction
============

This repository holds a package that is a SCons tool for working with Erlang code.

This tool provides the ``Erlang`` and ``EDoc`` builders:

 *  ``Erlang`` is used to compile Erlang source to create the *beam* files.
 *  ``EDoc`` is used to create the documentation generated from the source code. 

For example::

    environment = Environment ( tools = [ 'erlang' ] )
    environment.Erlang ( 'example.erl' ) 


Installation
============

There are many ways of installing this depending on the use case.  Rather than explain here (and replicate
in every tool README), the material is on the `ToolsIndex <http://www.scons.org/wiki/ToolsIndex>`_ page of
the `SCons <http://www.scons.org>`_ website.


Provenance
==========

The original material for this tool was obtained from http://pupeno.com/projects/scons-erlang -- but this
page appears to be no longer available. The material has subsequently moved to a Git repostory at
http://github.com/pupeno/scons_erlang.  This though has not been updated since 2007-01-28 and the README
indicates that development is via a Darcs repsoitory at http://software.pupeno.com/SConsErlang, but that
repository seems not to exist as reported.


Licence
=======

The original material was licenced under GPLv2.  This fork is licenced under GPLv3 as is permitted by the
GPL rules.

