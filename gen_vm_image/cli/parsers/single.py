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

from gen_vm_image.common.defaults import (
    SINGLE,
    GENERATED_IMAGE_DIR,
    DEFAULT_BUFFER_SIZE,
)
from gen_vm_image.cli.parsers.actions import PositionalArgumentsAction


def single_group(parser):
    generate_single_group = parser.add_argument_group(
        title="Generate a single Virtual Machine Image"
    )

    generate_single_group.add_argument(
        "name",
        action=PositionalArgumentsAction,
        type=str,
        help="The name of the image that will be generated.",
    )
    generate_single_group.add_argument(
        "size",
        action=PositionalArgumentsAction,
        type=str,
        help="The size of the image that will be generated.",
    )
    generate_single_group.add_argument(
        "-i",
        "--input",
        dest="{}_input".format(SINGLE),
        help="The path or url to the input image that the generated image should be based on.",
    )
    generate_single_group.add_argument(
        "-if",
        "--input-format",
        dest="{}_input_format".format(SINGLE),
        default=None,
        help="The format of the input image. Will dynamically try to determine the format if not provided.",
    )
    generate_single_group.add_argument(
        "-ict",
        "--input-checksum-type",
        dest="{}_input_checksum_type".format(SINGLE),
        default=None,
        help="The checksum type that should be used to validate the input image if set.",
    )
    generate_single_group.add_argument(
        "-ic",
        "--input-checksum",
        dest="{}_input_checksum".format(SINGLE),
        default=None,
        help="The checksum that should be used to validate the input image if set.",
    )
    generate_single_group.add_argument(
        "-icbs",
        "--input-checksum-buffer-size",
        dest="{}_input_checksum_buffer_size".format(SINGLE),
        default=DEFAULT_BUFFER_SIZE,
        help="The buffer size that is used to read the input image when calculating the checksum value.",
    )
    generate_single_group.add_argument(
        "-icrb",
        "--input-checksum-read-bytes",
        dest="{}_input_checksum_read_bytes".format(SINGLE),
        default=None,
        type=int,
        help="The amount of bytes that should be read from the input image to be used to calculate the expected checksum value.",
    )
    generate_single_group.add_argument(
        "-od",
        "--output-directory",
        dest="{}_output_directory".format(SINGLE),
        default=GENERATED_IMAGE_DIR,
        help="The path to the output directory where the image will be saved.",
    )
    generate_single_group.add_argument(
        "-of",
        "--output-format",
        dest="{}_output_format".format(SINGLE),
        default="qcow2",
        help="The format of the output image.",
    )
    generate_single_group.add_argument(
        "-V",
        "--version",
        dest="{}_version".format(SINGLE),
        help="The version of the image that is generated.",
    )
    generate_single_group.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        dest="{}_verbose".format(SINGLE),
        default=False,
        help="Print verbose output.",
    )
