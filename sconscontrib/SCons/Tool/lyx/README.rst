##################
The SCons lyx tool
##################

Basics
======

This Tool teaches PDF to understand `.lyx` files. Notice that 
we initialize both 'pdflatex' and 'pdftex' tools in the example below, because
the pdftex tool takes `.tex files and then 
figures out from the file contents whether to run pdftex or pdflatex. The 
pdflatex tool only accepts the `.ltx` and `.latex` extensions.

Usage
-----

::

    env = Environment(tools=['default', 'pdftex', 'pdflatex', 'lyx'])
    env.PDF(source='test.lyx')

