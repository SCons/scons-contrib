The SCons Protoc tool
=====================

Scons tool for compiling Google’s Protobuf

Basics
------

Put the ``protoc.py`` file in ``#site_scons/site_tools/`` then in your
SConstruct file do something like:

.. code:: python

   env = Environment(
       tools=["default", "protoc"],
       ...
   )

   env.Replace(PROTOC_CCOUT="/path/to/desired/cpp/output")

   protoc_out = env.Protoc(["src/Example.proto"])

To enable the generation of a language output files you have to supply
its output directory (``PROTOC_CCOUT``, ``PROTOC_PYOUT``,
``PROTOC_JAVAOUT``). If you need also to generate the GRPC files, you
have to supply the plug-ins paths (``PROTOC_GRPC_CC``,
``PROTOC_GRPC_PY``, ``PROTOC_GRPC_JAVA``)

During the setup of the environment, the protoc compiler will be
detected from the environment or from the ``PROTOC`` variable.

You can supply some or all of these variables using keyword arguments
during the creation of the construction environment:

.. code:: python

   env = Environment(
     tools=['default', 'protoc'],
     PROTOC='path/to/protoc',
     PROTOC_GRPC_CC = 'path/to/protoc/grpc_cc_plugin',
     PROTOC_GRPC_PY = 'path/to/protoc/grpc_py_plugin',
     PROTOC_GRPC_JAVA = 'path/to/protoc/grpc_java_plugin',
     ...
   )

or equivalently, using the tool-as-a-tuple form during creation:

.. code:: python

   env = Environment(
       tools=[
           "default",
           (
               "protoc",
               {
                   PROTOC: "path/to/protoc",
                   PROTOC_GRPC_CC: "path/to/protoc/grpc_cc_plugin",
                   PROTOC_GRPC_PY: "path/to/protoc/grpc_py_plugin",
                   PROTOC_GRPC_JAVA: "path/to/protoc/grpc_java_plugin",
               },
           ),
       ]
       ...
   )

or using ``Replace`` after the environment is created:

.. code:: python

   env.Replace(
       PROTOC="path/to/protoc",
       PROTOC_GRPC_CC="path/to/protoc/grpc_cc_plugin",
       PROTOC_GRPC_PY="path/to/protoc/grpc_py_plugin",
       PROTOC_GRPC_JAVA="path/to/protoc/grpc_java_plugin",
   )

Your call to the ``Protoc`` builder can still override the variables
controlling the build in the call itself:

.. code:: python

   protoc_out = env.Protoc(
       ["src/Example.proto"],
       PROTOC_CCOUT="/path/to/desired/cpp/output",
       PROTOC_PYOUT="/path/to/desired/python/output",
       PROTOC_JAVAOUT="/path/to/desired/java/output",
   )

The path that the ``proto`` file exists in will be added automatically
to the list of ``proto`` paths. You can add more paths by using the
``PROTOC_PATH`` variable.

You can also prepend flags to the ``protoc`` command using the
``PROTOC_FLAGS`` variable.

There are also a set of variables for the different output suffixes and
usually you don’t have to touch any of them.
