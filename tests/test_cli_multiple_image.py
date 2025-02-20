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
from gen_vm_image.common.defaults import MULTIPLE
from gen_vm_image.common.codes import SUCCESS
from gen_vm_image.utils.io import exists, makedirs, join, remove
from gen_vm_image.cli.cli import main

BASE_IMAGES_DIRECTORY = os.path.realpath(join("tests", "tmp", "images"))

BASIC_ARCHITECTURE_FILE = "basic_architecture.yml"
BASIC_ARCHITECTURE_PATH = os.path.realpath(
    join("tests", "res", BASIC_ARCHITECTURE_FILE)
)

ADVANCED_ARCHITECTURE_FILE = "advanced_architecture.yml"
ADVANCED_ARCHITECTURE_PATH = os.path.realpath(
    join("tests", "res", ADVANCED_ARCHITECTURE_FILE)
)


class TestCLIMultipleImage(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.seed = str(random.random())[2:10]
        cls.images_dir = join(BASE_IMAGES_DIRECTORY, cls.seed)
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
            return_code = main([MULTIPLE, "--help"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_cli_basic_multiple_images(self):
        return_code = None
        try:
            self.assertTrue(exists(BASIC_ARCHITECTURE_PATH))
            return_code = main(
                [
                    MULTIPLE,
                    BASIC_ARCHITECTURE_PATH,
                    "--output-directory",
                    self.images_dir,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
        expected_ouput_image_name = "test-image-9.4.qcow2"
        expected_output_image = join(self.images_dir, expected_ouput_image_name)
        self.assertTrue(exists(expected_output_image))
        # TODO verify the size is correct

    def test_cli_advanced_multiple_images(self):
        return_code = None
        try:
            self.assertTrue(exists(ADVANCED_ARCHITECTURE_PATH))
            return_code = main(
                [
                    MULTIPLE,
                    ADVANCED_ARCHITECTURE_PATH,
                    "--output-directory",
                    self.images_dir,
                ]
            )
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)
        expected_images = [
            "test-image-1-9.4.qcow2",
            "test-image-2-9.4.raw",
            "test-image-3-8.4.qcow2",
            "test-image-4-8.4.raw",
            "test-image-5-9.4.raw",
            "input-path-image-12.qcow2",
            "convert_input_image_format-12.raw",
            "non-version-image.raw",
            "image-with-output-path-9.4.qcow2",
        ]
        for image in expected_images:
            expected_output_image = join(self.images_dir, image)
            self.assertTrue(exists(expected_output_image))
