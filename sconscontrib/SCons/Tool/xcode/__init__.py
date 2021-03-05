#
# scons_xcode
#
# (c) Copyright 2016 Alastair Houghton
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import sys
import os
import shutil
import uuid
import re
import binascii

import SCons.Action
import SCons.Builder
import SCons.Util

PBXPROJ_HEADER = """// !$*UTF8*$!
{
  archiveVersion = 1;
  classes = {
  };
  objectVersion = 47;
  objects = {
"""

PBXPROJ_FILEREF = """    %s /* %s */ = {
      isa = PBXFileReference;
      name = %s;
      path = %s;
      sourceTree = "<group>";
    };
"""

PBXPROJ_LEGACYTARGET = """    %s /* %s */ = {
      isa = PBXLegacyTarget;
      buildArgumentsString = %s;
      buildConfigurationList = %s /* %s */;
      buildPhases = (
      );
      buildToolPath = %s;
      dependencies = (
      );
      name = %s;
      passBuildSettingsInEnvironment = 1;
      productName = %s;
    };
"""

PBXPROJ_GROUP = """    %s /* %s */ = {
      isa = PBXGroup;
      children = (
%s
      );
      name = %s;
      sourceTree = %s;
    };
"""

PBXPROJ_TOP_GROUP = """    %s = {
      isa = PBXGroup;
      children = (
%s
      );
      sourceTree = %s;
    };
"""

PBXPROJ_GROUPENTRY = "        %s /* %s */,"

PBXPROJ_BUILDCONF = """    %s /* %s */ = {
      isa = XCBuildConfiguration;
      buildSettings = {
      };
      name = %s;
    };
"""

PBXPROJ_CONFIGLIST = """    %s /* Build configuration list for %s */ = {
      isa = XCConfigurationList;
      buildConfigurations = (
%s
      );
      defaultConfigurationIsVisible = 0;
      defaultConfigurationName = Release;
    };
"""

PBXPROJ_CONFENTRY = "        %s /* %s */,"

PBXPROJ_PROJECT = """    %s /* Project object */ = {
      isa = PBXProject;
      attributes = {
        LastUpgradeCheck = 0730;
        ORGANIZATIONNAME = %s;
        TargetAttributes = {
%s
        };
      };
      buildConfigurationList = %s; /* Build configuration list for project */
      compatibilityVersion = "Xcode 6.3";
      developmentRegion = English;
      hasScannedForEncodings = 0;
      knownRegions = (
        en,
      );
      mainGroup = %s;
      productDirPath = "";
      projectRoot = "";
      targets = (
%s
      );
    };
"""

PBXPROJ_TARGETATTRS = """          %s = {
            CreatedOnToolsVersion = 7.3;
          };"""

PBXPROJ_TARGETENTRY = "        %s,"

PBXPROJ_FOOTER = """
  };
  rootObject = %s /* Project object */;
}
"""

