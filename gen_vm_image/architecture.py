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

import os
import yaml
from gen_vm_image.common.defaults import GENERATED_IMAGE_DIR, DEFAULT_BUFFER_SIZE
from gen_vm_image.common.codes import (
    PATH_CREATE_ERROR,
    PATH_CREATE_ERROR_MSG,
    PATH_NOT_FOUND_ERROR,
    PATH_NOT_FOUND_ERROR_MSG,
    PATH_LOAD_ERROR,
    PATH_LOAD_ERROR_MSG,
    INVALID_ATTRIBUTE_TYPE_ERROR,
    INVALID_ATTRIBUTE_TYPE_ERROR_MSG,
    MISSING_ATTRIBUTE_ERROR,
    MISSING_ATTRIBUTE_ERROR_MSG,
    SUCCESS,
)
from gen_vm_image.utils.io import exists, load, makedirs
from gen_vm_image.image import generate_image


def load_architecture(architecture_path):
    response = {}
    if not exists(architecture_path):
        response["error_code"] = PATH_NOT_FOUND_ERROR
        response["msg"] = PATH_NOT_FOUND_ERROR_MSG.format(
            architecture_path, "Failed to find the architecture file."
        )
        return False, response

    architecture = load(architecture_path, handler=yaml, Loader=yaml.FullLoader)
    if not architecture:
        response["error_code"] = PATH_LOAD_ERROR
        response["msg"] = PATH_LOAD_ERROR_MSG.format(
            architecture_path, "Failed to load the architecture file."
        )
        return False, response
    response["architecture"] = architecture
    return True, response


def correct_architecture_structure(architecture):
    response = {}
    owner = architecture.get("owner", None)
    if not owner:
        response["error_code"] = MISSING_ATTRIBUTE_ERROR
        response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format("owner", architecture)
        return False, response

    images = architecture.get("images", None)
    if not images:
        response["error_code"] = MISSING_ATTRIBUTE_ERROR
        response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format("images", architecture)
        return False, response

    required_attributes = ["name", "size"]
    for image_name, image_data in images.items():
        for attribute in required_attributes:
            if attribute not in image_data:
                response["error_code"] = MISSING_ATTRIBUTE_ERROR
                response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format(
                    attribute, image_name
                )
                return False, response
    return True, response


def validate_input(input_data):
    response = {}
    if not isinstance(input_data, str) and not isinstance(input_data, dict):
        response["error_code"] = INVALID_ATTRIBUTE_TYPE_ERROR
        response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
            type(input_data),
            input_data,
            "image input must be a string or dictionary",
        )
        return False, response

    if isinstance(input_data, dict):
        if "url" not in input_data and "path" not in input_data:
            response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format(
                "'url' or 'path' must be in the architecture input section"
            )

        if "url" in input_data and "path" in input_data:
            response["error_code"] = INVALID_ATTRIBUTE_TYPE_ERROR
            response["msg"] = (
                "Both 'url' and 'path' are defined in the architecture input section. Only one can be defined"
            )
            return False, response

        if "url" in input_data:
            if not isinstance(input_data["url"], str):
                response["error_code"] = INVALID_ATTRIBUTE_TYPE_ERROR
                response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                    type(input_data["url"]), input_data["url"], "string"
                )
                return False, response

        if "path" in input_data:
            if not isinstance(input_data["path"], str):
                response["error_code"] = INVALID_ATTRIBUTE_TYPE_ERROR
                response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                    type(input_data["path"]), input_data["path"], "string"
                )
                return False, response

        if "format" in input_data:
            vm_input_format = input_data["format"]
            if not isinstance(vm_input_format, str):
                response["error_code"] = INVALID_ATTRIBUTE_TYPE_ERROR
                response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                    type(vm_input_format), vm_input_format, "string"
                )
                return False, response

        # If a checksum is present, then validate that it is correctly structured
        if "checksum" in input_data:
            if not isinstance(input_data["checksum"], dict):
                response["error_code"] = INVALID_ATTRIBUTE_TYPE_ERROR
                response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                    type(input_data["checksum"]),
                    input_data["checksum"],
                    "dictionary",
                )
                return False, response

            required_checksum_attributes = ["type", "value"]
            for attr in required_checksum_attributes:
                if attr not in input_data["checksum"]:
                    response["error_code"] = MISSING_ATTRIBUTE_ERROR
                    response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format(
                        attr, input_data["checksum"]
                    )
                    return False, response
                if not isinstance(input_data["checksum"][attr], str):
                    response["error_code"] = INVALID_ATTRIBUTE_TYPE_ERROR
                    response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                        type(input_data["checksum"][attr]),
                        input_data["checksum"][attr],
                        "string",
                    )
                    return False, response
    return True, response


