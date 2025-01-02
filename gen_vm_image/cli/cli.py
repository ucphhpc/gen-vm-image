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


import argparse
import asyncio
import json
import inspect
import sys
import os
from gen_vm_image._version import __version__
from gen_vm_image.common.defaults import (
    PACKAGE_NAME,
    GENERATED_IMAGE_DIR,
    GEN_VM_IMAGE_CLI_STRUCTURE,
    SINGLE,
    MULTIPLE,
)
from gen_vm_image.common.codes import (
    SUCCESS,
    JSON_DUMP_ERROR,
    JSON_DUMP_ERROR_MSG,
)
from gen_vm_image.cli.common import error_print, to_str
from gen_vm_image.cli.actions import PositionalArgumentsAction


current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)


def cli_exec(arguments):
    # Actions determines which function to execute
    module_path = arguments.pop("module_path")
    module_name = arguments.pop("module_name")
    func_name = arguments.pop("func_name")

    if "positional_arguments" in arguments:
        positional_arguments = arguments.pop("positional_arguments")
    else:
        positional_arguments = []

    func = import_from_module(module_path, module_name, func_name)
    if not func:
        return False, {}

    if inspect.iscoroutinefunction(func):
        return asyncio.run(func(*positional_arguments, **arguments))
    return func(*positional_arguments, **arguments)


def add_base_cli_operations(parser):
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=__version__,
        help="Print the version of the program",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Print verbose output",
    )


def add_single_cli_operations(parser):
    parser.add_argument(
        "name",
        action=PositionalArgumentsAction,
        help="The name of the image to build",
    )
    parser.add_argument(
        "size",
        action=PositionalArgumentsAction,
        help="The size of the image to build",
    )
    parser.add_argument(
        "--input",
        help="The path of dictionary to the input image that the generated image should be based on",
    )
    parser.add_argument(
        "--output-directory",
        default=GENERATED_IMAGE_DIR,
        help="The path to the output directory where the image will be saved",
    )
    parser.add_argument(
        "--output-format",
        default="qcow2",
        help="The format of the output image",
    )
    parser.add_argument(
        "--version",
        help="The version of the image to build",
    )


def add_multiple_cli_arguments(parser):
    parser.add_argument(
        "architecture_path",
        help="The path to the architecture file that defines the images to build",
    )
    parser.add_argument(
        "--images-output-directory",
        default=GENERATED_IMAGE_DIR,
        help="The path to the output directory where the images will be saved",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Whether the tool should overwrite existing image disks",
    )


def add_build_image_cli_arguments(commands):
    for command in GEN_VM_IMAGE_CLI_STRUCTURE:
        if command == SINGLE:
            parser = commands.add_parser(
                SINGLE,
                help="Build a single image",
            )
            add_single_cli_operations(parser)
        if command == MULTIPLE:
            parser = commands.add_parser(
                MULTIPLE,
                help="Build multiple images",
            )
            add_multiple_cli_arguments(parser)
        parser.set_defaults(func=cli_exec)


def main(args):
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    # Add the basic CLI functions
    add_base_cli_operations(parser)
    # Add the build image CLI arguments
    commands = parser.add_subparsers(title="COMMAND")
    add_build_image_cli_arguments(commands)

    parsed_args = parser.parse_args(args)
    # Convert to a dictionary
    arguments = vars(parsed_args)

    if "func" in arguments:
        func = arguments.pop("func")
        return_code, result_dict = func(arguments)

        response = {}
        if return_code == SUCCESS:
            response["status"] = "success"
        else:
            response["status"] = "failed"
        if "verbose" in arguments:
            response["outputs"] = result_dict.get("verbose_outputs", [])
        response["msg"] = result_dict.get("msg", "")
        response["return_code"] = return_code

        try:
            output = json.dumps(response, indent=4, sort_keys=True, default=to_str)
        except Exception as err:
            error_print(JSON_DUMP_ERROR_MSG.format(err))
            return JSON_DUMP_ERROR
        if return_code == SUCCESS:
            print(output)
        else:
            error_print(output)
        return return_code
    return SUCCESS


def cli():
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
