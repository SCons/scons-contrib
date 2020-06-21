#####################
The SCons kotlin tool
#####################

Basics
======

This Tool adds basic support for compiling `kotlin` sources.
The following Builders are currently provided:

**Kotlin**
    Creates a `*.class` file from the given Kotlin source.
**NoweaveHtml**
    Converts the *noweb* input to a HTML document.
**Notangle**
    Extracts the code chunk with the given target name from the
    *noweb* input.


Example SConstruct
==================

::

    env = Environment(tools=['default','kotlin'])
    env.Kotlin('HelloWorldKt.class', 'HelloWorld.kt')


Install
=======

Installing the Tool requires you to copy the contents of the ``kotlin`` folder to

#. "``/path_to_your_project/site_scons/site_tools/kotlin``", if you need the Tool in one project only, or
#. "``~/.scons/site_scons/site_tools/kotlin``", for a system-wide installation under your current login.

For the latter option there is also a simple SConstruct provided, and you can call::

    scons install

to make the Tool available in your system.

