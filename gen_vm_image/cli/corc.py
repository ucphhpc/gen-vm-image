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

from gen_vm_image.common.defaults import GENERATED_IMAGE_DIR
from gen_vm_image.cli.cli import add_build_image_cli_arguments
from gen_vm_image.image import generate_image


def corc_initializer_plugin_entrypoint(build_data):
    return generate_image(
        build_data["name"],
        build_data["size"],
        version=build_data.get("version", None),
        input=build_data.get("input", None),
        output_format=build_data.get("format", None),
        output_directory=build_data.get("output_directory", GENERATED_IMAGE_DIR),
        overwrite=build_data.get("overwrite", False),
        verbose=build_data.get("verbose", False),
    )


def gen_vm_image_cli(commands):
    add_build_image_cli_arguments(commands)
