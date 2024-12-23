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
from gen_vm_image.common.codes import SUCCESS
from gen_vm_image.cli.build_image import (
    add_build_image_cli_arguments,
    build_architecture,
)


def build_image_cli(commands):
    parser = commands.add_parser(
        "build-image",
        help="Build the images defined in an architecture file.",
    )
    add_build_image_cli_arguments(parser)
    parser.set_defaults(func=corc_build_image_cli_exec)


def corc_build_image_cli_exec(args):
    architecture_path = args.get("architecture_path")
    images_output_directory = args.get("images_output_directory", GENERATED_IMAGE_DIR)
    overwrite = args.get("overwrite", False)
    verbose = args.get("verbose", False)

    return_code, result_dict = build_architecture(
        architecture_path,
        images_output_directory=images_output_directory,
        overwrite=overwrite,
        verbose=verbose,
    )

    if return_code == SUCCESS:
        return True, result_dict
    return False, result_dict