XCSCHEME = """<?xml version="1.0" encoding="UTF-8"?>
<Scheme
   LastUpgradeVersion = "0730"
   version = "1.3">
   <BuildAction
      parallelizeBuildables = "YES"
      buildImplicitDependencies = "YES">
      <BuildActionEntries>
         <BuildActionEntry
            buildForTesting = "YES"
            buildForRunning = "YES"
            buildForProfiling = "YES"
            buildForArchiving = "YES"
            buildForAnalyzing = "YES">
            <BuildableReference
               BuildableIdentifier = "primary"
               BlueprintIdentifier = "%(uuid)s"
               BuildableName = "%(name)s"
               BlueprintName = "%(name)s"
               ReferencedContainer = "container:%(xcodeproj)s">
            </BuildableReference>
         </BuildActionEntry>
      </BuildActionEntries>
   </BuildAction>
   <TestAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      shouldUseLaunchSchemeArgsEnv = "YES">
      <Testables>
      </Testables>
      <AdditionalOptions>
      </AdditionalOptions>
   </TestAction>
   <LaunchAction
      buildConfiguration = "Debug"
      selectedDebuggerIdentifier = "Xcode.DebuggerFoundation.Debugger.LLDB"
      selectedLauncherIdentifier = "Xcode.DebuggerFoundation.Launcher.LLDB"
      launchStyle = "0"
      useCustomWorkingDirectory = "NO"
      ignoresPersistentStateOnLaunch = "NO"
      debugDocumentVersioning = "YES"
      debugServiceExtension = "internal"
      allowLocationSimulation = "YES">
      <PathRunnable
         runnableDebuggingMode = "0"
         FilePath = "%(path)s">
      </PathRunnable>
      <MacroExpansion>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "%(uuid)s"
            BuildableName = "%(name)s"
            BlueprintName = "%(name)s"
            ReferencedContainer = "container:%(xcodeproj)s">
         </BuildableReference>
      </MacroExpansion>
      <AdditionalOptions>
      </AdditionalOptions>
   </LaunchAction>
   <ProfileAction
      buildConfiguration = "Release"
      shouldUseLaunchSchemeArgsEnv = "YES"
      savedToolIdentifier = ""
      useCustomWorkingDirectory = "NO"
      debugDocumentVersioning = "YES">
      <MacroExpansion>
         <BuildableReference
            BuildableIdentifier = "primary"
            BlueprintIdentifier = "%(uuid)s"
            BuildableName = "%(name)s"
            BlueprintName = "%(name)s"
            ReferencedContainer = "container:%(xcodeproj)s">
         </BuildableReference>
      </MacroExpansion>
   </ProfileAction>
   <AnalyzeAction
      buildConfiguration = "Debug">
   </AnalyzeAction>
   <ArchiveAction
      buildConfiguration = "Release"
      revealArchiveInOrganizer = "YES">
   </ArchiveAction>
</Scheme>
"""

_simple_re = re.compile(r"^[A-Za-z_/\.][A-Za-z0-9_/\.]*$")
_escape_re = re.compile(r'(")')


def _escape(s):
    if _simple_re.match(s):
        return s
    return "".join(['"', _escape_re.sub(r"\\\1", s), '"'])


_cend_re = re.compile(r"\*/")


def _escape_comment(s):
    return _cend_re.sub("(*)/", s)


_xml_esc_re = re.compile(r"([<&>])")
_xml_escs = {"<": "&lt;", "&": "&amp;", '"': "&quot;", ">": "&gt;"}


def _escape_xml(s):
    return _xml_esc_re.sub(lambda x: _xml_escs[x], s)


def _generate_uuid():
    return binascii.b2a_hex(os.urandom(12)).upper()


class SectionHandler(object):
    def __init__(self, f, name):
        self.file = f
        self.name = name

    def __enter__(self):
        self.file.write("\n/* Begin %s section */\n" % self.name)

    def __exit__(self, type, value, traceback):
        self.file.write("/* End %s section */\n" % self.name)


def _settings_from_env(target, env):
    settings = {}

    if "name" in env:
        settings["name"] = env["name"]
    else:
        settings["name"] = os.path.basename(SCons.Util.splitext(str(target))[0])

    if "products" not in env or env["products"] == None:
        settings["products"] = []
    elif SCons.Util.is_String(env["products"]):
        settings["products"] = [env["products"]]
    elif SCons.Util.is_List(env["products"]):
        settings["products"] = env["products"]

    if "groups" not in env or env["groups"] == None:
        settings["groups"] = {}
    else:
        settings["groups"] = env["groups"]

    if "variants" not in env or env["variants"] == None:
        settings["variants"] = ["Default"]
    else:
        settings["variants"] = env["variants"]

    try:
        get_abspath = target.get_abspath
    except AttributeError:
        settings["target"] = os.path.abspath(str(target))
    else:
        settings["target"] = get_abspath()

    return settings


