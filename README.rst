============
gen-vm-image
============

This package can be used for generating virtual machine images.

------------
Dependencies
------------

The dependencies required to use this package to generate virtual machine images
can be found in the ``dep`` directory for the supported distributions.

-----
Setup
-----

The ``qemu-kvm`` command might not be available in the default PATH.
This can be determined via the ``which`` command::

    which qemu-kvm

If the command is not available, the qemu-kvm might be in a different location that is not part of
your current PATH. In this case, you can create a symbolic link to the qemu-kvm command in a directory

An example of this could be::

    ln -s /usr/share/bash-completion/completions/qemu-kvm /usr/local/bin/qemu-kvm

The ``gen-vm-image`` command can be used to generate virtual machine images for the supported distributions.
To define which images should be generated, architecture.yml file should be created and defined beforehand.

-----------------------------
Build a Virtual Machine Image
-----------------------------

Before an image can be generated, you first have to create an architecture file that defines which images should be built.
What name this architecture file is given is not important, but it should be in YAML format and contain the following structure::

    owner: <string> # The owner of the image.
    images: <key-value pair> # The images to be generated.
      <image-name>:
        name: <string> # The name of the image.
        version: <string> # The version of the image.
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
                        [--generate-gocd-config]
                        [--gocd-config-name GOCD_CONFIG_NAME]
                        [--gocd-build-branch GOCD_BUILD_BRANCH]
                        [--verbose]
                        architecture_path

    positional arguments:
      architecture_path     The path to the architecture file that defines the images to build

    options:
      -h, --help            show this help message and exit
      --images-output-directory IMAGES_OUTPUT_DIRECTORY
                            The path to the output directory where the images will be saved (default: generated-images)
      --generate-gocd-config
                            Generate a GoCD config based on the architecture file (default: False)
      --gocd-config-name GOCD_CONFIG_NAME
                            Name of the generated gocd config file (default: 1.gocd.yml)
      --gocd-build-branch GOCD_BUILD_BRANCH
                            The branch that GoCD should use to build images (default: main)
      --verbose, -v         Print verbose output (default: False)

When the ``gen-vm-image`` command is executed, the generated VM disk image will be placed in the ``--image-output-path`` directory.

If every default value is acceptable, the VM image can be built by simply running ``make build`` in the root directory of the project::

    make build
