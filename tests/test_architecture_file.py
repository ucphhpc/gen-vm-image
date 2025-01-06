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

import unittest
from gen_vm_image.utils.io import join
from gen_vm_image.architecture import load_architecture
from gen_vm_image.common.codes import PATH_NOT_FOUND_ERROR


class TestImageArchitecture(unittest.TestCase):
    def setUp(self):
        self.architecture_path = join("tests", "res", "advanced_architecture.yml")

    def test_load_architecture(self):
        loaded, response = load_architecture(self.architecture_path)
        self.assertTrue(loaded)
        self.assertIn("architecture", response)
        architecture = response["architecture"]
        self.assertNotEqual(architecture, None)
        self.assertIsInstance(architecture, dict)

    def test_fail_load_architecture(self):
        missing_architecture_path = join("tests", "res", "missing.yml")
        loaded, response = load_architecture(missing_architecture_path)
        self.assertFalse(loaded)

        self.assertNotIn("architecture", response)
        self.assertIn("error_code", response)
        self.assertEqual(response["error_code"], PATH_NOT_FOUND_ERROR)

    def test_architecture_owner(self):
        loaded, response = load_architecture(self.architecture_path)
        self.assertTrue(loaded)
        self.assertIn("architecture", response)
        architecture = response["architecture"]

        self.assertIsInstance(architecture, dict)
        self.assertIn("owner", architecture)
        self.assertIsInstance(architecture["owner"], str)
        self.assertGreater(len(architecture["owner"]), 0)
        self.assertEqual(architecture["owner"], "the-owner-name")

    def test_architecture_images_top(self):
        loaded, response = load_architecture(self.architecture_path)
        self.assertTrue(loaded)
        self.assertIn("architecture", response)
        architecture = response["architecture"]

        self.assertIsInstance(architecture, dict)
        self.assertIn("images", architecture)
        self.assertIsInstance(architecture["images"], dict)
        self.assertGreater(len(architecture["images"]), 0)

    def test_architecture_images_items(self):
        loaded, response = load_architecture(self.architecture_path)
        self.assertTrue(loaded)
        self.assertIn("architecture", response)
        architecture = response["architecture"]

        self.assertIsInstance(architecture, dict)
        self.assertIn("images", architecture)
        self.assertIsInstance(architecture["images"], dict)
        self.assertGreater(len(architecture["images"]), 0)
        self.assertIn("image-1", architecture["images"])
        images = architecture["images"]

        for image_name, image_data in images.items():
            self.assertIsInstance(image_name, str)
            self.assertNotEqual(image_name, None)
            self.assertNotEqual(image_name, "")

            self.assertIsInstance(image_data, dict)
            self.assertIn("name", image_data)
            self.assertIsInstance(image_data["name"], str)
            self.assertGreater(len(image_data["name"]), 0)

            # Optional version attribute
            if "version" in image_data:
                self.assertIsInstance(image_data["version"], (float, int))

            self.assertIn("format", image_data)
            self.assertIsInstance(image_data["format"], str)
            self.assertGreater(len(image_data["format"]), 0)
            self.assertIn(image_data["format"], ["raw", "qcow2"])

            self.assertIn("size", image_data)
            self.assertIsInstance(image_data["size"], str)
            self.assertGreater(len(image_data["size"]), 0)
