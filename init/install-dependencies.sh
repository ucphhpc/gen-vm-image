#!/bin/bash

# To convert and check the cloud image
dnf install -y qemu-img

# The cloud-localds is used to generate the configuration image
# for cloud-init
dnf install -y cloud-utils --enablerepo devel
# genisoimage is required for filesystem=iso9660
dnf install -y genisoimage

# The emulator used to start and configure the image
dnf install -y qemu-kvm
# A link is missing
ln -s /usr/libexec/qemu-kvm /usr/bin/qemu-kvm

# Used to reset the image before it is deployed
dnf install -y /usr/bin/virt-sysprep
