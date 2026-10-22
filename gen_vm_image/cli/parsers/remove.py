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

from gen_vm_image.cli.parsers.actions import PositionalArgumentsAction
from gen_vm_image.common.defaults import GENERATED_IMAGE_DIR, REMOVE


def remove_group(parser):
    remove_group = parser.add_argument_group(title="Remove a Virtual Machine Image")

    remove_group.add_argument(
        "path",
        action=PositionalArgumentsAction,
        type=str,
        help="The path to the image that should be removed.",
    )
    remove_group.add_argument(
        "-sd",
        "--source-directory",
        dest="{}_source_directory".format(REMOVE),
        default=GENERATED_IMAGE_DIR,
        help="The source directory where the image is located. Used when the path is relative.",
    )
    remove_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        dest="{}_verbose".format(REMOVE),
        default=False,
        help="Print verbose output.",
    )
