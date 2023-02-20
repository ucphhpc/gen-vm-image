#!/bin/bash

# The cloud-localds is used to generate the configuration image
# for cloud-init
dnf install -y cloud-utils

# The emulator used to start and configure the image
dnf install -y qemu-kvm

# Used to reset the image before it is deployed
dnf install /usr/bin/virt-sysprep
