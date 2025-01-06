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
import validators
from gen_vm_image.common.defaults import (
    GENERATED_IMAGE_DIR,
    TMP_DIR,
    CONSITENCY_SUPPPORTED_FORMATS,
)
from gen_vm_image.common.codes import (
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
    DOWNLOAD_ERROR,
    GETSIZE_ERROR,
    GETSIZE_ERROR_MSG,
)
from gen_vm_image.utils.io import exists, makedirs, hashsum
from gen_vm_image.utils.io import size as get_size
from gen_vm_image.utils.job import run
from gen_vm_image.utils.net import download_file


def qemu_img_call(action, args, format_output_str=True, verbose=False):
    command = ["qemu-img", action]
    if not verbose:
        command.append("-q")
    command.extend(args)

    result = run(command, format_output_str=format_output_str, capture_output=True)
    if result["returncode"] != "0":
        return False, result["error"]
    return True, result["output"]


def create_image(path, size, image_format="qcow2", verbose=False):
    args = ["-f", image_format, path, size]
    result, msg = qemu_img_call("create", args, verbose=verbose)
    if not result:
        return False, msg
    return True, msg


def convert_image(
    input_path, output_path, input_format="qcow2", output_format="qcow2", verbose=False
):
    args = ["-f", input_format, "-O", output_format, input_path, output_path]
    result, msg = qemu_img_call("convert", args, verbose=verbose)
    if not result:
        return False, msg
    return True, msg


def resize_image(path, size, image_format="qcow2", resize_args=None, verbose=False):
    if not resize_args:
        resize_args = []

    result, msg = qemu_img_call(
        "resize", [*resize_args, "-f", image_format, path, size], verbose=verbose
    )
    if not result:
        return False, msg
    return True, msg


def amend_image(path, options, image_format="qcow2", verbose=False):
    args = ["-f", image_format, "-o", options, path]
    result, msg = qemu_img_call("amend", args, verbose=verbose)
    if not result:
        return False, msg
    return True, msg


def check_image(path, image_format="qcow2", verbose=False):
    if image_format not in CONSITENCY_SUPPPORTED_FORMATS:
        msg = "format: '{}' not supported for consistency check, only one of: {} is supported".format(
            image_format, CONSITENCY_SUPPPORTED_FORMATS
        )
        return False, msg
    result, msg = qemu_img_call("check", ["-f", image_format, path], verbose=verbose)
    if not result:
        return False, msg
    return True, msg


def expand_byte_magnitude(bytesize):
    # Convert
    expanded_bytesize = None
    if "kib" in bytesize.lower() or "ki" in bytesize.lower():
        expanded_bytesize = int(bytesize.lower().replace("kib", "").replace("ki", ""))
    elif "mib" in bytesize.lower() or "mi" in bytesize.lower():
        expanded_bytesize = (
            int(bytesize.lower().replace("mib", "").replace("mi", "")) * 1024
        )
    elif "mb" in bytesize.lower() or "m" in bytesize.lower():
        expanded_bytesize = (
            int(bytesize.lower().replace("mb", "").replace("m", "")) * 1000
        )
    elif "gib" in bytesize.lower() or "gi" in bytesize.lower():
        expanded_bytesize = (
            int(bytesize.lower().replace("gib", "").replace("gi", "")) * 1024 * 1024
        )
    elif "gb" in bytesize.lower() or "g" in bytesize.lower():
        expanded_bytesize = (
            int(bytesize.lower().replace("gb", "").replace("g", "")) * 1000 * 1000
        )
    elif "tib" in bytesize.lower() or "ti" in bytesize.lower():
        expanded_bytesize = (
            int(bytesize.lower().replace("tib", "").replace("ti", ""))
            * 1024
            * 1024
            * 1024
        )
    elif "tb" in bytesize.lower() or "t" in bytesize.lower():
        expanded_bytesize = (
            int(bytesize.lower().replace("tb", "").replace("t", ""))
            * 1000
            * 1000
            * 1000
        )
    else:
        expanded_bytesize = int(bytesize)
    return expanded_bytesize


