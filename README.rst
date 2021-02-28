NOTE: This branch is Python 2.7 compatible. No further development or PR's will be accepted.
############################################################################################

For now do not install using pip or setup.py as those need some maintenence and won't work.
###########################################################################################

SCons - a software construction tool contrib repo
#################################################


Basics
======


Welcome to the SCons contrib repo.  The real purpose of this tree is to
provide a place for contributed builders and other useful logic.
Previously many such files were posted to the wiki but that's not
very functional.

Please create a directory per contribution.
We may re-organize if it becomes obvious that doing so would 
make it easier for users to find useful logic.


Installing
==========

For installing via ``pip``, you have to say

::

    pip install sconscontrib

Your other option is to clone the repository ``https://bitbucket.org/scons/scons-contrib``, change into its
top-level folder, get root and then run the command

::

    python setup.py install

Requirements
============

The SCons contrib package requires you to have

* scons
 
installed.

TODOs and known problems
========================

* Implement more commands/builders/tools.
