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

PACKAGE_NAME = "gen-vm-image"
REPO_NAME = "gen-vm-image"
GOCD_GROUP = "bare_metal_vm_image"
GOCD_TEMPLATE = "bare_metal_vm_image"
GOCD_FORMAT_VERSION = 10
GO_REVISION_COMMIT_VAR = "GO_REVISION_SIF_VM_IMAGES"
CLOUD_CONFIG_DIR = "cloud-init-config"
IMAGE_CONFIG_DIR = "image-config"
GENERATED_IMAGE_DIR = "generated-images"
VM_DISK_DIR = "vmdisks"
TMP_DIR = "tmp"
CONSITENCY_SUPPPORTED_FORMATS = ["qcow2", "qed", "parallels", "vhdx", "vdi"]

# CLI
SINGLE = "single"
MULTIPLE = "multiple"

GEN_VM_IMAGE_CLI_STRUCTURE = [
    SINGLE,
    MULTIPLE,
]

DEFAULT_BUFFER_SIZE = 65536
