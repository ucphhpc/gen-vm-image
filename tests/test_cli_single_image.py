# Copyright (C) 2025  The gen-vm-image Project by the Science HPC Center at UCPH
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

import unittest
import os
import random
from gen_vm_image.common.codes import SUCCESS
from gen_vm_image.common.defaults import SINGLE
from gen_vm_image.utils.io import makedirs, exists, remove, join
from gen_vm_image.cli.cli import main


class TestCLISingleImage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.seed = str(random.random())[2:10]
        cls.images_dir = os.path.realpath(join("tests", "tmp", "images", cls.seed))
        cls.res_dir = os.path.realpath(join("tests", "res"))
        if not exists(cls.images_dir):
            assert makedirs(cls.images_dir)

    @classmethod
    def tearDownClass(cls):
        if exists(cls.images_dir):
            assert remove(cls.images_dir, recursive=True)

    def test_cli_help(self):
        return_code = None
        try:
            return_code = main([SINGLE, "--help"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_cli_basic_single_image(self):
        return_code = None
        try:
            name = "test-cli-single-image-{}".format(self.seed)
            size = "5G"
            return_code = main(
                [SINGLE, name, size, "--output-directory", self.images_dir]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
        output_path = join(self.images_dir, "{}.qcow2".format(name))
        self.assertTrue(exists(output_path))

    def test_cli_single_image_with_output_format_raw(self):
        return_code = None
        try:
            name = "test-cli-single-image-output-format-{}".format(self.seed)
            size = "5G"
            output_format = "raw"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--output-format",
                    output_format,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

        output_path = join(self.images_dir, "{}.{}".format(name, output_format))
        self.assertTrue(exists(output_path))

    def test_cli_single_image_with_output_format_qcow2(self):
        return_code = None
        try:
            name = "test-cli-single-image-output-format-{}".format(self.seed)
            size = "5G"
            output_format = "qcow2"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--output-format",
                    output_format,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

        output_path = join(self.images_dir, "{}.{}".format(name, output_format))
        self.assertTrue(exists(output_path))

    def test_cli_single_image_with_version(self):
        return_code = None
        try:
            name = "test-cli-single-image-version-{}".format(self.seed)
            size = "5G"
            version = "1.0"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--version",
                    version,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

        output_path = join(self.images_dir, "{}-{}.qcow2".format(name, version))
        self.assertTrue(exists(output_path))

    def test_cli_single_image_with_input_path(self):
        return_code = None
        try:
            name = "test-cli-single-image-input-{}".format(self.seed)
            size = "5G"
            input_path = join(self.res_dir, "test.qcow2")
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    input_path,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

        output_path = join(self.images_dir, "{}.qcow2".format(name))
        self.assertTrue(exists(output_path))

    def test_cli_single_image_with_input_path_and_raw_output_format(self):
        return_code = None
        try:
            name = "test-cli-single-image-input-{}".format(self.seed)
            size = "5G"
            input_path = join(self.res_dir, "test.qcow2")
            output_format = "raw"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    input_path,
                    "--output-format",
                    output_format,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

        output_path = join(self.images_dir, "{}.{}".format(name, output_format))
        self.assertTrue(exists(output_path))

    def test_cli_single_image_with_input_url(self):
        return_code = None
        try:
            name = "test-cli-single-image-input-{}".format(self.seed)
            size = "5G"
            image_url = "https://download.rockylinux.org/pub/rocky/9/images/x86_64/Rocky-9-GenericCloud-Base.latest.x86_64.qcow2"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    image_url,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

        output_path = join(self.images_dir, "{}.qcow2".format(name))
        self.assertTrue(exists(output_path))

    # TODO add tests for checksum validation