#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys


try:
    from setuptools import setup
    from setuptools.command.test import test as TestCommand
except ImportError:
    from distutils.core import setup

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.md').read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='thing',
    version='0.1.0',
    description='An attempt at using Trello as a todo/bookmark thing',
    long_description=readme,
    author='Wayne Werner',
    author_email='waynejwerner@gmail.com',
    url='https://github.com/waynew/trellish-todoish',
    packages=[
        'thing',
    ],
    entry_points={
        'console_scripts': [
            'thing-doer = thing.thing:run',
        ],
    },
    cmdclass={'test': PyTest},
    package_dir={'thing': 'thing'},
    include_package_data=True,
    install_requires=['trello'
    ],
    license="BSD",
    zip_safe=False,
    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=['pytest', 'hypothesis', 'pytest-cov'],
)
