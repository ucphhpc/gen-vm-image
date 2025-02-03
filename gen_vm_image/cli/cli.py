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
from gen_vm_image.common.defaults import PACKAGE_NAME, GEN_VM_IMAGE_CLI_STRUCTURE
from gen_vm_image.common.codes import (
    SUCCESS,
    JSON_DUMP_ERROR,
    JSON_DUMP_ERROR_MSG,
)
from gen_vm_image.cli.common import error_print, to_str
from gen_vm_image.cli.helpers import extract_arguments, strip_argument_group_prefix


current_dir = os.path.realpath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)


def import_from_module(module_path, module_name, func_name):
    module = __import__(module_path, fromlist=[module_name])
    return getattr(module, func_name)


def add_cli_operations(
    parser,
    operation,
    module_cli_input_group_prefix="gen_vm_image.cli.input_groups",
    module_operation_prefix="gen_vm_image.cli.operations",
):
    operation_input_groups_func = import_from_module(
        "{}.{}".format(module_cli_input_group_prefix, operation),
        "{}".format(operation),
        "{}_groups".format(operation),
    )

    provider_groups = []
    argument_groups = []
    input_groups = operation_input_groups_func(parser)
    if not input_groups:
        raise RuntimeError(
            "No input groups were returned by the input group function: {}".format(
                operation_input_groups_func.func_name
            )
        )

    argument_groups = input_groups
    parser.set_defaults(
        func=cli_exec,
        module_path="{}.{}.build".format(module_operation_prefix, operation),
        module_name="build",
        func_name="{}_operation".format(operation),
        provider_groups=provider_groups,
        argument_groups=argument_groups,
    )


def cli_exec(arguments):
    # Actions determines which function to execute
    module_path = arguments.pop("module_path")
    module_name = arguments.pop("module_name")
    func_name = arguments.pop("func_name")

    if "positional_arguments" in arguments:
        positional_arguments = arguments.pop("positional_arguments")
    else:
        positional_arguments = []

    if "argument_groups" in arguments:
        argument_groups = arguments.pop("argument_groups")
    else:
        argument_groups = []

    func = import_from_module(module_path, module_name, func_name)
    if not func:
        return False, {}

    action_kwargs, _ = extract_arguments(arguments, argument_groups)
    action_kwargs = strip_argument_group_prefix(action_kwargs, argument_groups)

    action_args = positional_arguments
    if inspect.iscoroutinefunction(func):
        return asyncio.run(func(*action_args, **action_kwargs))
    return func(*action_args, **action_kwargs)


def add_base_cli_operations(parser):
    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=__version__,
        help="Print the version of the program",
    )


def add_build_image_cli_arguments(
    commands, module_cli_prefix="gen_vm_image.cli.operations"
):
    for command in GEN_VM_IMAGE_CLI_STRUCTURE:
        command_parser = commands.add_parser(command)
        add_cli_operations(command_parser, command)


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
        response["verbose_messages"] = result_dict.get("verbose_outputs", [])
        response["response"] = result_dict.get("msg", "")
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
