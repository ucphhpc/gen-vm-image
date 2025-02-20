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
      name                  The name of the image that will be generated.
      size                  The size of the image that will be generated.
      -i SINGLE_INPUT, --input SINGLE_INPUT
                            The path or url to the input image that the generated image should be based on.
      -if SINGLE_INPUT_FORMAT, --input-format SINGLE_INPUT_FORMAT
                            The format of the input image. Will dynamically try to determine the format if not provided.
      -ict SINGLE_INPUT_CHECKSUM_TYPE, --input-checksum-type SINGLE_INPUT_CHECKSUM_TYPE
                            The checksum type that should be used to validate the input image if set.
      -ic SINGLE_INPUT_CHECKSUM, --input-checksum SINGLE_INPUT_CHECKSUM
                            The checksum that should be used to validate the input image if set.
      -icbs SINGLE_INPUT_CHECKSUM_BUFFER_SIZE, --input-checksum-buffer-size SINGLE_INPUT_CHECKSUM_BUFFER_SIZE
                            The buffer size that is used to read the input image when calculating the checksum value.
      -icrb SINGLE_INPUT_CHECKSUM_READ_BYTES, --input-checksum-read-bytes SINGLE_INPUT_CHECKSUM_READ_BYTES
                            The amount of bytes that should be read from the input image to be used to calculate the expected checksum value.
      -od SINGLE_OUTPUT_DIRECTORY, --output-directory SINGLE_OUTPUT_DIRECTORY
                            The path to the output directory where the image will be saved.
      -of SINGLE_OUTPUT_FORMAT, --output-format SINGLE_OUTPUT_FORMAT
                            The format of the output image.
      -V SINGLE_VERSION, --version SINGLE_VERSION
                            The version of the image that is generated.
      --verbose, -v         Print verbose output.

Some simple examples for its usage can be seen below.

Basic Single Image Disk Example
-------------------------------

To generate a simple 20 GB disk image that is not based on any existing image, the following basic command can be used::

    gen-vm-image single basic-disk-image 20G

If no optional ``-od/--output-directory`` is set, the disk image will be generated in the default ``generated-image`` directory in your current working directory.
By default the ``gen-vm-image`` will generate the VMI with the `qcow2 <https://en.wikipedia.org/wiki/Qcow>`_ format. This can be changed via the ``-of/--output-format`` option.

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

When having to numerous many VMIs, it is useful to be able to do so in a single execution.
Additionally, when maintaining an infrastructure with many VMIs over time, it can be useful to have a structured definition that defines
this VMI infrastructure and is able to (re)produce it at will. The ``gen-vm-image`` tool allows you to do so with the ``multiple`` command::
The totality of the command can be seen below::

    gen-vm-image multiple -h
    usage: gen-vm-image multiple [-h] [-iod MULTIPLE_OUTPUT_DIRECTORY] [--overwrite] [--verbose] architecture_path

    options:
      -h, --help            show this help message and exit

    Generate multiple Virtual Machine Images:
      architecture_path     The path to the architecture file that defines the images that should be generated.
      -iod MULTIPLE_OUTPUT_DIRECTORY, --output-directory MULTIPLE_OUTPUT_DIRECTORY
                            The path to the output directory where the images will be saved.
      --overwrite           Whether the tool should overwrite existing image disks.
      --verbose, -v         Print verbose output.


The ``multiple`` command requires that you define and pass the path to an architecture file, that is a YAML formatted file that defines which VMIs that should be generated.
The expected structure of said architecture file can be seen below::

    owner: <string> # The owner of the image.
    images: <key-value pair> # The images to be generated.
      <image-name>:
        name: <string> # The name of the image.
        version: <string> # (Optional) The version of the image.
        size: <string> # The size of the to be generated vm image disk, can use suffixes such as 'K', 'M', 'G', 'T'.
        format: <string> # The format of the generated, cloud for instance be `raw` or `qcow2`.
        input: <dict> # (Optional) Input can be defined if the generated image should be based on a pre-existing image.
          path | url: <string> # A local filesystem path or URL to an image that should be used as the input image for the generated image.
          format: <string> # The format of the input image, could for instance be `raw` or `qcow2`.
          checksum: <dict> # A dictionary that defines the checksum that should be used to validate the input image.
            type: <string> # The type of checksum that should be used to validate the input image. For valid types, see the supported algorithms `Here <https://docs.python.org/3/library/hashlib.html#hashlib.new>`_
            value: <string> # The checksum value that should be used to validate the input image.

Practical examples of architecture files can be found in the ``examples`` directory.