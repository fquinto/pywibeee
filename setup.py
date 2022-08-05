#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Setup package."""

import ast
import io
import re
import os
from setuptools import find_packages, setup

DEPENDENCIES = ["xmltodict", "requests", "aiohttp", "httpx"]
EXCLUDE_FROM_PACKAGES = ["contrib", "docs", "tests*"]
CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "README.rst"), "r", encoding="utf-8") as f:
    long_description = f.read()
long_description += "\n\n"


def get_version():
    """Provide version."""
    main_file = os.path.join(CURDIR, "pywibeee", "main.py")
    _version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")
    with open(main_file, "r", encoding="utf8") as f:
        match = _version_re.search(f.read())
        version = match.group("version") if match is not None else '"unknown"'
    return str(ast.literal_eval(version))


def get_long_description():
    """
    Return the README and CHANGELOG.md.
    """
    long_description = ""
    with open("README.rst", encoding="utf8") as f:
        long_description += f.read()
    # long_description += "\n\n"
    # with open(os.path.join(CURDIR, "CHANGELOG.md"), encoding="utf8") as f:
    #     long_description += f.read()
    return long_description


setup(
    name="pywibeee",
    version=get_version(),
    author="fquinto",
    author_email="fran.quinto@gmail.com",
    description="Command line interface (CLI) for WiBeee (old Mirubee) meter",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/fquinto/pywibeee",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    keywords=['homeautomation', 'cli', 'interface', 'wibeee', 'mirubeee',
              'energy meter', 'smart meter', 'hass'],
    scripts=['bin/pywibeee'],
    zip_safe=False,
    install_requires=DEPENDENCIES,
    test_suite="tests.test_project",
    python_requires=">=3.7",
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Topic :: Home Automation",
        "Topic :: System :: Monitoring",
        "Topic :: System :: Shells",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Developers",
    ],
)
