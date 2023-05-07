#! /usr/bin/env python

#
# Licensed to Elasticsearch under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from setuptools import setup, find_packages
from pathlib import Path

CWD = Path(__file__).parent

README = (CWD / "README.md").read_text()

setup(
    name="swat",
    version="0.1.0",
    description="SWAT is a red teaming tool for Google Workspace environments.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/elastic/SWAT",
    author="Terrance DeJesus",
    author_email="contact@dejesus.io",
    maintainer="Elastic",
    license="Apache License 2.0",
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Security",
        "Topic :: Google Workspace",
    ],
    include_package_data=True,

    packages=find_packages(),
    install_requires=open("requirements.txt", "r").read(),
    entry_points={
        "console_scripts": [
            "swat = swat.main:main",
        ],
    },
)
