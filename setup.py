#!/usr/bin/env python

from distutils.core import setup

setup(name='troposphereWrapper',
      version = '0.1.2',
      description = 'Wrapper for Troposphere',
      author = 'Janos Potecki',
      url = 'https://github.com/jpotecki/TroposphereWrapper',
      packages = ['troposphereWrapper'],
      install_requires = [
          'troposphere', 'awacs'
      ]
     )