def prepare_input_kwargs(input_data):
    input_kwargs = {}

    checksum = input_data.get("checksum", None)
    if checksum:
        input_kwargs["input_checksum_type"] = checksum.get("type", None)
        input_kwargs["input_checksum"] = checksum.get("value", None)
        input_kwargs["input_checksum_buffer_size"] = checksum.get(
            "buffer_size", DEFAULT_BUFFER_SIZE
        )
        input_kwargs["input_checksum_read_bytes"] = checksum.get("read_bytes", None)

    if "path" in input_data:
        input_kwargs["input"] = input_data.get("path", None)
    if "url" in input_data:
        input_kwargs["input"] = input_data.get("url", None)
    if "format" in input_data:
        input_kwargs["input_format"] = input_data.get("format", None)
    return input_kwargs


async def build_architecture(
    architecture_path,
    output_directory=GENERATED_IMAGE_DIR,
    overwrite=False,
    verbose=False,
):
    response = {"verbose_outputs": []}
    # Load the architecture file
    architecture_loaded, architecture_response = load_architecture(architecture_path)
    if not architecture_loaded:
        response["msg"] = architecture_response["msg"]
        return architecture_response["error_code"], response

    architecture = architecture_response["architecture"]
    correct_architecture, correct_response = correct_architecture_structure(
        architecture
    )
    if not correct_architecture:
        response["msg"] = correct_response["msg"]
        return correct_response["error_code"], response

    # Create the destination directory where the images will be saved
    if not exists(output_directory):
        created = makedirs(output_directory)
        if not created:
            response["msg"] = PATH_CREATE_ERROR_MSG.format(
                output_directory, "Failed to create the images output directory"
            )
            return PATH_CREATE_ERROR, response

    if "images" not in architecture:
        response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format("images", architecture)
        return MISSING_ATTRIBUTE_ERROR, response

    images = architecture.get("images")
    if not isinstance(images, dict):
        response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
            type(images), images, dict
        )
        return INVALID_ATTRIBUTE_TYPE_ERROR, response

    # Generate the image configuration
    for _, build_data in images.items():
        generate_image_kwargs = {}

        input_ = build_data.get("input", None)
        if input_:
            correct_input, correct_input_response = validate_input(input_)
            if not correct_input:
                return (
                    correct_input_response["error_code"],
                    correct_input_response["msg"],
                )

            if isinstance(input_, dict):
                generate_image_kwargs.update(**prepare_input_kwargs(input_))

        generate_image_kwargs["output_directory"] = output_directory
        generate_image_kwargs["output_format"] = build_data.get("format", "qcow2")
        generate_image_kwargs["version"] = build_data.get("version", None)

        build_return_code, build_response = await generate_image(
            build_data["name"],
            build_data["size"],
            **generate_image_kwargs,
            verbose=verbose,
        )

        if build_return_code != SUCCESS:
            response["verbose_outputs"] = build_response.get("verbose_outputs", [])
            response["msg"] = build_response.get("msg", "")
            return build_return_code, response

    response["msg"] = "Successfully built the images in: {}".format(
        os.path.realpath(output_directory)
    )
    return SUCCESS, response
