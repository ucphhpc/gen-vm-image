#!/bin/bash

# genisoimage is required for filesystem=iso9660
apt install -y genisoimage

# The emulator used to start and configure the image
apt install -y kvm

# virt-sysprep is provided by libguestfs-tools
apt install -y libguestfs-tools