# -*- coding: utf-8 -*-
from setuptools import setup


with open('README.rst') as f:
    readme = f.read()

setup(
    name='maxcube-api',
    version='0.4.0',
    description='eQ-3/ELV MAX! Cube Python API',
    long_description=readme,
    author='David Uebelacker',
    author_email='david@uebelacker.ch',
    url='https://github.com/hackercowboy/python-maxcube-api.git',
    license=license,
    packages=['maxcube'],
    test_suite="tests",
    python_requires='>=3.7'
)
