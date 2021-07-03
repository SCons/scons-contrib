# Copyright 2016-2021 Keith F Prussing
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# 1.  Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
# 2.  Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
__doc__ = """SCons.Tool.pandoc

The Tool specific initialization for the Pandoc document conversion
command line tool.

There normally shouldn't be any need to import this module directly.  It
will usually be imported through the generic SCons.Tool.Tool() selection
method.

"""

import SCons.Action
import SCons.Builder
import SCons.Scanner
import SCons.Util
try:
    from SCons.Warnings import SConsWarning as SConsWarning
except ImportError:
    from SCons.Warnings import Warning as SConsWarning

import argparse
import logging
import os
import re
import shlex
import subprocess
import sys

try:
    import importlib.metadata as metadata
except ImportError:
    # Work around the fact that mypy has a bug
    #
    # -   https://github.com/python/mypy/issues/1153
    import importlib_metadata as metadata  # type: ignore

if sys.version_info < (3, 6):
    raise RuntimeError(
        "Panflute (and thus this Tool) does not support Python < 3.6"
    )

__version__ = "1.2.0"

# Acknowledgements
# ----------------
#
# The format of this Tool is highly influenced by the JAL Tool on the
# ToolsForFools_ page from the SCons Wiki.
#
# .. ToolsForFools: https://bitbucket.org/scons/scons/wiki/ToolsForFools
#

_debug = False
if _debug:
    _logger = logging.getLogger(__name__)
    _logger.setLevel(logging.DEBUG)
    _handler = logging.StreamHandler()
    _handler.setLevel(logging.DEBUG)
    _formatter = logging.Formatter("%(name)s:%(levelname)s:%(message)s")
    _handler.setFormatter(_formatter)
    _logger.addHandler(_handler)
else:
    logging.getLogger(__name__).addHandler(logging.NullHandler())


class ToolPandocWarning(SConsWarning):
    pass


class PandocNotFound(ToolPandocWarning):
    pass


class PanfluteNotFound(ToolPandocWarning):
    pass


class PandocVersionMissing(ToolPandocWarning):
    pass


class PandocBadVersion(ToolPandocWarning):
    pass


class PanfluteBadVersion(ToolPandocWarning):
    pass


class PanflutePandocVersionSkew(ToolPandocWarning):
    pass


SCons.Warnings.enableWarningClass(ToolPandocWarning)


def _find_filter(filt, datadir, env):
    """Utility function to determine the Pandoc filter command

    To process the final filter, we need to locate it and determine if
    we need to pass it through an interpreter.  According to the User's
    Guide, the search order is: full or relative path to the filter, in
    the $DATADIR/filters directory, and finally in the $PATH.  If the
    datadir provided is None, we check the ``pandoc --version`` output
    for the default.  The ``env`` is the SCons construction Environment.

    Returns
    -------

    command: list
        The command to execute the filter without the format

    """
    if not datadir:
        output = subprocess.check_output([env["PANDOC"], "--version"],
                                         universal_newlines=True)
        for line in output.split("\n"):
            pattern = r"\s*Default user data directory:\s*(.*)"
            match = re.match(pattern, line)
            if match:
                datadir = match.group(1)
                break

    if os.path.exists(filt):
        cmd = [filt]
    elif datadir and os.path.exists(os.path.join(datadir, filt)):
        cmd = [os.path.join(datadir, "filters", filt)]
    else:
        # The filter must be executable and on the PATH.  Therefore, we
        # can just let it error in the usual wan if it is not on the
        # PATH.
        return [filt]

    # Now to check if the filter is executable or needs an interpreter.
    if os.access(cmd[0], os.X_OK):
        return cmd

    # We define the interpreters the same way Pandoc does based on the
    # file extension.  Translated from Pandoc.Filter.JSON
    interpreter = {
            ".py": ["python"],
            ".hs": ["runhaskell"],
            ".pl": ["perl"],
            ".rb": ["ruby"],
            ".php": ["php"],
            ".js": ["node"],
            ".r": ["Rscript"],
        }
    _, ext = os.path.splitext(filt)
    return interpreter.get(ext, []) + cmd


