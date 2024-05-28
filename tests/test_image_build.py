import unittest
import random
import wget
from gen_vm_image.utils.io import join, find, remove, exists
from gen_vm_image.architecture import load_architecture
from gen_vm_image.cli.build_image import create_image, convert_image


class TestImageBuild(unittest.TestCase):
    def setUp(self):
        self.seed = str(random.random())[2:10]
        self.architecture_path = join("tests", "res", "architecture.yml")
        self.architecture, error = load_architecture(self.architecture_path)
        self.assertNotEqual(self.architecture, None)
        self.assertEqual(error, None)
        self.assertIsInstance(self.architecture, dict)

    def tearDown(self):
        # Remove every seed file
        regex_name = ".*{}.*".format(self.seed)
        seed_files = find(".", regex_name)
        for seed_file in seed_files:
            if exists(seed_file):
                self.assertTrue(remove(seed_file)[0])

    def test_create_image_1(self):
        image_1 = self.architecture["images"]["image-1"]
        self.assertEqual(image_1["name"], "test-image-1")
        image_1_name = "{}-{}".format(image_1["name"], self.seed)
        self.assertEqual(image_1["version"], 9.4)
        self.assertEqual(image_1["format"], "qcow2")
        self.assertEqual(image_1["size"], "10G")

        result, msg = create_image(
            image_1_name,
            image_1["version"],
            image_1["size"],
            image_format=image_1["format"],
        )
        self.assertNotIsInstance(result, int)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["returncode"], "0")
        self.assertIsNone(msg)

    def test_convert_image(self):
        debian_12 = self.architecture["images"]["Debian-12"]
        self.assertEqual(debian_12["name"], "Debian")
        self.assertEqual(debian_12["version"], 12)
        self.assertEqual(debian_12["format"], "qcow2")
        self.assertEqual(debian_12["size"], "20G")

        input_path = "debian-input-{}.qcow2".format(self.seed)
        self.assertIn("input", debian_12)
        self.assertGreater(len(debian_12["input"]), 0)
        self.assertIn("url", debian_12["input"])
        self.assertIn("format", debian_12["input"])
        wget.download(debian_12["input"]["url"], out=input_path)
        self.assertTrue(exists(input_path))
        output_path = "debian-output-{}.qcow2".format(self.seed)

        result, msg = convert_image(
            input_path,
            output_path,
            input_format=debian_12["format"],
            output_format=debian_12["format"],
        )
        self.assertNotIsInstance(result, int)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["returncode"], "0")
        self.assertIsNone(msg)
        self.assertTrue(exists(output_path))
        # TODO, validate that the output image is of the correct size and format
