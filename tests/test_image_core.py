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
import random
from gen_vm_image.utils.io import join, find, remove, exists
from gen_vm_image.image import create_image, convert_image, resize_image
from .context import AsyncImageTestContext


class TestImageBuild(unittest.IsolatedAsyncioTestCase):
    context = AsyncImageTestContext()

    async def asyncSetUp(self):
        await self.context.setUp()
        self.seed = str(random.random())[2:10]

    async def asyncTearDown(self):
        # Remove every seed file
        regex_name = ".*{}.*".format(self.seed)
        seed_files = find(self.context.test_tmp_directory, regex_name)
        for seed_file in seed_files:
            if exists(seed_file):
                self.assertTrue(remove(seed_file))

    @classmethod
    def tearDownClass(cls):
        cls.context.tearDown()

    async def test_create_image_qcow_1(self):
        image_1 = self.context.architecture["images"]["image-1"]
        self.assertEqual(image_1["name"], "test-image-1")
        image_1_name = "{}-{}".format(image_1["name"], self.seed)
        self.assertEqual(image_1["version"], 9.4)
        self.assertEqual(image_1["format"], "qcow2")
        self.assertEqual(image_1["size"], "10G")

        new_image_path = join(
            self.context.test_tmp_directory,
            "{}.{}".format(image_1_name, image_1["format"]),
        )
        result, msg = await create_image(
            new_image_path,
            image_1["size"],
            image_format=image_1["format"],
        )
        self.assertTrue(result)
        self.assertEqual(msg, b"")

    async def test_create_image_raw_2(self):
        image_2 = self.context.architecture["images"]["image-2"]
        self.assertEqual(image_2["name"], "test-image-2")
        image_2_name = "{}-{}".format(image_2["name"], self.seed)
        self.assertEqual(image_2["version"], 9.4)
        self.assertEqual(image_2["format"], "raw")
        self.assertEqual(image_2["size"], "10G")

        new_image_path = join(
            self.context.test_tmp_directory,
            "{}.{}".format(image_2_name, image_2["format"]),
        )
        result, msg = await create_image(
            new_image_path,
            image_2["size"],
            image_format=image_2["format"],
        )
        self.assertTrue(result)
        self.assertEqual(msg, b"")

    async def test_image_path_input(self):
        input_path_image = self.context.architecture["images"]["input_path_image"]
        self.assertEqual(input_path_image["name"], "input-path-image")
        self.assertEqual(input_path_image["version"], 12)
        self.assertEqual(input_path_image["format"], "qcow2")
        self.assertEqual(input_path_image["size"], "20G")

        self.assertIn("input", input_path_image)
        self.assertIsInstance(input_path_image["input"], dict)
        self.assertIn("path", input_path_image["input"])
        self.assertIn("format", input_path_image["input"])

        self.assertEqual(
            input_path_image["input"]["path"], self.context.input_image_path
        )
        self.assertEqual(input_path_image["input"]["format"], "qcow2")
        self.assertTrue(exists(self.context.input_image_path))

        output_path = join(
            self.context.test_tmp_directory,
            "{}-{}.{}".format(
                input_path_image["name"], self.seed, input_path_image["format"]
            ),
        )

        concert_result, convert_msg = await convert_image(
            input_path_image["input"]["path"],
            output_path,
            input_format=input_path_image["input"]["format"],
            output_format=input_path_image["format"],
        )
        self.assertTrue(concert_result)
        self.assertEqual(convert_msg, b"")
        self.assertTrue(exists(output_path))

        resize_result, resize_msg = await resize_image(
            output_path,
            input_path_image["size"],
            image_format=input_path_image["format"],
        )
        self.assertTrue(resize_result)
        self.assertEqual(resize_msg, b"")
        # TODO, validate that the size of the output image is correct

    async def test_convert_image_format(self):
        convert_image_dict = self.context.architecture["images"][
            "convert_input_image_format"
        ]
        self.assertEqual(convert_image_dict["name"], "convert_input_image_format")
        self.assertEqual(convert_image_dict["version"], 12)
        self.assertEqual(convert_image_dict["format"], "raw")
        self.assertEqual(convert_image_dict["size"], "20G")

        self.assertIn("input", convert_image_dict)
        self.assertGreater(len(convert_image_dict["input"]), 0)
        self.assertIn("path", convert_image_dict["input"])
        self.assertIn("format", convert_image_dict["input"])
        self.assertEqual(convert_image_dict["input"]["format"], "qcow2")

        self.assertTrue(exists(convert_image_dict["input"]["path"]))
        output_path = join(
            self.context.test_tmp_directory,
            "{}-{}.{}".format(
                convert_image_dict["name"], self.seed, convert_image_dict["format"]
            ),
        )

        result, msg = await convert_image(
            convert_image_dict["input"]["path"],
            output_path,
            input_format=convert_image_dict["input"]["format"],
            output_format=convert_image_dict["format"],
        )
        self.assertTrue(result)
        self.assertEqual(msg, b"")
        self.assertTrue(exists(output_path))
        # TODO, validate that the output image is of the correct size and format

    async def test_build_with_no_version(self):
        image_no_version = self.context.architecture["images"]["non_version_image_test"]
        self.assertEqual(image_no_version["name"], "non-version-image")
        self.assertEqual(image_no_version["format"], "raw")
        self.assertEqual(image_no_version["size"], "10G")

        new_image_path = join(
            self.context.test_tmp_directory,
            "{}-{}.{}".format(
                image_no_version["name"], self.seed, image_no_version["format"]
            ),
        )
        result, msg = await create_image(
            new_image_path,
            image_no_version["size"],
            image_format=image_no_version["format"],
        )
        self.assertTrue(result)
        self.assertEqual(msg, b"")
        self.assertTrue(exists(new_image_path))
