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
import json
import sys
import os
from gen_vm_image._version import __version__
from gen_vm_image.common.defaults import (
    PACKAGE_NAME,
    GENERATED_IMAGE_DIR,
    TMP_DIR,
    CONSITENCY_SUPPPORTED_FORMATS,
)
from gen_vm_image.cli.common import error_print, to_str
from gen_vm_image.cli.return_codes import (
    PATH_NOT_FOUND_ERROR,
    PATH_NOT_FOUND_ERROR_MSG,
    PATH_CREATE_ERROR,
    PATH_CREATE_ERROR_MSG,
    MISSING_ATTRIBUTE_ERROR,
    MISSING_ATTRIBUTE_ERROR_MSG,
    INVALID_ATTRIBUTE_TYPE_ERROR,
    INVALID_ATTRIBUTE_TYPE_ERROR_MSG,
    CHECKSUM_ERROR,
    RESIZE_ERROR,
    RESIZE_ERROR_MSG,
    CHECK_ERROR,
    CHECK_ERROR_MSG,
    SUCCESS,
    JSON_DUMP_ERROR,
    JSON_DUMP_ERROR_MSG,
)
from gen_vm_image.architecture import load_architecture, correct_architecture_structure
from gen_vm_image.utils.io import exists, makedirs, hashsum
from gen_vm_image.utils.job import run
from gen_vm_image.utils.net import download_file


current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)


def qemu_img_call(action, args, format_output_str=True, verbose=False):
    command = ["qemu-img", action]
    if not verbose:
        command.append("-q")
    command.extend(args)

    result = run(command, format_output_str=format_output_str)
    if result["returncode"] != "0":
        return False, result["error"]
    return True, None


def create_image(path, size, image_format="qcow2", verbose=False):
    args = ["-f", image_format, path, size]
    result, msg = qemu_img_call("create", args, verbose=verbose)
    if not result:
        return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(path, msg)
    return result, None


def convert_image(
    input_path, output_path, input_format="qcow2", output_format="qcow2", verbose=False
):
    args = ["-f", input_format, "-O", output_format, input_path, output_path]
    result, msg = qemu_img_call("convert", args, verbose=verbose)
    if not result:
        return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(input_path, msg)
    return result, None


def resize_image(path, size, image_format="qcow2", verbose=False):
    result, msg = qemu_img_call(
        "resize", ["-f", image_format, path, size], verbose=verbose
    )
    if not result:
        return RESIZE_ERROR, RESIZE_ERROR_MSG.format(msg)
    return result, None


def amend_image(path, options, image_format="qcow2", verbose=False):
    args = ["-f", image_format, "-o", options, path]
    result, msg = qemu_img_call("amend", args, verbose=verbose)
    if not result:
        return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(path, msg)
    return result, None


def check_image(path, image_format="qcow2", verbose=False):
    if image_format not in CONSITENCY_SUPPPORTED_FORMATS:
        msg = "format: '{}' not supported for consistency check, only one of: {} is supported".format(
            image_format, CONSITENCY_SUPPPORTED_FORMATS
        )
        return False, msg
    result, msg = qemu_img_call("check", ["-f", image_format, path], verbose=verbose)
    if not result:
        return CHECK_ERROR, CHECK_ERROR_MSG.format(msg)
    return result, None


