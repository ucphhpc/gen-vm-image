#!/bin/bash
# Copyright (C) 2024  The gen-vm-image Project by the Science HPC Center at UCPH
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

# To convert and check the cloud image
dnf install -y qemu-img

# genisoimage is required for filesystem=iso9660
dnf install -y genisoimage

# The emulator used to start and configure the image
dnf install -y qemu-kvm
# A link is missing
ln -s /usr/libexec/qemu-kvm /usr/bin/qemu-kvm

# Used to reset the image before it is deployed
dnf install -y /usr/bin/virt-sysprep
