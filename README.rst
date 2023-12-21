=============
saga-vm-images
=============

This repository holds the configurations for the SAGA virtual machine images
that is used for the VMs that hosts the users Jupyter Notebook Containers.

# Rocky 9 Linux cloud images can be found here: https://download.rockylinux.org/pub/rocky/9/images/x86_64/


------------
Dependencies
------------

These tools needs to be installed::

    apt install -y qemu-utils qemu-system-x86 qemu-system-gui

To run the command `cloud-localds` install the following::

    apt install -y  cloud-utils

The `qemu-kvm` command might not be available in the default PATH.
This can for example be::

    ln -s /usr/share/bash-completion/completions/qemu-kvm /usr/local/bin/qemu-kvm

