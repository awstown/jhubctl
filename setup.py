#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os
import sys
from shutil import rmtree

from setuptools import setup, find_packages

# Package meta-data.
NAME = 'jhubctl'
DESCRIPTION = 'CLI for managing Jupyterhub instances on AWS+Kubernetes'
URL = 'https://github.com/townsenddw/jhubctl'
EMAIL = ''
AUTHOR = 'Dwight Townsend, Zach Sailer'
REQUIRES_PYTHON = '>=3.6.0'
VERSION = None

REQUIRED = [
    "pyyaml",
    "traitlets_paths",
    "traitlets"
    "tqdm",
    "ipython",
    "kubeconf",
    "boto3",
    "jinja2",
]

setup(
    name=NAME,
    version="0.0.1",
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(exclude=('tests',)),
    entry_points={
        'console_scripts': ['jhubctl=jhubctl.main:main'],
    },
    install_requires=REQUIRED,
    include_package_data=True,
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ],
)
