Introduction
============

This is a package that is a SCons tool for processing Python documentation Sphinx.

Inspiration from Glenn Hutchings' template SConstruct.

Installation
============

Currently this tool is at a very early stage so there is no release.  In order to use this you will have to
take a clone of the Git repository.  There are many ways of organizing things, probably the easiest is
to create the directory:

  $HOME/.scons/site_scons/site_tools

(this works for Posix compliant systems, for Windows replace with the path that works.)

Change directory to this directory and then:

  hg clone http://bitbucket.org/russel/scons_sphinx sphinx

The *sphinx* tool will then be avilable for all your SCons projects.

Usage
=====

Currently only the HTML builder exists.  For example::

    environment = Environment ( tools = [ 'sphinx' ] )
    environment.HTML ( )

this assumes all the reStructured Text files are in the directory ``source`` and that all the HTML files
should be created in ``build``.  To change these set the ``source`` and ``target`` keyword parameters to the
``HTML`` builder.  So for example::

    environment = Environment ( tools = [ 'sphinx' ] )
    environment.HTML ( source = 'rst' , target = 'docs' )