def build_architecture(
    architecture_path, images_output_directory, overwrite=False, verbose=False
):
    # Load the architecture file
    architecture, return_message = load_architecture(architecture_path)
    if not architecture:
        return architecture, return_message

    correct_architecture, correct_error_msg = correct_architecture_structure(
        architecture
    )
    if not correct_architecture:
        return correct_architecture, correct_error_msg

    # Create the destination directory where the images will be saved
    if not exists(images_output_directory):
        created, msg = makedirs(images_output_directory)
        if not created:
            return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(
                images_output_directory, msg
            )

    if "images" not in architecture:
        return MISSING_ATTRIBUTE_ERROR, MISSING_ATTRIBUTE_ERROR_MSG.format(
            "images", architecture
        )

    images = architecture.get("images")
    if not isinstance(images, dict):
        return INVALID_ATTRIBUTE_TYPE_ERROR, INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
            type(images), images, dict
        )

    # Generate the image configuration
    for build, build_data in images.items():
        vm_name = build_data["name"]
        vm_size = build_data["size"]
        # Optional version attribute for each image configuration
        vm_version = build_data.get("version", None)

        # Optional attributes for each image configuration
        vm_output_format = build_data.get("format", "qcow2")
        vm_input, vm_input_format = None, "qcow2"
        if "input" in build_data:
            vm_input = build_data["input"]
            if not isinstance(vm_input, str) and not isinstance(vm_input, dict):
                return (
                    INVALID_ATTRIBUTE_TYPE_ERROR,
                    INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                        type(vm_input), vm_input, "string or dictionary"
                    ),
                )

        if vm_version:
            vm_output_path = os.path.join(
                images_output_directory,
                "{}-{}.{}".format(vm_name, vm_version, vm_output_format),
            )
        else:
            vm_output_path = os.path.join(
                images_output_directory, "{}.{}".format(vm_name, vm_output_format)
            )

        if exists(vm_output_path):
            if verbose:
                print("The output image: {} already exists".format(vm_output_path))
            if not overwrite:
                if verbose:
                    print(
                        "Use the --overwrite flag to overwrite the existing image, continuing to the next image..."
                    )
                continue
            else:
                if verbose:
                    print("Overwriting the existing image: {}".format(vm_output_path))

        if vm_input:
            if isinstance(vm_input, dict):
                if "url" not in vm_input and "path" not in vm_input:
                    return MISSING_ATTRIBUTE_ERROR, MISSING_ATTRIBUTE_ERROR_MSG.format(
                        "'url' or 'path' must be in the architecture input section",
                        vm_input,
                    )

                if "url" in vm_input and "path" in vm_input:
                    return (
                        INVALID_ATTRIBUTE_TYPE_ERROR,
                        "Both 'url' and 'path' are defined in the architecture input section. Only one can be defined",
                    )

                if "url" in vm_input:
                    if not isinstance(vm_input["url"], str):
                        return (
                            INVALID_ATTRIBUTE_TYPE_ERROR,
                            INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                                type(vm_input["url"]), vm_input["url"], "string"
                            ),
                        )

                if "path" in vm_input:
                    if not isinstance(vm_input["path"], str):
                        return (
                            INVALID_ATTRIBUTE_TYPE_ERROR,
                            INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                                type(vm_input["path"]), vm_input["path"], "string"
                            ),
                        )

                # If a checksum is present, then validate that it is correctly structured
                vm_input_checksum = None
                if "checksum" in vm_input:
                    if not isinstance(vm_input["checksum"], dict):
                        return (
                            INVALID_ATTRIBUTE_TYPE_ERROR,
                            INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                                type(vm_input["checksum"]),
                                vm_input["checksum"],
                                "dictionary",
                            ),
                        )

                    required_checksum_attributes = ["type", "value"]
                    for attr in required_checksum_attributes:
                        if attr not in vm_input["checksum"]:
                            return (
                                MISSING_ATTRIBUTE_ERROR,
                                MISSING_ATTRIBUTE_ERROR_MSG.format(
                                    attr, vm_input["checksum"]
                                ),
                            )
                        if not isinstance(vm_input["checksum"][attr], str):
                            return (
                                INVALID_ATTRIBUTE_TYPE_ERROR,
                                INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                                    type(vm_input["checksum"][attr]),
                                    vm_input["checksum"][attr],
                                    "string",
                                ),
                            )
                    vm_input_checksum = vm_input["checksum"]

                if "url" in vm_input:
                    vm_input_url = vm_input["url"]
                    # Download the specified url and save it into
                    # a tmp directory.
                    # First prepare the temporary directory
                    # where the downloaded image will be prepared
                    if not exists(TMP_DIR):
                        created, msg = makedirs(TMP_DIR)
                        if not created:
                            return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(
                                TMP_DIR, msg
                            )

                    input_url_filename = vm_input_url.split("/")[-1]
                    input_vm_path = os.path.join(TMP_DIR, input_url_filename)
                    if not exists(input_vm_path):
                        if verbose:
                            print("Downloading image from: {}".format(vm_input_url))
                        download_file(vm_input_url, input_vm_path)
                elif "path" in vm_input:
                    input_vm_path = vm_input["path"]
                    if not exists(input_vm_path):
                        return PATH_NOT_FOUND_ERROR, PATH_NOT_FOUND_ERROR_MSG.format(
                            input_vm_path,
                            "the defined input path to the does not exist",
                        )

                if vm_input_checksum:
                    checksum_type = vm_input_checksum["type"]
                    checksum_value = vm_input_checksum["value"]
                    calculated_checksum = hashsum(
                        input_vm_path, algorithm=checksum_type
                    )
                    if not calculated_checksum:
                        return (
                            CHECKSUM_ERROR,
                            "Failed to calculate the checksum of the downloaded image",
                        )

                    if calculated_checksum != checksum_value:
                        return (
                            CHECKSUM_ERROR,
                            "The checksum of the downloaded image: {} does not match the expected checksum: {}".format(
                                calculated_checksum, checksum_value
                            ),
                        )
                    if verbose:
                        print(
                            "The calculated checksum: {} matches the defined checksum: {}".format(
                                calculated_checksum, checksum_value
                            )
                        )
            else:
                if not exists(vm_input):
                    return PATH_NOT_FOUND_ERROR, PATH_NOT_FOUND_ERROR_MSG.format(
                        vm_input, "the defined input path to the does not exist"
                    )

            converted_result, msg = convert_image(
                input_vm_path,
                vm_output_path,
                input_format=vm_input_format,
                output_format=vm_output_format,
                verbose=verbose,
            )
            if not converted_result:
                return converted_result, msg

            # Resize the vm disk image
            resized_result, resized_msg = resize_image(
                vm_output_path, vm_size, image_format=vm_output_format, verbose=verbose
            )
            if not resized_result:
                return resized_result, resized_msg
        else:
            # If no input is specified, then we assume that we are creating a new disc image
            create_image_result, msg = create_image(
                vm_output_path,
                vm_size,
                image_format=vm_output_format,
                verbose=verbose,
            )
            if not create_image_result:
                return create_image_result, msg
            else:
                if verbose:
                    print(
                        "Generated image at: {}".format(os.path.abspath(vm_output_path))
                    )

        # Amend to qcow2 version 3 which is required in RHEL 9 if the output format is
        # qcow2
        # TODO, validate that the image is a rhel based image
        if vm_output_format == "qcow2":
            amend_result, amend_msg = amend_image(
                vm_output_path, "compat=v3", verbose=verbose
            )
            if not amend_result:
                error_print(PATH_CREATE_ERROR_MSG.format(vm_output_path, amend_msg))

        if vm_output_format in CONSITENCY_SUPPPORTED_FORMATS:
            check_result, check_msg = check_image(
                vm_output_path,
                image_format=vm_output_format,
                verbose=verbose,
            )
            if not check_result:
                return check_result, check_msg
    return SUCCESS, "Successfully built the images"


def build_image_cli(commands):
    parser = commands.add_parser(
        "build-image", help="Build images based on an architecture file"
    )

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
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Print verbose output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=__version__,
        help="Print the version of the program",
    )


def main(args):
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    commands = parser.add_subparsers(title="COMMAND")
    build_image_cli(commands)
    parsed_args = parser.parse_args(args)

    architecture_path = parsed_args.architecture_path
    images_output_directory = parsed_args.images_output_directory
    overwrite = parsed_args.overwrite
    verbose = parsed_args.verbose

    return_code, message = build_architecture(
        architecture_path, images_output_directory, overwrite=overwrite, verbose=verbose
    )
    response = {}
    if return_code == SUCCESS:
        response["status"] = "success"
    else:
        response["status"] = "failed"
    response["msg"] = message
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


def cli():
    return main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
