#!/usr/bin/env python
import os
import re
import sys

from setuptools import setup, find_packages


version = re.compile(r'VERSION\s*=\s*\((.*?)\)')


def get_package_version():
    """
    :returns: package version without importing it.
    """

    base = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(base, "gotalk/__init__.py")) as initf:
        for line in initf:
            m = version.match(line.strip())
            if not m:
                continue
            return ".".join(m.groups()[0].split(", "))


def get_requirements(filename):
    return open('requirements/' + filename).read().splitlines()


classes = """
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: BSD License
    Topic :: System :: Distributed Computing
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.6
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4
    Programming Language :: Python :: Implementation :: CPython
    Operating System :: OS Independent
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


install_requires = get_requirements('install.txt')
if sys.version_info < (3, 0):
    install_requires.append('futures')


setup(
    name='gotalk',
    version=get_package_version(),
    description='A Python implementation of the Gotalk protocol.',
    long_description=open('README.rst').read(),
    author='Greg Taylor',
    author_email='gtaylor@gc-taylor.com',
    url='https://github.com/gtaylor/python-gotalk',
    license='BSD',
    classifiers=classifiers,
    packages=find_packages(exclude=['tests', 'tests.*']),
    install_requires=install_requires,
    test_suite="tests",
    tests_require=get_requirements('test.txt'),
)
