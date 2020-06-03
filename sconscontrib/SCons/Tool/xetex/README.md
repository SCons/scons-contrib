# Xe(La)Tex Tool for SCons

## Introduction

[SCons](http://www.scons.org) is a build framework originally for C, C++, Fortran, and D builds. It has
though a tools (think plugin) architecture that allows tools to be built for other language builds. This
repository contains a tool for building Xetex and XeLaTex documents.

Original source due to Robert Managan, various additions by Russel Winder.

## Usage

You need to clone the scons-contrib Git repository.

You then need to make a symbolic link to
<scons-contrib-location>/sconscontrib/SCons/Tool/xetex from ~/.scons/site_scons/site_tools/xetex

You then need to load the xetex tool in your SConstruct file, for ecxample:

```python
environment = Environment(
    tools=['xetex'],
    ENV=os.environ,
)
```

You can then use the builders, for example:

```python
targets = [environment.XELATEX(file)[0].name for file in Glob('*.ltx')]
```

The above will allow you a directory of LaTeX source files all of which can be built
individually, or by default, all of them get built.

## Licence

This software is provided by the SCons Foundation under the MIT
Licence.  [![MIT Licence](Images/mit_licence_50.png)](https://opensource.org/licenses/MIT)