def _detect(env):
    """Try to find Pandoc and :package:`panflute`
    """
    try:
        return env["PANDOC"]
    except KeyError:
        pass

    pandoc = env.WhereIs("pandoc")
    if pandoc:
        return pandoc

    raise SCons.Errors.StopError(
            PandocNotFound, "Could not find Pandoc"
        )


def _scanner(node, env, path, arg=None):
    """ Attempt to scan the final target for images and bibliographies

    In Pandoc flavored MarkDown, the only "included" files are the
    images and the bibliographies.  We need to tell SCons about these,
    but we don't want to do this by hand.  To do this, we directly use
    Pandoc's json output and analyze the document tree for the images
    and the metadata for bibliographies.  We need to operate on the
    filtered syntax tree so we can get the final filtered version.  The
    logic should work on any input format Pandoc can translate into its
    AST.

    Note you must respect Pandoc's bibliography file rules.  The command
    line arguments will override files specified in the YAML block of
    the header file.

    This logic is primarily aimed at the MarkDown sources, but it should
    work with the other plain text sources too.  However, this is not
    rigorously tested.  For LaTeX sources, you should really just use
    the SCons builder to have the right thing done.

    """
    import panflute
    logger = logging.getLogger(__name__ + ".scanner")
    # Grab the base command SCons will run and remove the output flag.
    # This does assume the user did not override the command variable
    # and hard code the output.
    cmd = shlex.split(env.subst_target_source("$PANDOCCOM"))
    for flag in ("-o", "--output"):
        try:
            cmd.remove(flag)
        except ValueError:
            # They specified the other flag
            pass

    # If the user provided the --from flag, we need to move it to the
    # beginning of the command
    newidx = 1
    for idx, item in enumerate(cmd):
        match = re.match(r"(-f|--from=?)([-+\w]*)?", item)
        if match:
            cmd[newidx:newidx] = [cmd.pop(idx)]
            newidx += 1
            if not match.group(2):
                cmd[newidx:newidx] = [cmd.pop(idx+1)]
                newidx += 1

    logger.debug("initial command: '{0}'".format(" ".join(cmd)))
    # Now parse the command line for the known arguments with files that
    # are needed generate the final document.  But, we want to make sure
    # the file is actually in the build tree and not simply an installed
    # executable or file.  To do this, we map destinations in an
    # :class:`argparser.ArgumentParser` to Pandoc flags.  We do not want
    # to deal with searching all over creation so we do not deal with
    # the data directory.
    #
    # .. note:: This does not deal with the --resource-path flag which
    #           provides additional search paths for Pandoc.
    arguments = {
            "filter": ("-F", "--filter"),
            "lua": ("--lua-filter",),
            "metadata": ("--metadata-file",),
            "abbreviations": ("--abbreviations",),
            "highlight": ("--highlight-style",),
            "syntax": ("--syntax-definition",),
            "header": ("-H", "--include-in-header"),
            "before": ("-B", "--include-before-body"),
            "after": ("-A", "--include-after-body"),
            "css": ("-c", "--css"),
            "reference": ("--reference-doc",),
            "epubcover": ("--epub-cover-image",),
            "epubmeta": ("--epub-metadata",),
            "epubfont": ("--epub-embed-font",),
            "bibliography": ("--bibliography",),
            "csl": ("--csl",),
            "citeabbrev": ("--citation-abbreviations",),
        }
    parser = argparse.ArgumentParser()
    for dest in arguments:
        parser.add_argument(*arguments[dest], dest=dest,
                            action="append", default=[])

    # Add the target format in case it was specified as this overrides
    # the output format.  We also need the data directory for finding
    # installed filters.
    parser.add_argument("-t", "--to")
    parser.add_argument("--data-dir", dest="datadir")
    parser.add_argument("--template", default="default")

    args, _ = parser.parse_known_args(cmd)
    files = []
    for dest in arguments:
        files.extend([env.File(x) for x in getattr(args, dest)
                      if os.path.exists(x)])

    # Now we need to determine the files inside the document that will
    # influence the output.  To do this, we need to analyze the tree
    # Pandoc will write out after all of the filters have been run.  The
    # best parser for a Pandoc document is Pandoc itself; however, we
    # want to interrupt the processing before the Writer is called.
    # Looking at the filter documentation, we can achieve this by
    # calling Pandoc with the appropriate flags and piping the JSON
    # output through each filter.  The output format is passed as an
    # argument to each filter so we must replicate that behavior to
    # ensure the syntax tree has the final files.
    #
    # If the user provided the ``--to`` flag (with possible extensions),
    # that _is_ the output format.  Otherwise, we take the format from
    # the file extension.  The only exception is the 'beamer' output.
    if args.to:
        if args.to == "beamer":
            format = "latex"
        else:
            format = re.match(r"(\w+)[-+]?", args.to).group(1)

    else:
        _, format = os.path.splitext(str(node))
        format = format[1:]

    # Now that we have the format, we can figure out if the template was
    # defined and inside the project.  First, we need the root of the
    # build and the template.
    template = args.template
    # Add the extension if needed.
    _, ext = os.path.splitext(template)
    if ext == "":
        template = template + "." + format

    # First, check that the file exists or is findable in the data
    # directory.
    if not os.path.exists(template):
        if args.datadir:
            template = os.path.join(args.datadir, "templates", template)

    if os.path.exists(template) and format not in ("docx", "pptx"):
        files.append(env.File(template))

    def run_command(cmd, proc=None):
        """Helper function for running a command
        """
        logger = logging.getLogger(__name__+".scanner.run_command")
        logger.debug("command: '{0}'".format(" ".join(cmd)))
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stdin=proc.stdout if proc else None)
        return proc

    # We need to run each filter in order; however, we also need to
    # run any Lua filters in their proper location.  We can do this
    # by reading from the front of the command until we find a
    # filter.  We consume the command until we find a filter and run
    # each stage.  We start by processing the input files.
    proc = None
    cmd_ = []
    cmd0 = [_detect(env), "--from", "json", "--to", "json"] + (
        ["--data-dir={0}".format(args.datadir)] if args.datadir else []
    )
    sources = [x.path for x in node.sources if os.path.exists(x.path)]
    while cmd and sources:
        # Grab the first item off the list
        item = cmd.pop(0)
        # Is this a 'to' flag?
        match = re.match(r"(-T|--to=?)([-+\w+]+)?", item)
        if match:
            if not match.group(2):
                cmd.pop(0)

            continue

        # Determine if it is a filter
        match = re.match(r"(-F|--filter=?)([-\w/.]+)?", item)
        if match:
            # Grab the filter
            filt = match.group(2) if match.group(2) else cmd.pop(0)
            logger.debug("cmd : '{0}'".format(" ".join(cmd)))
            logger.debug("item: '{0}'".format(item))
            logger.debug("filt: '{0}'".format(filt))
            logger.debug("cmd_: '{0}'".format(" ".join(cmd_)))

            # First, deal with any intervening commands
            if cmd_:
                if proc:
                    proc = run_command(cmd0 + cmd_, proc)
                else:
                    # If this is the first filter, we need to process the
                    # input files.
                    cmd_.extend(["--to", "json"])
                    cmd_.extend(sources)
                    proc = run_command(cmd_)

            # Now figure out the filter.
            cmd_ = _find_filter(filt, args.datadir, env)
            proc = run_command(cmd_ + [format], proc)
            cmd_ = []
        else:
            # Otherwise, put it on the running command.
            cmd_.append(item)

    # Now process any arguments after the last filter
    if cmd_:
        if proc:
            proc = run_command(cmd0 + cmd_, proc)
        else:
            # If we have no filters, process the sources.
            cmd_.extend(["--to", "json"])
            cmd_.extend(sources)
            proc = run_command(cmd_)

    doc = panflute.load(proc.stdout) if proc else None

    def _path(x):
        """A helper for getting the path right"""
        root = os.path.dirname(str(node))
        if os.path.commonprefix([root, x]) == root:
            return env.File(x)
        else:
            return env.File(os.path.join(root, x))

    # For images, we only concern ourselves with outputs that are a
    # final stage.  This includes formats such as 'docx', 'pptx',
    # 'html', and 'epub'.  It excludes 'markdown' and 'latex'.  The
    # rationale is these are not delivery formats and, therefore, still
    # need to be processed as another stage in SCons.  That is when the
    # scanning needs to be done.  We also exclude PDF because SCons has
    # a better scanner built in. (And why would you want to use SCons if
    # you just want to use Pandoc to go straight to PDF?)
    skip = (
            "asciidoc",
            "commonmark",
            "context",
            "gfm",
            "json",
            "latex",
            "markdown",
            "markdown_mmd",
            "markdown_phpextra",
            "markdown_strict",
            "native",
            "org",
            "plain",
            "rst",
            "tex",
        )
    if format not in skip:
        def walk(src):
            """Walk the tree and find images and bibliographies
            """
            if isinstance(src, panflute.Image):
                return [src.url]
            else:
                tmp = [walk(y) for y in getattr(src, "content", [])]
                return [y for z in tmp for y in z if y]

        images = [x for x in walk(doc) if x]
        logger.debug("images: {0}".format(images))
        files.extend([_path(x) for x in images])

    # And, finally, check the metadata for a bibliography file
    if doc:
        if not args.bibliography:
            bibs = doc.metadata.content.get("bibliography", [])
            if bibs:
                files.extend([_path(x.text) for x
                              in getattr(bibs, "content", [bibs])])

    logger.debug("{0!s}: {1!s}".format(node, [str(x) for x in files]))
    return files


