============
gen-vm-image
============

This package can be used for generating and configuring virtual machine images.

------------
Dependencies
------------

The dependencies required to use this package to generate virtual machine images
can be found in the `dep` directory for the supported distributions.

-----
Setup
-----

The `qemu-kvm` command might not be available in the default PATH.
This can be determined via the `which` command::

    which qemu-kvm

If the command is not available, the qemu-kvm might be in a different location that is not part of
your current PATH. In this case, you can create a symbolic link to the qemu-kvm command in a directory

An example of this could be::

    ln -s /usr/share/bash-completion/completions/qemu-kvm /usr/local/bin/qemu-kvm

The `gen-vm-image` command can be used to generate virtual machine images for the supported distributions.
To define which images should be generated, architecture.yml file should be created and defined beforehand.

-----------------------------
Build a Virtual Machine Image
-----------------------------

Before an image can be generated, you first have to create an architecture file that defines which images should be built.
What name this architecture file is given is not important, but it should be in YAML format and contain the following structure::

    owner: <string> # The owner of the image
    images: <key-value pair> # The images to be generated
        <image-name>:
            name: <string> # The name of the image
            version: <string> # The version of the image
            get_url: <string> # The URL to download the image from
            checksum:
                type: <string> # The type of checksum that should be used to validate the image. For valid types, see the supported algorithms `Here <https://docs.python.org/3/library/hashlib.html#hashlib.new>`_
                value: <string> # The checksum value that should be used to validate the image
            size: <string> # The size of the to be generated vm image disk, can use suffixes such as 'K', 'M', 'G', 'T'.

An example of such a file can be found in the `examples` directory.

Upon creating such a file, the `gen-vm-image` command can be used to generate the virtual machine image.
The totality of the command can be seen below::

        usage: gen-vm-image [-h] [--architecture-path ARCHITECTURE_PATH]
                                 [--image-output-path IMAGE_OUTPUT_PATH]
                                 [--generated-image-owner GENERATED_IMAGE_OWNER]
                                 [--generate-gocd-config]
                                 [--gocd-config-name GOCD_CONFIG_NAME]
                                 [--gocd-build-branch GOCD_BUILD_BRANCH]

        optional arguments:
        -h, --help            show this help message and exit
        --architecture-path ARCHITECTURE_PATH
                                The path to the architecture file that is used to configure the images to be built (default: architecture.yml)
        --image-output-path IMAGE_OUTPUT_PATH
                                The output path of the built image (default: generated-images/image.qcow2)
        --generated-image-owner GENERATED_IMAGE_OWNER
                                Set the uid owner of the configured image (default: qemu)
        --generate-gocd-config
                                Generate a GoCD config based on the architecture file (default: False)
        --gocd-config-name GOCD_CONFIG_NAME
                                Name of the generated gocd config file (default: 1.gocd.yml)
        --gocd-build-branch GOCD_BUILD_BRANCH
                                The branch that GoCD should use to build images (default: main)

When the ``gen-vm-image`` command is executed, the generated VM disk image will be placed in the ``--image-output-path`` directory.

If every default value is acceptable, the VM image can be built by simply running ``make build`` in the root directory of the project::

    make build


---------------------------------
Configure a Virtual Machine Image
---------------------------------

To configure a built VM image disk, the `configure-vm-image` command can be used.
This tool uses cloud-init to configure the image, and the configuration files for cloud-init should be defined beforehand.
Therefore, the tool requires that the to be configured image supports cloud-init, a list of various distributions cloud-init images can be found below.

- `Rocky <https://download.rockylinux.org/pub/rocky/>`_
- `Debian <https://cloud.debian.org/images/cloud/>`_
- `Ubuntu <https://cloud-images.ubuntu.com/>`_
- `Fedora <https://mirrors.dotsrc.org/fedora-enchilada/linux/releases/39/Cloud/>`_


The default location from where these are expected to be found can be discovered by running the command with the ``--help`` flag::

        usage: configure_image.py [-h] [--image-input-path IMAGE_INPUT_PATH]
                                       [---image-qemu-socket-path IMAGE_QEMU_SOCKET_PATH]
                                       [--config-user-data-path CONFIG_USER_DATA_PATH]
                                       [--config-meta-data-path CONFIG_META_DATA_PATH]
                                       [--config-vendor-data-path CONFIG_VENDOR_DATA_PATH]
                                       [--config-seed-output-path CONFIG_SEED_OUTPUT_PATH]
                                       [--qemu-cpu-model QEMU_CPU_MODEL]

        optional arguments:
        -h, --help            show this help message and exit
        --image-input-path IMAGE_INPUT_PATH
                                The path to the image that is to be configured (default: generated-images/image.qcow2)
        ---image-qemu-socket-path IMAGE_QEMU_SOCKET_PATH
                                The path to where the QEMU monitor socket should be placed which is used to send commands to the running image while it is being configured. (default:
                                generated-images/qemu-monitor-socket)
        --config-user-data-path CONFIG_USER_DATA_PATH
                                The path to the cloud-init user-data configuration file (default: cloud-init-config/user-data)
        --config-meta-data-path CONFIG_META_DATA_PATH
                                The path to the cloud-init meta-data configuration file (default: cloud-init-config/meta-data)
        --config-vendor-data-path CONFIG_VENDOR_DATA_PATH
                                The path to the cloud-init vendor-data configuration file (default: cloud-init-config/vendor-data)
        --config-seed-output-path CONFIG_SEED_OUTPUT_PATH
                                The path to the cloud-init output seed image file that is generated based on the data defined in the user-data, meta-data, and vendor-data configs
                                (default: image-config/seed.img)
        --qemu-cpu-model QEMU_CPU_MODEL
                                The default cpu model for configuring the image (default: host)

To configure the image, the `configure-vm-image` tool starts an instance of the image and sends commands to the running image via the QEMU monitor socket.
The configuration files for cloud-init should be defined beforehand and the tool requires that the to be configured image supports cloud-init.

To configure the built VM image disk with the default values, `make configure` can be run in the root directory of the project::

    make configure

------------------------
Putting it all togeather
------------------------

To build and configure a VM image disk with the default values, `make` can be run in the root directory of the project::

    make

The build and configure steps can be specialized via each of the respected Makefile parameters `BUILD_ARGS` and `CONFIGURE_ARGS`.
An example of this can be seen below::

    make BUILD_ARGS="--architecture-path examples/architecture.yml" CONFIGURE_ARGS="--image-input-path output-images/image.qcow2"