class XcodeProjectGenerator(object):
    def __init__(self, target, env):
        self.target = target
        self.target_dir = target.get_dir()
        self.env = env

        settings = _settings_from_env(target, env)

        self.name = settings["name"]
        self.products = settings["products"]
        self.groups = settings["groups"]
        self.variants = settings["variants"]
        self.target_path = settings["target"]

    def relpath(self, node):
        return node.get_path(self.target_dir)

    def build(self):
        print("scons: Building %s" % self.target_path)

        try:
            if os.path.exists(self.target_path):
                shutil.rmtree(self.target_path)
            os.mkdir(self.target_path)
        except OSError as detail:
            print('Unable to create "' + self.target_path + '":', detail, "\n")
            raise

        pbxproj = os.path.join(self.target_path, "project.pbxproj")
        with open(pbxproj, "wb") as self.file:
            self.file.write(PBXPROJ_HEADER)

            self.write_file_references()
            self.write_groups()
            self.write_buildconfs(self.variants)
            self.write_cfglists()
            self.write_targets()
            self.write_project()

            self.file.write(PBXPROJ_FOOTER % self.project_uuid)

        os.makedirs(os.path.join(self.target_path, "xcshareddata", "xcschemes"))
        self.write_schemes()

    def write_schemes(self):
        # For now, we only do this for programs
        xcodeproj = os.path.basename(self.target_path)
        for product in self.products:
            buildername = product.builder.get_name(self.env)
            if buildername == "Program":
                if SCons.Util.is_String(product):
                    prodpath = product
                    abspath = prodpath
                else:
                    prodpath = str(self.relpath(product))
                    abspath = str(product.get_abspath())
                filename = os.path.basename(prodpath)

                scheme = os.path.join(
                    self.target_path,
                    "xcshareddata",
                    "xcschemes",
                    filename + ".xcscheme",
                )
                with open(scheme, "wb") as sf:
                    sf.write(
                        XCSCHEME
                        % {
                            "xcodeproj": _escape_xml(xcodeproj),
                            "name": _escape_xml(filename),
                            "uuid": self.product_targets[prodpath],
                            "path": _escape_xml(abspath),
                        }
                    )

    def write_buildconfs(self, variants):
        with SectionHandler(self.file, "XCBuildConfiguration"):
            self.project_build_confs = self.write_build_configurations(variants)
            self.target_build_confs = self.write_build_configurations(variants)
            self.target_bcs = {}
            for product in self.products:
                if SCons.Util.is_String(product):
                    prodpath = product
                else:
                    prodpath = str(self.relpath(product))
                filename = os.path.basename(prodpath)

                self.target_bcs[prodpath] = self.write_build_configurations(variants)

    def write_cfglists(self):
        with SectionHandler(self.file, "XCConfigurationList"):
            self.config_uuid = self.write_config_list(
                self.project_build_confs, "project"
            )
            self.target_cfg_uuid = self.write_config_list(
                self.target_build_confs, "target"
            )
            self.target_cfgs = {}
            for product in self.products:
                if SCons.Util.is_String(product):
                    prodpath = product
                else:
                    prodpath = str(self.relpath(product))
                filename = os.path.basename(prodpath)

                self.target_cfgs[prodpath] = self.write_config_list(
                    self.target_bcs[prodpath], filename
                )

    def all_group_files(self):
        group_files = set()

        def collect_files(group_files, group):
            for k, v in group.items():
                if v is None:
                    continue
                if not SCons.Util.is_List(v):
                    v = [v]
                for item in v:
                    if isinstance(item, dict):
                        collect_files(group_files, item)
                    else:
                        group_files.add(item)

        collect_files(group_files, self.groups)
        return group_files

    def write_file_references(self):
        self.product_uuids = {}
        self.file_uuids = {}
        with SectionHandler(self.file, "PBXFileReference"):
            for product in self.products:
                if SCons.Util.is_String(product):
                    prodpath = product
                else:
                    prodpath = str(self.relpath(product))
                filename = os.path.basename(prodpath)
                uuid = _generate_uuid()
                self.product_uuids[uuid] = filename

                self.file.write(
                    PBXPROJ_FILEREF
                    % (
                        uuid,
                        _escape_comment(filename),
                        _escape(filename),
                        _escape(prodpath),
                    )
                )
            for f in self.all_group_files():
                if SCons.Util.is_String(f):
                    filepath = f
                else:
                    filepath = str(self.relpath(f))
                filename = os.path.basename(filepath)
                uuid = _generate_uuid()
                self.file_uuids[f] = uuid

                self.file.write(
                    PBXPROJ_FILEREF
                    % (
                        uuid,
                        _escape_comment(filename),
                        _escape(filename),
                        _escape(filepath),
                    )
                )

    def write_group(self, group, contents):
        group_uuids = {}

        # First, scan for subgroups and write them out
        for item in contents:
            if isinstance(item, dict):
                for subgroup, subcontents in item.items():
                    uuid = self.write_group(subgroup, subcontents)
                    group_uuids[subgroup] = uuid

        # Now, write the group
        uuid = _generate_uuid()
        entries = []
        for item in contents:
            if isinstance(item, dict):
                for subgroup in item.keys():
                    entries.append(
                        PBXPROJ_GROUPENTRY
                        % (group_uuids[subgroup], _escape_comment(subgroup))
                    )
            else:
                if SCons.Util.is_String(item):
                    filepath = item
                else:
                    filepath = str(self.relpath(item))
                filename = os.path.basename(filepath)

                entries.append(
                    PBXPROJ_GROUPENTRY
                    % (self.file_uuids[item], _escape_comment(filename))
                )

        self.file.write(
            PBXPROJ_GROUP
            % (
                uuid,
                _escape_comment(group),
                "\n".join(entries),
                _escape(group),
                '"<group>"',
            )
        )

        return uuid

    def write_groups(self):
        all_groups = []
        with SectionHandler(self.file, "PBXGroup"):
            for group, contents in self.groups.items():
                uuid = self.write_group(group, contents)
                all_groups.append((uuid, group))

            products_uuid = _generate_uuid()
            all_groups.append((products_uuid, "Products"))
            entries = []
            for uuid, filename in self.product_uuids.items():
                entries.append(PBXPROJ_GROUPENTRY % (uuid, _escape_comment(filename)))
            self.file.write(
                PBXPROJ_GROUP
                % (
                    products_uuid,
                    "Products",
                    "\n".join(entries),
                    "Products",
                    '"<group>"',
                )
            )

            self.toplevel_group = _generate_uuid()
            entries = []
            for uuid, name in all_groups:
                entries.append(PBXPROJ_GROUPENTRY % (uuid, _escape_comment(name)))

            self.file.write(
                PBXPROJ_TOP_GROUP
                % (self.toplevel_group, "\n".join(entries), '"<group>"')
            )

    def write_build_configurations(self, names):
        config_uuids = {}
        for config in names:
            uuid = _generate_uuid()
            config_uuids[uuid] = config
            self.file.write(
                PBXPROJ_BUILDCONF % (uuid, _escape_comment(config), _escape(config))
            )
        return config_uuids

    def write_config_list(self, config_uuids, list_name):
        config_uuid = _generate_uuid()
        entries = []
        for uuid, name in config_uuids.items():
            entries.append(PBXPROJ_CONFENTRY % (uuid, _escape_comment(name)))

        self.file.write(
            PBXPROJ_CONFIGLIST
            % (config_uuid, _escape_comment(list_name), "\n".join(entries))
        )
        return config_uuid

    def write_targets(self):
        self.targets = []
        self.product_targets = {}
        with SectionHandler(self.file, "PBXLegacyTarget"):
            uuid = _generate_uuid()
            self.targets.append(uuid)
            self.file.write(
                PBXPROJ_LEGACYTARGET
                % (
                    uuid,
                    _escape_comment("Everything"),
                    _escape(
                        "--xcode-action=$(ACTION) --xcode-variant=$(CONFIGURATION)"
                    ),
                    self.target_cfg_uuid,
                    _escape_comment(
                        'Build configuration list for PBXLegacyTarget "%s"' % self.name
                    ),
                    os.path.abspath(sys.argv[0]),
                    _escape("Everything"),
                    _escape("Everything"),
                )
            )

            for product in self.products:
                if SCons.Util.is_String(product):
                    prodpath = product
                else:
                    prodpath = str(self.relpath(product))
                filename = os.path.basename(prodpath)

                uuid = _generate_uuid()
                self.product_targets[prodpath] = uuid
                self.targets.append(uuid)
                self.file.write(
                    PBXPROJ_LEGACYTARGET
                    % (
                        uuid,
                        _escape_comment(filename),
                        _escape(
                            '--xcode-action=$(ACTION) --xcode-variant=$(CONFIGURATION) "%s"'
                            % _escape(prodpath)
                        ),
                        self.target_cfgs[prodpath],
                        _escape_comment(
                            'Build configuration list for PBXLegacyTarget "%s"'
                            % filename
                        ),
                        os.path.abspath(sys.argv[0]),
                        _escape(filename),
                        _escape(filename),
                    )
                )

    def write_project(self):
        self.project_uuid = _generate_uuid()
        org = self.env["XCODEORGANIZATION"]
        with SectionHandler(self.file, "PBXProject"):
            target_attrs = [PBXPROJ_TARGETATTRS % uuid for uuid in self.targets]
            target_list = [PBXPROJ_TARGETENTRY % uuid for uuid in self.targets]

            self.file.write(
                PBXPROJ_PROJECT
                % (
                    self.project_uuid,
                    _escape(org),
                    "\n".join(target_attrs),
                    self.config_uuid,
                    self.toplevel_group,
                    "\n".join(target_list),
                )
            )


