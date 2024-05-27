import unittest
from gen_vm_image.utils.io import join
from gen_vm_image.architecture import load_architecture
from gen_vm_image.common.errors import PATH_NOT_FOUND_ERROR


class TestImageArchitecture(unittest.TestCase):
    def setUp(self):
        self.architecture_path = join("tests", "res", "architecture.yml")

    def test_load_architecture(self):
        architecture, error = load_architecture(self.architecture_path)
        self.assertNotEqual(architecture, None)
        self.assertEqual(error, None)
        self.assertIsInstance(architecture, dict)

    def test_fail_load_architecture(self):
        missing_architecture_path = join("tests", "res", "missing.yml")
        architecture, error = load_architecture(missing_architecture_path)
        self.assertNotEqual(error, None)
        self.assertEqual(architecture, PATH_NOT_FOUND_ERROR)

    def test_architecture_owner(self):
        architecture, error = load_architecture(self.architecture_path)
        self.assertNotEqual(architecture, None)
        self.assertEqual(error, None)
        self.assertIsInstance(architecture, dict)
        self.assertIn("owner", architecture)
        self.assertIsInstance(architecture["owner"], str)
        self.assertGreater(len(architecture["owner"]), 0)
        self.assertEqual(architecture["owner"], "the-owner-name")

    def test_architecture_images_top(self):
        architecture, error = load_architecture(self.architecture_path)
        self.assertNotEqual(architecture, None)
        self.assertEqual(error, None)
        self.assertIsInstance(architecture, dict)
        self.assertIn("images", architecture)
        self.assertIsInstance(architecture["images"], dict)
        self.assertGreater(len(architecture["images"]), 0)
        self.assertEqual(len(architecture["images"]), 4)

    def test_architecture_images_items(self):
        architecture, error = load_architecture(self.architecture_path)
        self.assertNotEqual(architecture, None)
        self.assertEqual(error, None)
        self.assertIsInstance(architecture, dict)
        self.assertIn("images", architecture)
        self.assertIsInstance(architecture["images"], dict)
        self.assertGreater(len(architecture["images"]), 0)
        self.assertEqual(len(architecture["images"]), 4)
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

            self.assertIn("version", image_data)
            self.assertIsInstance(image_data["version"], (float, int))

            self.assertIn("format", image_data)
            self.assertIsInstance(image_data["format"], str)
            self.assertGreater(len(image_data["format"]), 0)
            self.assertIn(image_data["format"], ["raw", "qcow2"])

            self.assertIn("size", image_data)
            self.assertIsInstance(image_data["size"], str)
            self.assertGreater(len(image_data["size"]), 0)
