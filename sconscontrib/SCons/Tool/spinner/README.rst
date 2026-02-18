Spinner: compact build output for SCons
========================================

The **spinner** tool replaces SCons' default verbose build output (which
prints the full shell command for every build step) with compact,
single-line status messages that overwrite each other in place.

Instead of::

    gcc -o build/src/drivers/uart.o -c -I/path/to/include -Wall -Werror -O2 src/drivers/uart.c

you see::

    Compiling src/drivers/uart.c

which is overwritten in-place as each build step completes. The effect
is a quiet, focused build display similar to CMake's or Ninja's default
output.

When stdout is not a TTY (such as in CI environments or when piped to a
file), the tool falls back to printing one line per build step without
ANSI escape sequences.

Installation
------------

Install the ``scons-contrib`` package::

    pip install git+https://github.com/SCons/scons-contrib.git

Or manually copy the ``spinner`` directory into your project's
``site_scons/site_tools/`` directory.

Usage
-----

Activate the tool when creating your construction environment::

    env = Environment(tools=['default', 'spinner'])

That's it. All standard builders (C/C++, Fortran, Lex, Yacc, Java,
linker, archiver, and install) will display spinner output.

Verbose mode
~~~~~~~~~~~~

SCons does not have a built-in ``--verbose`` option, and SCons tools
cannot define command-line options (only ``SConstruct`` files can).
To let users disable the spinner and see full build commands, define
your own option in your ``SConstruct`` and pass it to the spinner
via ``SPINNER_DISABLE``::

    AddOption('--verbose',
              dest='verbose',
              action='store_true',
              default=False,
              help='Show full build commands')

    env = Environment(
        tools=['default', 'spinner'],
        SPINNER_DISABLE=GetOption('verbose'),
    )

When ``SPINNER_DISABLE`` is truthy, the spinner leaves
``PRINT_CMD_LINE_FUNC`` and all ``*COMSTR`` variables at their
defaults, so SCons prints the full shell commands as usual.
``SpinnerAction`` is still available but returns a plain ``Action``
without the spinner display override, so custom builders also
fall back to showing raw commands.

If your project already has a verbosity flag under a different name,
simply wire it to ``SPINNER_DISABLE`` the same way::

    env = Environment(
        tools=['default', 'spinner'],
        SPINNER_DISABLE=my_build_options.verbose,
    )

Multi-platform prefix
~~~~~~~~~~~~~~~~~~~~~

If you are building for multiple platforms and want to distinguish
them in the output, set ``SPINNER_PREFIX``::

    arm_env = env.Clone()
    arm_env['SPINNER_PREFIX'] = 'arm'
    x86_env = env.Clone()
    x86_env['SPINNER_PREFIX'] = 'x86'

This produces output like::

    [arm] Compiling src/drivers/uart.c

Custom builders
~~~~~~~~~~~~~~~

To add spinner output to custom builders or commands, use
``SpinnerAction`` to create an ``Action`` with the spinner display
string wired in.

With a ``Builder``::

    env.Append(BUILDERS = {
        "HexFile": Builder(
            src_suffix = ".elf",
            suffix = ".hex",
            action = env.SpinnerAction(
                "objcopy $SOURCE -O ihex $TARGET",
                'Creating hex',
                use_source=False,
            ),
        ),
    })

With ``env.Command``::

    env.Command(
        target = 'output.ch',
        source = 'input.txt',
        action = env.SpinnerAction(
            'my_converter.py $SOURCE > $TARGET',
            'Generating',
            use_source=False,
        ),
    )

The ``use_source`` parameter controls whether the source filename or
the target filename is displayed. Use ``True`` (the default) for
compile-like builders and ``False`` for link/archive builders that
produce one target from many sources.

Environment variable overrides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``PRETEND_ISATTY``
    Set to a truthy value (e.g. ``1``, ``true``, ``yes``) in the OS
    environment to force ANSI spinner output even when stdout is not
    a TTY. Useful for testing. Values of ``0``, ``false``, ``no``,
    and empty/unset are treated as false.

Construction variables
----------------------

``SPINNER_DISABLE``
    If set to a truthy value, the spinner is not installed and SCons'
    default verbose output is preserved. ``SpinnerAction`` remains
    available but returns plain ``Action`` objects without spinner
    display overrides.

``SPINNER_PREFIX``
    Optional string displayed in brackets before each action name.
    Set per-environment to distinguish builds for different platforms.

``PRINT_CMD_LINE_FUNC``
    Set by ``generate()`` to the spinner print function. This is a
    standard SCons construction variable.

Examples
--------

Minimal usage
~~~~~~~~~~~~~

::

    # SConstruct
    env = Environment(tools=['default', 'spinner'])
    env.Program('hello', 'hello.c')

Output::

    Compiling hello.c
    Linking hello

With verbose flag and multi-platform builds
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

    # SConstruct
    AddOption('--verbose',
              dest='verbose',
              action='store_true',
              default=False,
              help='Show full build commands')

    env = Environment(
        tools=['default', 'spinner'],
        SPINNER_DISABLE=GetOption('verbose'),
    )

    # Build for two platforms
    arm_env = env.Clone()
    arm_env['SPINNER_PREFIX'] = 'arm'
    arm_env.Object('build/arm/main.o', 'src/main.c')

    x86_env = env.Clone()
    x86_env['SPINNER_PREFIX'] = 'x86'
    x86_env.Object('build/x86/main.o', 'src/main.c')

Output with ``scons``::

    [arm] Compiling src/main.c
    [x86] Compiling src/main.c

Output with ``scons --verbose``::

    arm-gcc -o build/arm/main.o -c -Iinclude src/main.c
    gcc -o build/x86/main.o -c -Iinclude src/main.c

With custom builders
~~~~~~~~~~~~~~~~~~~~

::

    # SConstruct
    env = Environment(tools=['default', 'spinner'])

    env.Append(BUILDERS = {
        "HexFile": Builder(
            src_suffix = ".elf",
            suffix = ".hex",
            action = env.SpinnerAction(
                "objcopy $SOURCE -O ihex $TARGET",
                'Creating hex',
                use_source=False,
            ),
        ),
    })

    env.HexFile('firmware.hex', 'firmware.elf')

Output::

    Creating hex firmware.hex

How it works
------------

For standard builders, the tool sets each builder's ``*COMSTR``
variable to an internal marker string containing the human-readable
action name. For custom builders, ``SpinnerAction`` embeds the same
marker as the ``Action``'s display string. In both cases, the tool
sets ``PRINT_CMD_LINE_FUNC`` to a custom print function that
recognizes the markers, extracts the action name and the relevant
filename, makes the path relative to the project root (the directory
containing the top-level ``SConstruct``), truncates long paths to
fit the terminal width, and writes the result using ANSI escape
sequences to overwrite the previous line.

Non-marked strings (such as output from builders that were not
configured with the spinner) are printed normally.

License
-------

MIT License. Copyright 2019-2025 Jeremy Elson.
