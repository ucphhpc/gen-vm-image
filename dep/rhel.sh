#!/bin/bash

# genisoimage is required for filesystem=iso9660
dnf install -y genisoimage

# The emulator used to start and configure the image
dnf install -y qemu-img
