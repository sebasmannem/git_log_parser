#! /usr/bin/env python

"""
Load git commits into postgres and report on it
"""

import codecs
import os
import re
from setuptools import find_packages
from setuptools import setup

INSTALL_REQUIREMENTS = [
    'psycopg2-binary==2.8.5',
]


def find_version():
    """Read the pgcdfga version from __init__.py."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, 'git_log', '__init__.py'),
                     'r') as file_pointer:
        version_file = file_pointer.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name='git_log_parser',
    version=find_version(),
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=INSTALL_REQUIREMENTS,
    entry_points={
        'console_scripts': [
            'git_log_commit_parser=git_log.commit_parser:main',
        ]
    }
)
