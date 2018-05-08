#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from setuptools import setup


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    with open(os.path.join(package, '__init__.py')) as f:
        init_py = f.read()

    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under root package, that are not in a package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


def get_long_description(long_description_file):
    """
    Read long description from file.
    """
    with open(long_description_file) as f:
        long_description = f.read()

    return long_description


name = 'apistar-auth'
package_name = 'apistar_auth'
version = get_version(package_name)

setup(
    name=name,
    version=version,
    description='Authentication integration based on SQLAlchemy for API Star.',
    long_description=get_long_description('README.rst'),
    author='Sander Mathijs van Veen',
    author_email='sandervv+pypi@gmail.com',
    maintainer='Sander Mathijs van Veen',
    maintainer_email='sandervv+pypi@gmail.com',
    url='https://github.com/smvv/apistar-auth',
    download_url='https://github.com/smvv/apistar-auth',
    packages=get_packages(package_name),
    package_data=get_package_data(package_name),
    install_requires=[
        'apistar',
        'apistar-sqlalchemy',
        'SQLAlchemy',
        'SQLAlchemy-Utils',
        'passlib',
        'bcrypt',
    ],
    tests_require=[
        'apistar',
        'clinner',
        'coverage',
        'prospector',
        'pytest',
        'pytest-xdist',
        'pytest-cov',
        'tox',
    ],
    license='MIT',
    keywords=' '.join([
        'python',
        'apistar',
        'api',
        'sqlalchemy',
        'auth',
        'authentication',
        'login',
        'session',
        'cookie',
        'user',
        'role',
    ]),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Database',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
