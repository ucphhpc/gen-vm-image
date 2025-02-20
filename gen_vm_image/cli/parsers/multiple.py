# Copyright (C) 2025  The gen-vm-image Project by the Science HPC Center at UCPH
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

from gen_vm_image.common.defaults import MULTIPLE, GENERATED_IMAGE_DIR
from gen_vm_image.cli.parsers.actions import PositionalArgumentsAction


def multiple_group(parser):
    generate_multiple_group = parser.add_argument_group(
        title="Generate multiple Virtual Machine Images"
    )

    generate_multiple_group.add_argument(
        "architecture_path",
        action=PositionalArgumentsAction,
        help="The path to the architecture file that defines the images that should be generated.",
    )
    generate_multiple_group.add_argument(
        "-od",
        "--output-directory",
        dest="{}_output_directory".format(MULTIPLE),
        default=GENERATED_IMAGE_DIR,
        help="The path to the output directory where the images will be saved.",
    )
    generate_multiple_group.add_argument(
        "--overwrite",
        dest="{}_overwrite".format(MULTIPLE),
        action="store_true",
        default=False,
        help="Whether the tool should overwrite existing image disks.",
    )
    generate_multiple_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        dest="{}_verbose".format(MULTIPLE),
        default=False,
        help="Print verbose output.",
    )
