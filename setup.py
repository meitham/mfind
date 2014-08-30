#!/usr/bin/env python

from setuptools import setup, find_packages
import sys


version = '0.7'

scripts = ['bin/mfind.py']

if sys.platform == "win":
    scripts.append('bin/mfind.bat')
else:
    scripts.append('bin/mfind')

setup(name='mfind',
      version=version,
      description="Meta find, like GNU find but works on file metadata",
      author='Meitham Jamaa',
      author_email='meitham@meitham.com',
      url='https://meitham.com/mfind/',
      packages=find_packages(),
      py_modules=('mfinder'),
      scripts=scripts,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Shell Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2.7',
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
      )
