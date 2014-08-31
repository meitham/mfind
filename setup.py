#!/usr/bin/env python

import sys

from setuptools import setup


classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Utilities',
]

long_description = open('README.rst').read()

version = '0.7'


def main():
    scripts = ['bin/mfind.py']
    if sys.platform == "win":
        scripts.append('bin/mfind.bat')
    else:
        scripts.append('bin/mfind')

    install_requires = []
    if sys.version_info < (2, 7) or (3,) <= sys.version_info < (3, 2):
        install_requires.append('argparse')

    setup(name='mfind',
          version=version,
          description="Meta find, like GNU find but works on file metadata",
          author='Meitham Jamaa',
          author_email='m at meitham.com',
          url='https://meitham.com/mfind/',
          license='BSD License',
          py_modules=('mfinder', ),
          scripts=scripts,
          classifiers=classifiers,
          )


if __name__ == '__main__':
    main()
