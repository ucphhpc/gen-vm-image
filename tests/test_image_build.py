import unittest
import random
import wget
from gen_vm_image.utils.io import join, find, remove, exists, makedirs
from gen_vm_image.architecture import load_architecture
from gen_vm_image.cli.build_image import create_image, convert_image, resize_image


class TestImageBuild(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # https://cloud.debian.org/images/cloud/bookworm/latest/input_path_image-genericcloud-amd64.qcow2
        # Download the test image for the path input test
        cls.input_path_url = "https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-genericcloud-amd64.qcow2"
        cls.test_tmp_directory = join("tests", "tmp")
        cls.test_res_directory = join("tests", "res")
        if not exists(cls.test_tmp_directory):
            assert makedirs(cls.test_tmp_directory)
        cls.input_image_path = join(cls.test_tmp_directory, "debian-12.qcow2")
        wget.download(cls.input_path_url, out=cls.input_image_path)
        assert exists(cls.input_image_path)

        cls.architecture_path = join(cls.test_res_directory, "architecture.yml")
        cls.architecture, error = load_architecture(cls.architecture_path)
        assert cls.architecture is not None
        assert error is None
        assert isinstance(cls.architecture, dict)

    @classmethod
    def tearDownClass(cls):
        # Remove the downloaded test image
        if exists(cls.input_image_path):
            assert remove(cls.input_image_path)[0]
        if exists(cls.test_tmp_directory):
            assert remove(cls.test_tmp_directory, recursive=True)[0]

    def setUp(self):
        self.seed = str(random.random())[2:10]

    def tearDown(self):
        # Remove every seed file
        regex_name = ".*{}.*".format(self.seed)
        seed_files = find(self.test_tmp_directory, regex_name)
        for seed_file in seed_files:
            if exists(seed_file):
                self.assertTrue(remove(seed_file)[0])

    def test_create_image_qcow_1(self):
        image_1 = self.architecture["images"]["image-1"]
        self.assertEqual(image_1["name"], "test-image-1")
        image_1_name = "{}-{}".format(image_1["name"], self.seed)
        self.assertEqual(image_1["version"], 9.4)
        self.assertEqual(image_1["format"], "qcow2")
        self.assertEqual(image_1["size"], "10G")

        new_image_path = join(
            self.test_tmp_directory, "{}.{}".format(image_1_name, image_1["format"])
        )
        result, msg = create_image(
            new_image_path,
            image_1["size"],
            image_format=image_1["format"],
        )
        self.assertTrue(result)
        self.assertIsNone(msg)

    def test_create_image_raw_2(self):
        image_2 = self.architecture["images"]["image-2"]
        self.assertEqual(image_2["name"], "test-image-2")
        image_2_name = "{}-{}".format(image_2["name"], self.seed)
        self.assertEqual(image_2["version"], 9.4)
        self.assertEqual(image_2["format"], "raw")
        self.assertEqual(image_2["size"], "10G")

        new_image_path = join(
            self.test_tmp_directory, "{}.{}".format(image_2_name, image_2["format"])
        )
        result, msg = create_image(
            new_image_path,
            image_2["size"],
            image_format=image_2["format"],
        )
        self.assertTrue(result)
        self.assertIsNone(msg)

    def test_image_path_input(self):
        input_path_image = self.architecture["images"]["input_path_image"]
        self.assertEqual(input_path_image["name"], "input-path-image")
        self.assertEqual(input_path_image["version"], 12)
        self.assertEqual(input_path_image["format"], "qcow2")
        self.assertEqual(input_path_image["size"], "20G")

        self.assertIn("input", input_path_image)
        self.assertIsInstance(input_path_image["input"], dict)
        self.assertIn("path", input_path_image["input"])
        self.assertIn("format", input_path_image["input"])

        self.assertEqual(input_path_image["input"]["path"], self.input_image_path)
        self.assertEqual(input_path_image["input"]["format"], "qcow2")
        self.assertTrue(exists(self.input_image_path))

        output_path = join(
            self.test_tmp_directory,
            "{}-{}.{}".format(
                input_path_image["name"], self.seed, input_path_image["format"]
            ),
        )

        concert_result, convert_msg = convert_image(
            input_path_image["input"]["path"],
            output_path,
            input_format=input_path_image["input"]["format"],
            output_format=input_path_image["format"],
        )
        self.assertTrue(concert_result)
        self.assertIsNone(convert_msg)
        self.assertTrue(exists(output_path))

        resize_result, resize_msg = resize_image(
            output_path,
            input_path_image["size"],
            image_format=input_path_image["format"],
        )
        self.assertTrue(resize_result)
        self.assertIsNone(resize_msg)
        # TODO, validate that the size of the output image is correct

    def test_convert_image_format(self):
        convert_image_dict = self.architecture["images"]["convert_input_image_format"]
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
            self.test_tmp_directory,
            "{}-{}.{}".format(
                convert_image_dict["name"], self.seed, convert_image_dict["format"]
            ),
        )

        result, msg = convert_image(
            convert_image_dict["input"]["path"],
            output_path,
            input_format=convert_image_dict["input"]["format"],
            output_format=convert_image_dict["format"],
        )
        self.assertTrue(result)
        self.assertIsNone(msg)
        self.assertTrue(exists(output_path))
        # TODO, validate that the output image is of the correct size and format

    def test_build_with_no_version(self):
        image_no_version = self.architecture["images"]["non_version_image_test"]
        self.assertEqual(image_no_version["name"], "non-version-image")
        self.assertEqual(image_no_version["format"], "raw")
        self.assertEqual(image_no_version["size"], "10G")

        new_image_path = join(
            self.test_tmp_directory,
            "{}-{}.{}".format(
                image_no_version["name"], self.seed, image_no_version["format"]
            ),
        )
        result, msg = create_image(
            new_image_path,
            image_no_version["size"],
            image_format=image_no_version["format"],
        )
        self.assertTrue(result)
        self.assertIsNone(msg)
        self.assertTrue(exists(new_image_path))