def generate_image(
    name,
    size,
    # Optional version attribute for each image configuration
    version=None,
    image_input=None,
    input_format="qcow2",
    input_checksum_type=None,
    input_checksum=None,
    output_format="qcow2",
    output_directory=GENERATED_IMAGE_DIR,
    overwrite=False,
    verbose=False,
):
    response = {}
    verbose_outputs = []

    if version:
        vm_output_path = os.path.join(
            output_directory,
            "{}-{}.{}".format(name, version, output_format),
        )
    else:
        vm_output_path = os.path.join(
            output_directory, "{}.{}".format(name, output_format)
        )

    if exists(vm_output_path):
        if verbose:
            verbose_outputs.append(
                "The output image: {} already exists".format(vm_output_path)
            )
        if not overwrite:
            if verbose:
                verbose_outputs.append(
                    "Use the --overwrite flag to overwrite the existing image"
                )
                response["verbose_outputs"] = verbose_outputs
            return SUCCESS, response
        else:
            if verbose:
                verbose_outputs.append(
                    "Overwriting the existing image: {}".format(vm_output_path)
                )

    if image_input:
        if not isinstance(image_input, str):
            response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                type(image_input), image_input, "string"
            )
            response["verbose_outputs"] = verbose_outputs
            return INVALID_ATTRIBUTE_TYPE_ERROR, response

        # If a checksum is present, then validate that it is correctly structured
        if input_checksum:
            if not isinstance(input_checksum, str):
                response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                    type(input_checksum),
                    input_checksum,
                    "string",
                )
                response["verbose_outputs"] = verbose_outputs
                return INVALID_ATTRIBUTE_TYPE_ERROR, response

            if not input_checksum_type:
                response["msg"] = MISSING_ATTRIBUTE_ERROR_MSG.format(
                    "input_checksum_type", input_checksum
                )
                response["verbose_outputs"] = verbose_outputs
                return MISSING_ATTRIBUTE_ERROR, response

            if not isinstance(input_checksum_type, str):
                response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                    type(input_checksum_type),
                    input_checksum_type,
                    "string",
                )
                response["verbose_outputs"] = verbose_outputs
                return INVALID_ATTRIBUTE_TYPE_ERROR, response

        if validators.url(image_input):
            image_input_url = image_input
            # Download the specified url and save it into
            # a tmp directory.
            # First prepare the temporary directory
            # where the downloaded image will be prepared
            if not exists(TMP_DIR):
                created = makedirs(TMP_DIR)
                if not created:
                    response["msg"] = PATH_CREATE_ERROR_MSG.format(
                        TMP_DIR,
                        "Failed to create the temporary download directory",
                    )
                    response["verbose_outputs"] = verbose_outputs
                    return PATH_CREATE_ERROR, response

            input_url_filename = image_input_url.split("/")[-1]
            input_image_path = os.path.join(TMP_DIR, input_url_filename)
            if not exists(input_image_path):
                if verbose:
                    verbose_outputs.append(
                        "Downloading image from: {}".format(image_input_url)
                    )
                downloaded, download_response = download_file(
                    image_input_url, input_image_path
                )
                if not downloaded:
                    response["msg"] = download_response["msg"]
                    response["verbose_outputs"] = verbose_outputs
                    return DOWNLOAD_ERROR, response
                if verbose:
                    verbose_outputs.append(
                        "Download details: {}".format(download_response)
                    )
        else:
            # If the input is a string, then we assume that it is a path to the image
            if not exists(image_input):
                response["msg"] = PATH_NOT_FOUND_ERROR_MSG.format(
                    image_input, "the defined input path to the does not exist"
                )
                response["verbose_outputs"] = verbose_outputs
                return PATH_NOT_FOUND_ERROR, response
            input_image_path = image_input

        if not input_format and input_image_path:
            # Try to discover the input format since we have
            # only been given a string value
            input_format = input_image_path.split(".")[-1]

        if not isinstance(input_format, str):
            response["msg"] = INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                type(input_format), input_format, "string"
            )
            response["verbose_outputs"] = verbose_outputs
            return INVALID_ATTRIBUTE_TYPE_ERROR, response

        if input_checksum:
            calculated_checksum = hashsum(
                input_image_path, algorithm=input_checksum_type
            )
            if not calculated_checksum:
                response["msg"] = (
                    "Failed to calculate the checksum of the downloaded image"
                )
                response["verbose_outputs"] = verbose_outputs
                return CHECKSUM_ERROR, response

            if calculated_checksum != input_checksum:
                response["msg"] = (
                    "The checksum of the downloaded image: {} does not match the expected checksum: {}".format(
                        calculated_checksum, input_checksum
                    )
                )
                response["verbose_outputs"] = verbose_outputs
                return CHECKSUM_ERROR, response
            if verbose:
                verbose_outputs.append(
                    "The calculated checksum: {} matches the defined checksum: {}".format(
                        calculated_checksum, input_checksum
                    )
                )

        converted_result, msg = convert_image(
            input_image_path,
            vm_output_path,
            input_format=input_format,
            output_format=output_format,
            verbose=verbose,
        )
        if not converted_result:
            response["msg"] = PATH_CREATE_ERROR_MSG.format(input_image_path, msg)
            response["verbose_outputs"] = verbose_outputs
            return PATH_CREATE_ERROR, response

        image_input_size = get_size(input_image_path)
        if not image_input_size:
            response["msg"] = GETSIZE_ERROR_MSG.format(input_image_path)
            response["verbose_outputs"] = verbose_outputs
            return GETSIZE_ERROR, response

        expected_resize_size = expand_byte_magnitude(size)
        resize_args = []
        if expected_resize_size < image_input_size:
            resize_args = ["--shrink"]

        # Resize the vm disk image
        resized_result, resized_msg = resize_image(
            vm_output_path,
            size,
            image_format=output_format,
            resize_args=resize_args,
            verbose=verbose,
        )
        if not resized_result:
            response["msg"] = RESIZE_ERROR_MSG.format(vm_output_path, resized_msg)
            response["verbose_outputs"] = verbose_outputs
            return RESIZE_ERROR, response
    else:
        # If no input is specified, then we assume that we are creating a new disc image
        create_image_result, msg = create_image(
            vm_output_path,
            size,
            image_format=output_format,
            verbose=verbose,
        )
        if not create_image_result:
            response["msg"] = PATH_CREATE_ERROR_MSG.format(vm_output_path, msg)
            response["verbose_outputs"] = verbose_outputs
            return PATH_CREATE_ERROR, response
        else:
            if verbose:
                verbose_outputs.append(
                    "Generated image at: {}".format(os.path.realpath(vm_output_path))
                )

    # Amend to qcow2 version 3 which is required in RHEL 9 if the output format is
    # qcow2
    # TODO, validate that the image is a rhel based image
    if output_format == "qcow2":
        amend_result, amend_msg = amend_image(
            vm_output_path, "compat=v3", verbose=verbose
        )
        if not amend_result:
            verbose_outputs.append(
                PATH_CREATE_ERROR_MSG.format(vm_output_path, amend_msg)
            )

    if output_format in CONSITENCY_SUPPPORTED_FORMATS:
        check_result, check_msg = check_image(
            vm_output_path,
            image_format=output_format,
            verbose=verbose,
        )
        if not check_result:
            response["msg"] = CHECK_ERROR_MSG.format(check_msg)
            response["verbose_outputs"] = verbose_outputs
            return CHECK_ERROR, response
    return SUCCESS, response
