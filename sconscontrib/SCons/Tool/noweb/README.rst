####################
The SCons noweb tool
####################

Basics
======

This Tool adds basic support for the `noweb` literate
programming tool (https://www.cs.tufts.edu/~nr/noweb/) by
Norman Ramsey. The following Builders are currently provided:

**Noweave**
    Converts the *noweb* input to a LaTeX document.
**NoweaveHtml**
    Converts the *noweb* input to a HTML document.
**Notangle**
    Extracts the code chunk with the given target name from the
    *noweb* input.


Example SConstruct
==================

::

    env = Environment(tools=['default','noweb'])
    env.Noweave('dimmer.ltx', 'dimmer.nw')
    env.Notangle('dimmer.asm', 'dimmer.nw')
    env.PDF(source='dimmer.ltx')


Install
=======

Installing the Tool requires you to copy the contents of the ``noweb`` folder to

#. "``/path_to_your_project/site_scons/site_tools/noweb``", if you need the Tool in one project only, or
#. "``~/.scons/site_scons/site_tools/noweb``", for a system-wide installation under your current login.

For the latter option there is also a simple SConstruct provided, and you can call::

    scons install

to make the Tool available in your system.

