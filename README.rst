============
gen-vm-image
============

.. image:: https://img.shields.io/pypi/pyversions/gen-vm-image.svg
    :target: https://img.shields.io/pypi/pyversions/gen-vm-image
.. image:: https://badge.fury.io/py/gen-vm-image.svg
    :target: https://badge.fury.io/py/gen-vm-image

This package can be used for generating virtual machine images.

------------
Dependencies
------------

The dependencies required to use this package to generate virtual machine images
can be found in the ``dep`` directory for the supported distributions.

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

-----------------------------
Build a Virtual Machine Image
-----------------------------

Before an image can be generated, you first have to create an architecture file that defines which images should be built.
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
                        [--generate-gocd-config]
                        [--gocd-config-name GOCD_CONFIG_NAME]
                        [--gocd-build-branch GOCD_BUILD_BRANCH]
                        [--verbose]
                        architecture_path

    positional arguments:
      architecture_path     The path to the architecture file that defines the images to build

    optional arguments:
      -h, --help            show this help message and exit
      --images-output-directory IMAGES_OUTPUT_DIRECTORY
                            The path to the output directory where the images will be saved (default: generated-images)
      --overwrite           Whether the tool should overwrite existing image disks (default: False)
      --generate-gocd-config
                            Generate a GoCD config based on the architecture file (default: False)
      --gocd-config-name GOCD_CONFIG_NAME
                            Name of the generated gocd config file (default: 1.gocd.yml)
      --gocd-build-branch GOCD_BUILD_BRANCH
                            The branch that GoCD should use to build images (default: main)
      --verbose, -v         Print verbose output (default: False)

In summation, when the ``gen-vm-image path/to/architecture.yml`` command is executed,
the specified images will be generated in the ``--image-output-path`` directory.
