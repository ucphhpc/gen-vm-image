============
gen-vm-image
============

.. image:: https://img.shields.io/pypi/pyversions/gen-vm-image.svg
    :target: https://img.shields.io/pypi/pyversions/gen-vm-image
.. image:: https://badge.fury.io/py/gen-vm-image.svg
    :target: https://badge.fury.io/py/gen-vm-image

This package can be used for generating Virtual Machine Image(s) (VMI)s.
The ``gen-vm-image`` tool can also be used as an initializer plugin for `corc <https://github.com/rasmunk/corc>`_

------------
Dependencies
------------

The dependencies required to use this package to generate VMIs can be found in the ``dep`` directory for the supported distributions.

------------
Installation
------------

The current stable release version ``gen-vm-image`` tool can be installed directly from pypi via::

    pip install gen-vm-image

Alternatively, you can install the current development version by firstly cloning the repository::

  git clone https://github.com/ucphhpc/gen-vm-image.git

Then, secondly installing the ``gen-vm-image`` tool either in its own virtual environment::

  cd gen-vm-image
  make install

or systemwide::

    cd gen-vm-image
    make install PYTHON=path/to/your/systemwide/python

-----------------------------------
Generating Virtual Machine Image(s)
-----------------------------------

The ``gen-vm-image`` tool provides two distinct methods for generating VMIs, namely the ``single`` and ``multiple`` commands for generating image(s).
Either of these commands can be selected via the ``gen-vm-image`` CLI::

    gen-vm-image --help
    usage: gen-vm-image [-h] [--version] {single,multiple} ...

    options:
      -h, --help         show this help message and exit
      --version, -V      Print the version of the program

    COMMAND:
      {single,multiple}


Single Image
============

The ``single`` CLI command provides the most straigthforward method for quickly generating a single VMI.
Information on the various options for the ``single`` command can also be displayed via the ``--help`` option.
As indicated by the help output, ``single`` command only requires two positional arguments::

    usage: gen-vm-image single
                        [-h]
                        [-i SINGLE_INPUT]
                        [-if SINGLE_INPUT_FORMAT]
                        [-ict SINGLE_INPUT_CHECKSUM_TYPE]
                        [-ic SINGLE_INPUT_CHECKSUM]
                        [-icbs SINGLE_INPUT_CHECKSUM_BUFFER_SIZE]
                        [-icrb SINGLE_INPUT_CHECKSUM_READ_BYTES]
                        [-od SINGLE_OUTPUT_DIRECTORY]
                        [-of SINGLE_OUTPUT_FORMAT]
                        [-V SINGLE_VERSION]
                        [--verbose]
                        name
                        size

    options:
      -h, --help            show this help message and exit

    Generate a single Virtual Machine Image:
      name                  The name of the image that will be generated
      size                  The size of the image that will be generated
      -i SINGLE_INPUT, --input SINGLE_INPUT
                            The path or url to the input image that the generated image should be based on
      -if SINGLE_INPUT_FORMAT, --input-format SINGLE_INPUT_FORMAT
                            The format of the input image. Will dynamically try to determine the format if not provided
      -ict SINGLE_INPUT_CHECKSUM_TYPE, --input-checksum-type SINGLE_INPUT_CHECKSUM_TYPE
                            The checksum type that should be used to validate the input image if set.
      -ic SINGLE_INPUT_CHECKSUM, --input-checksum SINGLE_INPUT_CHECKSUM
                            The checksum that should be used to validate the input image if set.
      -icbs SINGLE_INPUT_CHECKSUM_BUFFER_SIZE, --input-checksum-buffer-size SINGLE_INPUT_CHECKSUM_BUFFER_SIZE
                            The buffer size that is used to read the input image when calculating the checksum value
      -icrb SINGLE_INPUT_CHECKSUM_READ_BYTES, --input-checksum-read-bytes SINGLE_INPUT_CHECKSUM_READ_BYTES
                            The amount of bytes that should be read from the input image to be used to calculate the expected checksum value
      -od SINGLE_OUTPUT_DIRECTORY, --output-directory SINGLE_OUTPUT_DIRECTORY
                            The path to the output directory where the image will be saved
      -of SINGLE_OUTPUT_FORMAT, --output-format SINGLE_OUTPUT_FORMAT
                            The format of the output image
      -V SINGLE_VERSION, --version SINGLE_VERSION
                            The version of the image to build
      --verbose, -v         Print verbose output

Some simple examples for its usage can be seen below.


Basic Single Image Disk Example
-------------------------------

To generate a simple 20 GB disk image that is not based on any existing image, the following basic command can be used::

    gen-vm-image single basic-disk-image 20G

If no optional ``-od/--output-directory`` is set, the disk image will be generated in the default ``generated-image`` directory in your current working directory.


Image Based on an Existing Image
--------------------------------

The following example will generate a 10 GB GenericCloud single disk image based on the Debian 12 distribution::

    gen-vm-image single basic-image 10G -i https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2

Verify Checksum of Downloaded Image
-----------------------------------

When generating a VMI based on an existing image that is downloaded, it is recommended that as part of the generation with
``gen-vm-image`` that the downloaded image checksum is verified.

For instance with the `Image Based on an Existing Image` example, the expected checksum of the downloaded image
can be found at https://cloud.debian.org/images/cloud/bookworm/latest/SHA512SUMS::

    gen-vm-image single basic-image 10G --input-checksum-type sha512 --input-checksum <expected_sha512_checksum_of_the_downloaded_image> -i https://cloud.debian.org/images/cloud/bookworm/latest/debian-12-generic-amd64.qcow2


Multiple Images
===============

To generate multiple images in one execution, you first have to create an architecture file that defines which images should be built.
What name this architecture file is given is not important, but it should be in YAML format and contain the following structure::

    owner: <string> # The owner of the image.
    images: <key-value pair> # The images to be generated.
      <image-name>:
        name: <string> # The name of the image.
        version: <string> # (Optional) The version of the image.
        size: <string> # The size of the to be generated vm image disk, can use suffixes such as 'K', 'M', 'G', 'T'.
        input: <dict> # Input can be defined if the generated image should be based on a pre-existing image.
          url: <string> # An URL to an image that should be used as the input image for the generated image.
          format: <string> # The format of the input image, could for instance be `raw` or `qcow2`.
          checksum: <dict> # A dictionary that defines the checksum that should be used to validate the input image.
            type: <string> # The type of checksum that should be used to validate the image. For valid types, see the supported algorithms `Here <https://docs.python.org/3/library/hashlib.html#hashlib.new>`_
            value: <string> # The checksum value that should be used to validate the image.


An example of such a file can be found in the ``examples`` directory.

Upon creating such a file, the `gen-vm-image` command can be used to generate the virtual machine image.
The totality of the command can be seen below::

    usage: gen-vm-image [-h]
                        [--images-output-directory IMAGES_OUTPUT_DIRECTORY]
                        [--overwrite]
                        [--verbose]
                        [--version]
                        architecture_path

    positional arguments:
      architecture_path     The path to the architecture file that defines the images to build

    options:
      -h, --help            show this help message and exit
      --images-output-directory IMAGES_OUTPUT_DIRECTORY
                            The path to the output directory where the images will be saved (default: generated-images)
      --overwrite           Whether the tool should overwrite existing image disks (default: False)
      --verbose, -v         Print verbose output (default: False)
      --version             Print the version of the program

In summation, when the ``gen-vm-image path/to/architecture.yml`` command is executed,
the specified images will be generated in the ``--image-output-path`` directory.