_builder = SCons.Builder.Builder(
        action=SCons.Action.Action("$PANDOCCOM", "$PANDOCCOMSTR"),
        target_scanner=SCons.Scanner.Scanner(_scanner),
    )


def generate(env):
    """Add the Builders and construction variables to the Environment
    """
    env["PANDOC"] = _detect(env)
    command = "$PANDOC $PANDOCFLAGS -o ${TARGET} ${SOURCES}"
    env.SetDefault(
            # Command line flags.
            PANDOCFLAGS=SCons.Util.CLVar("--standalone"),

            # Commands.
            PANDOCCOM=command,
            PANDOCCOMSTR="",

        )
    env["BUILDERS"]["Pandoc"] = _builder
    return


def exists(env):
    pandoc = _detect(env)
    proc = subprocess.run([pandoc, "--version"], capture_output=True,
                          text=True)
    match = re.match(r"pandoc\s+(\d+[.]\d+)", proc.stdout, re.IGNORECASE)
    if not match:
        raise SCons.Errors.StopError(
            PandocVersionMissing,
            f"Could not determine Pandoc version from: '{proc.stdout}'"
        )

    pandoc_version_ = match.group(1)
    if pandoc_version_ == "2.10":
        raise SCons.Errors.StopError(
            PandocBadVersion, "Pandoc 2.10 is not supported"
        )

    try:
        pandoc_version = tuple(
            int(_) for _ in pandoc_version_.split(".")
            if re.match(r"^(\d)+$", _)
        )
    except ValueError:
        raise SCons.Errors.StopError(
            PandocBadVersion,
            f"Could not parse Pandoc version {pandoc_version_}"
        )

    try:
        panflute_version_ = metadata.version("panflute")
    except metadata.PackageNotFoundError:
        raise SCons.Errors.StopError(
                PanfluteNotFound, "Could not find panflute"
            )

    try:
        panflute_version = tuple(
            int(_) for _ in panflute_version_.split(".")
            if re.match(r"^\d+$", _)
        )
    except ValueError:
        raise SCons.Errors.StopError(
            PanfluteBadVersion,
            f"Could not parse panflute version {panflute_version_}"
        )

    if any(pandoc_version < (2, 10) and panflute_version >= (2,),
           pandoc_version > (2, 10) and panflute_version < (2,)):
        raise SCons.Errors.StopError(
                PanflutePandocVersionSkew,
                f"Incompatible Pandoc (version {pandoc_version_}) and "
                f"Panflute (version {panflute_version_}) found"
            )

    return pandoc
