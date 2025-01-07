#!/usr/bin/python
# coding: utf-8
# Copyright (C) 2024  The gen-vm-image Project by the Science HPC Center at UCPH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import os
from setuptools import setup, find_packages

cur_dir = os.path.realpath(os.path.dirname(__file__))


def read(path):
    with open(path, "r") as _file:
        return _file.read()


def read_req(name):
    path = os.path.join(cur_dir, name)
    return [req.strip() for req in read(path).splitlines() if req.strip()]


version_ns = {}
version_path = os.path.join(cur_dir, "gen_vm_image", "_version.py")
version_content = read(version_path)
exec(version_content, {}, version_ns)


long_description = open("README.rst").read()
setup(
    name="gen-vm-image",
    version=version_ns["__version__"],
    description="This tool can be used for generating virtual machine images.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    author="Rasmus Munk",
    author_email="munk1@live.dk",
    packages=find_packages(),
    url="https://github.com/ucphhpc/gen-vm-image",
    license="GNU General Public License v2 (GPLv2)",
    keywords=["Virtual Machine", "VM", "Images"],
    install_requires=read_req("requirements.txt"),
    extras_require={
        "test": read_req("tests/requirements.txt"),
        "dev": read_req("requirements-dev.txt"),
    },
    # Ensures that the plugin can be discovered/loaded by corc
    entry_points={
        "console_scripts": [
            "gen-vm-image = gen_vm_image.cli.cli:cli",
        ],
        "corc.plugins": ["gen_vm_image=gen_vm_image"],
        "corc.plugins.initializer": ["gen_vm_image=gen_vm_image.image:generate_image"],
        "corc.plugins.cli": ["gen_vm_image=gen_vm_image.cli.corc:gen_vm_image_cli"],
    },
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
