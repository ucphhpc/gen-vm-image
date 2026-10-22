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

import os
import random
import unittest

from gen_vm_image.cli.cli import main
from gen_vm_image.common.codes import PATH_NOT_FOUND_ERROR, SUCCESS
from gen_vm_image.common.defaults import REMOVE
from gen_vm_image.utils.io import exists, join, makedirs, remove, write


class TestCLIRemove(unittest.TestCase):

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

    def _create_test_image(self, name):
        image_path = join(self.images_dir, name)
        assert write(image_path, "test content")
        return image_path

    def test_cli_help(self):
        return_code = None
        try:
            return_code = main([REMOVE, "--help"])
        except SystemExit as e:
            return_code = e.code
        self.assertEqual(return_code, SUCCESS)

    def test_cli_remove_with_absolute_path(self):
        image_name = "test-remove-abs-{}.qcow2".format(self.seed)
        image_path = self._create_test_image(image_name)
        self.assertTrue(exists(image_path))

        return_code = main([REMOVE, image_path])
        self.assertEqual(return_code, SUCCESS)
        self.assertFalse(exists(image_path))

    def test_cli_remove_with_relative_path_default_source_directory(self):
        image_name = "test-remove-rel-default-{}.qcow2".format(self.seed)
        default_dir = "generated-images"
        full_path = join(default_dir, image_name)
        if not exists(default_dir):
            assert makedirs(default_dir)
        assert write(full_path, "test content")
        self.assertTrue(exists(full_path))

        try:
            return_code = main([REMOVE, image_name])
            self.assertEqual(return_code, SUCCESS)
            self.assertFalse(exists(full_path))
        finally:
            if exists(default_dir):
                remove(default_dir, recursive=True)

    def test_cli_remove_with_relative_path_custom_source_directory(self):
        image_name = "test-remove-rel-custom-{}.qcow2".format(self.seed)
        image_path = self._create_test_image(image_name)
        self.assertTrue(exists(image_path))

        return_code = main([REMOVE, image_name, "--source-directory", self.images_dir])
        self.assertEqual(return_code, SUCCESS)
        self.assertFalse(exists(image_path))

    def test_cli_remove_non_existent_path(self):
        non_existent = join(self.images_dir, "non-existent-{}.qcow2".format(self.seed))
        return_code = main(
            [REMOVE, non_existent, "--source-directory", self.images_dir]
        )
        self.assertEqual(return_code, SUCCESS)

    def test_cli_remove_non_existent_relative_path(self):
        return_code = main(
            [
                REMOVE,
                "non-existent-{}.qcow2".format(self.seed),
                "--source-directory",
                self.images_dir,
            ]
        )
        self.assertEqual(return_code, SUCCESS)

    def test_cli_remove_with_verbose(self):
        image_name = "test-remove-verbose-{}.qcow2".format(self.seed)
        image_path = self._create_test_image(image_name)
        self.assertTrue(exists(image_path))

        return_code = main(
            [
                REMOVE,
                image_name,
                "--source-directory",
                self.images_dir,
                "--verbose",
            ]
        )
        self.assertEqual(return_code, SUCCESS)
        self.assertFalse(exists(image_path))


if __name__ == "__main__":
    unittest.main()
