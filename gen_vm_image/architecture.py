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
from gen_vm_image.common.defaults import GENERATED_IMAGE_DIR
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

    required_attributes = ["name", "version", "size"]
    for image_name, image_data in images.items():
        for attribute in required_attributes:
            if attribute not in image_data:
                return MISSING_ATTRIBUTE_ERROR, MISSING_ATTRIBUTE_ERROR_MSG.format(
                    attribute, image_name
                )
    return True, response


def build_architecture(
    architecture_path,
    images_output_directory=GENERATED_IMAGE_DIR,
    overwrite=False,
    verbose=False,
):
    response = {}
    verbose_outputs = []
    # Load the architecture file
    architecture_loaded, architecture_response = load_architecture(architecture_path)
    if not architecture_loaded:
        return architecture_response["error_code"], architecture_response["msg"]

    architecture = architecture_response["architecture"]
    correct_architecture, correct_response = correct_architecture_structure(
        architecture
    )
    if not correct_architecture:
        return correct_response["error_code"], correct_response["msg"]

    # Create the destination directory where the images will be saved
    if not exists(images_output_directory):
        created = makedirs(images_output_directory)
        if not created:
            response["msg"] = PATH_CREATE_ERROR_MSG.format(
                images_output_directory, "Failed to create the images output directory"
            )
            response["verbose_outputs"] = verbose_outputs
            return PATH_CREATE_ERROR, response

    if "images" not in architecture:
        response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format("images", architecture)
        response["verbose_outputs"] = verbose_outputs
        return MISSING_ATTRIBUTE_ERROR, response

    images = architecture.get("images")
    if not isinstance(images, dict):
        response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
            type(images), images, dict
        )
        response["verbose_outputs"] = verbose_outputs
        return INVALID_ATTRIBUTE_TYPE_ERROR, response

    # Generate the image configuration
    for _, build_data in images.items():
        build_return_code, build_response = generate_image(
            build_data["name"],
            build_data["size"],
            version=build_data.get("version", None),
            image_input=build_data.get("input", None),
            output_format=build_data.get("format", "qcow2"),
            output_directory=images_output_directory,
            overwrite=overwrite,
            verbose=verbose,
        )
        if build_return_code != SUCCESS:
            return build_return_code, response

    response["msg"] = "Successfully built the images in: {}".format(
        os.path.realpath(images_output_directory)
    )
    response["verbose_outputs"] = verbose_outputs
    return SUCCESS, response
