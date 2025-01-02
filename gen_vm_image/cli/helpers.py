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


def strip_argument_prefix(arguments, prefix=""):
    return {k.replace(prefix, ""): v for k, v in arguments.items()}


def get_arguments(arguments, startswith=""):
    return {k: v for k, v in arguments.items() if k.startswith(startswith)}


def extract_arguments(arguments, argument_groups):
    found_kwargs, remaining_kwargs = {}, {}
    for argument_group in argument_groups:
        group_args = get_arguments(arguments, argument_group.lower())
        found_kwargs.update(group_args)
    remaining_kwargs = {
        k: v for k, v in arguments.items() if k not in found_kwargs and v
    }
    return found_kwargs, remaining_kwargs


def strip_argument_group_prefix(arguments, argument_groups):
    args = {}
    for argument_group in argument_groups:
        group_arguments = get_arguments(arguments, argument_group.lower())
        args.update(
            strip_argument_prefix(group_arguments, argument_group.lower() + "_")
        )
    return args
