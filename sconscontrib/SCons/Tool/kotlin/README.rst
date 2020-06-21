#####################
The SCons kotlin tool
#####################

Basics
======

This Tool adds basic support for compiling *Kotlin* sources.
The following Builders are currently provided:

**Kotlin**
    Creates a `*.class` file from the given Kotlin source.
**KotlinJar**
    Creates a `*.jar` file from the given Kotlin source (can't be run standalone).
**KotlinRuntimeJar**
    Creates a `*.jar` file from the Kotlin source, while including a full runtime. The resulting
    JAR can be directly run with `java -jar <target>.jar`.


SConstruct examples
===================

All the three Builders above are implemented as pseudo-Builders. They are clever enough to
deduce the target name when only a source is given. This even works when also leaving
out the suffix of the source file.

So, creating a class file from a source `hello.kt` can be as simple as::

    env = Environment(tools=['default','kotlin'])
    env.Kotlin('hello')

The Builder will correctly derive the target name `HelloKt.class` from this. Adding a different
target filename to the `Kotlin` Builder has no effect, it will only mix-up your dependencies.

However, for the `KotlinJar` and `KotlinRuntimeJar` Builders it's perfectly legal to
specify::

    env = Environment(tools=['default','kotlin'])
    env.KotlinRuntimeJar('run.jar', 'hello.kt')
   
or::

    env = Environment(tools=['default','kotlin'])
    env.KotlinRuntimeJar('run', 'hello')

TODO
    It's still unclear what to do with the created `META-INF` folder.

Install
=======

Installing the Tool requires you to copy the contents of the ``kotlin`` folder to

#. "``/path_to_your_project/site_scons/site_tools/kotlin``", if you need the Tool in one project only, or
#. "``~/.scons/site_scons/site_tools/kotlin``", for a system-wide installation under your current login.

For the latter option there is also a simple SConstruct provided, and you can call::

    scons install

to make the Tool available in your system.