def GenerateProject(target, source, env):
    """Generate an .xcodeproj folder containing a suitable project.pbxproj."""
    xcodeproj = target[0]

    generator = XcodeProjectGenerator(xcodeproj, env)

    generator.build()


def projectEmitter(target, source, env):
    ###FIXME: Why does this not result in a rebuild if we change settings?

    # Set-up a dependency on our settings
    settings = _settings_from_env(target[0], env)

    if SCons.Util.is_List(settings["products"]):
        settings["products"] = [str(p) for p in settings["products"]]
    source_node = SCons.Node.Python.Value(repr(settings))

    return ([target[0]], [source_node])


_added = False


def generate(env):
    """Add Builders and construction variables for Xcode project files
    to an Environment."""
    from SCons.Script import AddOption, GetOption, SetOption

    global _added
    if not _added:
        _added = True
        AddOption(
            "--xcode-action",
            dest="xcode_action",
            type="string",
            action="store",
            default="",
            help="The action Xcode wishes to perform",
        )
        AddOption(
            "--xcode-variant",
            dest="xcode_variant",
            type="string",
            action="store",
            default="",
            help="The variant Xcode wishes to activate",
        )

    xcode = GetOption("xcode_action")
    if xcode == "clean":
        SetOption("clean", True)

    projectAction = SCons.Action.Action(GenerateProject, None)

    projectBuilder = SCons.Builder.Builder(
        action="$XCODEPROJECTCOM",
        suffix="$XCODEPROJECTSUFFIX",
        emitter=projectEmitter,
        target_factory=env.fs.Dir,
        source_factory=env.fs.Dir,
    )

    if "XcodeProject" not in env:
        env["BUILDERS"]["XcodeProject"] = projectBuilder

    env["XCODEPROJECTCOM"] = projectAction
    env["XCODEPROJECTSUFFIX"] = ".xcodeproj"
    env["XCODEORGANIZATION"] = "n/a"

    if "XCODE" not in env:
        env["XCODE"] = {}


def exists(env):
    return env.Detect("xcodebuild")


# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
