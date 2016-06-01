#!/usr/bin/env python

from setuptools import setup

setup(name='sconscontrib',
      version='1.0',
      description='Contributed builders and other useful logic for the SCons build system.',
      author='The SCons Foundation',
      author_email='scons-users@scons.org',
      url='https://bitbucket.org/scons/scons-contrib/',
      packages=['sconscontrib/SCons/Tool/cuda'],
      install_requires=['scons'],
      license='MIT',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: Developers',
                   'Topic :: Software Development :: Build Tools',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2'
                  ],
      keywords='scons build development',

      # install executable script without .py extension
      #py_modules=['Dummy'],
      #entry_points={'console_scripts': ['Dummy = Dummy:main']}

     )
