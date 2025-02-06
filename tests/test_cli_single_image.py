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
from gen_vm_image.common.codes import SUCCESS, CHECKSUM_ERROR
from gen_vm_image.common.defaults import SINGLE
from gen_vm_image.utils.io import makedirs, exists, remove, join
from gen_vm_image.cli.cli import main


TEST_RES_DIR = os.path.realpath(join("tests", "res"))
TEST_IMAGE_NAME = "test.qcow2"
TEST_IMAGE_PATH = os.path.realpath(join(TEST_RES_DIR, TEST_IMAGE_NAME))


class TestCLISingleImage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.seed = str(random.random())[2:10]
        cls.images_dir = os.path.realpath(join("tests", "tmp", "images", cls.seed))
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
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    TEST_IMAGE_PATH,
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
            output_format = "raw"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    TEST_IMAGE_PATH,
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

    def test_cli_single_image_with_checksum(self):
        expected_checksum = "db12db337b0d1c82ab5b174c21241e0be24ee44a79e0d310aa05e3652e301a22bf604fd86c4cf9e4489bd512cab275feb8d8326847ca04b90e0903c72f39cb64"
        return_code = None
        try:
            name = "test-cli-single-image-checksum-{}".format(self.seed)
            size = "10G"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    TEST_IMAGE_PATH,
                    "--input-checksum-type",
                    "sha512",
                    "--input-checksum",
                    expected_checksum,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
        output_path = join(self.images_dir, "{}.qcow2".format(name))
        self.assertTrue(exists(output_path))

    def test_cli_single_image_incorrect_checksum(self):
        expected_checksum = "12931j3901j39183189231230912309-01230-0-askdasidma"
        return_code = None
        try:
            name = "test-cli-single-image-checksum-{}".format(self.seed)
            size = "10G"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    TEST_IMAGE_PATH,
                    "--input-checksum-type",
                    "sha512",
                    "--input-checksum",
                    expected_checksum,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, CHECKSUM_ERROR)
        output_path = join(self.images_dir, "{}.qcow2".format(name))
        self.assertFalse(exists(output_path))

    def test_cli_single_image_with_checksum_and_partial_bytes(self):
        expected_checksum = "1d7e67951f6b693b8f0ec66c7ad27743edb9088bee19b60cdd564abe0f3d1f36664299aa03ad4903e60fccdd60faf71b4eacb498c8c33da06bd5f6f33f7852ce"
        return_code = None
        try:
            name = "test-cli-single-image-checksum-partial-bytes-{}".format(self.seed)
            size = "5G"
            read_bytes_of_file = "1000"
            return_code = main(
                [
                    SINGLE,
                    name,
                    size,
                    "--output-directory",
                    self.images_dir,
                    "--input",
                    TEST_IMAGE_PATH,
                    "--input-checksum-type",
                    "sha512",
                    "--input-checksum",
                    expected_checksum,
                    "--input-checksum-read-bytes",
                    read_bytes_of_file,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
        output_path = join(self.images_dir, "{}.qcow2".format(name))
        self.assertTrue(exists(output_path))
