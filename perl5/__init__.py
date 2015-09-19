#!/usr/bin/env python
# -*- coding: utf-8 -*-

## Copyright (C) 2011-2015 Carnë Draug <carandraug+dev@gmail.com>
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see
## <http:##www.gnu.org/licenses/>.

"""SCons tool for perl5 scripts and modules
"""

import os
import os.path
import subprocess
import distutils.spawn

import SCons.Script

SCANDEPS_BIN = ""

def perl5_scanner(node, env, path):
  perl_inc = ["-I" + inc for inc in env['PERL5LIB']]
  perl_args = ["perl", "-MModule::ScanDeps"] + perl_inc
  code = """
    $deps = scan_deps (files => ['%s'],
                       recurse => 0);
    foreach (keys %%{$deps})
      { print $deps->{$_}->{file} . "\\n"; }
  """ % str(node)
  deps = subprocess.check_output(perl_args + ["-e", code], env=env['ENV'])

  our_deps = []
  cwd = os.path.realpath(os.getcwd())
  for dep in deps.splitlines():
    dep = os.path.realpath(dep)
    if dep.startswith(cwd):
      our_deps.append(dep)
  return env.File(our_deps)

## This is currently unused because there's no way to share configure tests.
def CheckPerlModule(context, module_name):
  context.Message("Checking for perl module %s..." % module_name)
  is_ok = 0 == subprocess.call(["perl", "-M" + module_name, "-e 1"],
                               stdout = open(os.devnull, "wb"))
  context.Result(is_ok)
  return is_ok

def generate(env):
  vars = SCons.Script.Variables()
  vars.Add('PERL5LIB', ("List of directories in which to look for Perl"
                         + " library files before looking in the standard"
                         + " library and the current directory."))
  vars.Update(env)
  SCons.Script.Help(vars.GenerateHelpText(env))

  scanner = SCons.Script.Scanner(perl5_scanner, skeys=['.pl', '.pm'])
  env.Append(SCANNERS=scanner)

def exists(env):
  if not distutils.spawn.find_executable("perl"):
    return 0

  rc = subprocess.call(["perl", "-MModule::ScanDeps", "-e", "1;"])
  return rc == 0
