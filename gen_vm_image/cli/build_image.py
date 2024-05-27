import argparse
import os
import yaml
import requests
import shutil
from tqdm.auto import tqdm
from gen_vm_image.common.defaults import (
    GOCD_GROUP,
    GOCD_TEMPLATE,
    REPO_NAME,
    PACKAGE_NAME,
    GENERATED_IMAGE_DIR,
    TMP_DIR,
    GOCD_FORMAT_VERSION,
    GO_REVISION_COMMIT_VAR,
)
from gen_vm_image.common.errors import (
    PATH_NOT_FOUND_ERROR,
    PATH_NOT_FOUND_ERROR_MSG,
    PATH_CREATE_ERROR,
    PATH_CREATE_ERROR_MSG,
    MISSING_ATTRIBUTE_ERROR,
    MISSING_ATTRIBUTE_ERROR_MSG,
    INVALID_ATTRIBUTE_TYPE_ERROR,
    INVALID_ATTRIBUTE_TYPE_ERROR_MSG,
    CHECKSUM_ERROR,
)
from gen_vm_image.architecture import load_architecture, correct_architecture_structure
from gen_vm_image.utils.io import exists, makedirs, write, hashsum
from gen_vm_image.utils.job import run


current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)


def get_pipelines(images):
    pipelines = []
    for build in images:
        pipelines.append(build)
    return pipelines


def get_common_environment(pipelines):
    common_environment = {
        "environments": {
            GOCD_GROUP: {
                "environment_variables": {
                    "GIT_USER": "{{SECRET:[github][username]}}",
                },
                "pipelines": pipelines,
            }
        }
    }
    return common_environment


def get_common_pipeline():
    common_pipeline = {
        "group": GOCD_GROUP,
        "label_template": "${COUNT}",
        "lock_behaviour": "none",
        "display_order": -1,
        "template": GOCD_TEMPLATE,
    }
    return common_pipeline


def get_common_materials(branch="main"):
    common_materials = {
        "ucphhpc_images": {
            "git": "https://github.com/ucphhpc/{}.git".format(REPO_NAME),
            "branch": branch,
            "destination": REPO_NAME,
            "username": "${GIT_USER}",
            "password": "{{SECRET:[github][access_token]}}",
        },
        # this is the name of material
        # says about type of material and url at once
    }
    return common_materials


def get_upstream_materials(name, pipeline, stage):
    upstream_materials = {
        "upstream_{}".format(name): {
            "pipeline": pipeline,
            "stage": stage,
        }
    }
    return upstream_materials


def get_materials(name, upstream_pipeline=None, stage=None, branch="main"):
    materials = {}
    common_materials = get_common_materials(branch=branch)
    materials.update(common_materials)
    if upstream_pipeline and stage:
        upstream_materials = get_upstream_materials(name, upstream_pipeline, stage)
        materials.update(upstream_materials)
    return materials


def create_image(name, version, size, image_format="qcow2"):
    image_name = "{}-{}.{}".format(name, version, image_format)
    create_image_command = ["qemu-img", "create", "-f", image_format, image_name, size]
    created_result = run(create_image_command, format_output_str=True)
    if created_result["returncode"] != "0":
        return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(
            image_name, created_result["error"]
        )
    return created_result, None


def convert_image(input_path, output_path, input_format="qcow2", output_format="qcow2"):
    convert_image_command = [
        "qemu-img",
        "convert",
        "-f",
        input_format,
        "-O",
        output_format,
        input_path,
        output_path,
    ]
    converted_result = run(convert_image_command, format_output_str=True)
    if converted_result["returncode"] != "0":
        return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(
            input_path, converted_result["error"]
        )
    return converted_result, None


def build_gocd_config(architecture, gocd_name, branch, verbose):
    images = architecture.get("images", [])

    # GOCD file
    list_images = list(images.keys())

    # Get all pipelines
    pipelines = get_pipelines(list_images)

    # GOCD environment
    common_environments = get_common_environment(pipelines)

    # Common GOCD pipeline params
    common_pipeline_attributes = get_common_pipeline()

    generated_config = {
        "format_version": GOCD_FORMAT_VERSION,
        **common_environments,
        "pipelines": {},
    }
    # Generate the GOCD build config
    for build, build_data in images.items():
        name = build_data.get("name", None)
        version = build_data.get("version", None)
        materials = get_materials(name, branch=branch)

        build_version_name = build
        build_pipeline = {
            **common_pipeline_attributes,
            "materials": materials,
            "parameters": {
                "IMAGE": name,
                "IMAGE_PIPELINE": build_version_name,
                "DEFAULT_TAG": version,
                "SRC_DIRECTORY": REPO_NAME,
                "TEST_DIRECTORY": REPO_NAME,
                "PUSH_DIRECTORY": "publish-docker-scripts",
                "COMMIT_TAG": GO_REVISION_COMMIT_VAR,
                "ARGS": "",
            },
        }
        generated_config["pipelines"][build_version_name] = build_pipeline

    gocd_config_path = os.path.join(current_dir, gocd_name)
    if not write(gocd_config_path, generated_config, handler=yaml):
        print(
            PATH_CREATE_ERROR_MSG.format(gocd_config_path, "Failed to save gocd config")
        )
        exit(PATH_CREATE_ERROR)
    if verbose:
        print("Generated a new GOCD config in: {}".format(gocd_config_path))


def build_architecture(architecture_path, images_output_directory, verbose):
    # Load the architecture file
    architecture, load_error_msg = load_architecture(architecture_path)
    if load_error_msg:
        print(load_error_msg)
        exit(architecture)

    correct_architecture, correct_error_msg = correct_architecture_structure(
        architecture
    )
    if not correct_architecture:
        print(correct_error_msg)
        exit(correct_architecture)

    # Create the destination directory where the images will be saved
    if not exists(images_output_directory):
        created, msg = makedirs(images_output_directory)
        if not created:
            print(PATH_CREATE_ERROR_MSG.format(images_output_directory, msg))
            exit(PATH_CREATE_ERROR)

    images = architecture.get("images", [])
    # Generate the image configuration
    for build, build_data in images.items():
        # Base command used to either create or convert an image
        disc_action = ["qemu-img"]
        vm_name = build_data["name"]
        vm_version = build_data["version"]
        vm_size = build_data["size"]

        # Optional attributes for each image configuration
        vm_output_format = build_data.get("format", "qcow2")
        vm_input, vm_input_format = None, "qcow2"
        if "input" in build_data:
            vm_input = build_data["input"]
            if not isinstance(vm_input, str) and not isinstance(vm_input, dict):
                print(
                    INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                        type(vm_input), vm_input, "string or dictionary"
                    )
                )
                exit(INVALID_ATTRIBUTE_TYPE_ERROR)

        vm_output_path = os.path.join(
            images_output_directory,
            "{}-{}.{}".format(vm_name, vm_version, vm_output_format),
        )

        if vm_input:
            if isinstance(vm_input, dict):
                if "url" not in vm_input:
                    print(MISSING_ATTRIBUTE_ERROR_MSG.format("url", vm_input))
                    exit(MISSING_ATTRIBUTE_ERROR)
                if not isinstance(vm_input["url"], str):
                    print(
                        INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                            type(vm_input["url"]), vm_input["url"], "string"
                        )
                    )
                    exit(INVALID_ATTRIBUTE_TYPE_ERROR)

                if "checksum" not in vm_input:
                    print(MISSING_ATTRIBUTE_ERROR_MSG.format("checksum", vm_input))
                    exit(MISSING_ATTRIBUTE_ERROR)
                if not isinstance(vm_input["checksum"], dict):
                    print(
                        INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                            type(vm_input["checksum"]),
                            vm_input["checksum"],
                            "dictionary",
                        )
                    )
                    exit(INVALID_ATTRIBUTE_TYPE_ERROR)
                required_checksum_attributes = ["type", "value"]
                for attr in required_checksum_attributes:
                    if attr not in vm_input["checksum"]:
                        print(
                            MISSING_ATTRIBUTE_ERROR_MSG.format(
                                attr, vm_input["checksum"]
                            )
                        )
                        exit(MISSING_ATTRIBUTE_ERROR)
                    if not isinstance(vm_input["checksum"][attr], str):
                        print(
                            INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                                type(vm_input["checksum"][attr]),
                                vm_input["checksum"][attr],
                                "string",
                            )
                        )
                        exit(INVALID_ATTRIBUTE_TYPE_ERROR)

                vm_input_url = vm_input["url"]
                vm_input_checksum = vm_input["checksum"]
                # Download the specified Url and save it into
                # a tmp directory.
                # First prepare the temporary directory
                # where the downloaded image will be prepared
                if not exists(TMP_DIR):
                    created, msg = makedirs(TMP_DIR)
                    if not created:
                        print(PATH_CREATE_ERROR_MSG.format(TMP_DIR, msg))
                        exit(PATH_CREATE_ERROR)

                input_url_filename = vm_input_url.split("/")[-1]
                input_vm_path = os.path.join(TMP_DIR, input_url_filename)
                if not exists(input_vm_path):
                    if verbose:
                        print("Downloading image from: {}".format(vm_input_url))
                    with requests.get(vm_input_url, stream=True) as r:
                        # check header to get content length, in bytes
                        total_length = int(r.headers.get("Content-Length"))
                        # implement progress bar via tqdm
                        with tqdm.wrapattr(
                            r.raw, "read", total=total_length, desc=""
                        ) as raw:
                            # Save the output
                            with open(input_vm_path, "wb") as output:
                                shutil.copyfileobj(raw, output)

                checksum_type = vm_input_checksum["type"]
                checksum_value = vm_input_checksum["value"]
                calculated_checksum = hashsum(input_vm_path, algorithm=checksum_type)
                if not calculated_checksum:
                    print("Failed to calculate the checksum of the downloaded image")
                    exit(CHECKSUM_ERROR)

                if calculated_checksum != checksum_value:
                    print(
                        "The checksum of the downloaded image does not match the expected checksum: {} != {}".format(
                            calculated_checksum, checksum_value
                        )
                    )
                    exit(CHECKSUM_ERROR)
                if verbose:
                    print(
                        "The calculated checksum: {} matches the defined checksum: {}".format(
                            calculated_checksum, checksum_value
                        )
                    )
            else:
                if not exists(vm_input):
                    print(
                        PATH_NOT_FOUND_ERROR_MSG.format(
                            vm_input, "the defined input path to the does not exist"
                        )
                    )
                    exit(PATH_NOT_FOUND_ERROR)
            convert_action = [
                "convert",
                "-f",
                vm_input_format,
                "-O",
                vm_output_format,
                input_vm_path,
                vm_output_path,
            ]
            disc_action.extend(convert_action)
        else:
            # If no input is specified, then we assume that we are creating a new disc image
            new_action = ["create", "-f", vm_output_format, vm_output_path, vm_size]
            disc_action.extend(new_action)

        disc_action_result = run(disc_action)
        if disc_action_result["returncode"] != 0:
            print(
                PATH_CREATE_ERROR_MSG.format(
                    vm_output_path, disc_action_result["error"]
                )
            )
            exit(PATH_CREATE_ERROR)
        else:
            if verbose:
                print(
                    "Created VM disk image at: {}".format(
                        os.path.abspath(vm_output_path)
                    )
                )

        # Amend to qcow2 version 3 which is required in RHEL 9
        amend_command = ["qemu-img", "amend", "-o", "compat=v3", vm_output_path]
        amended_result = run(amend_command)
        if amended_result["returncode"] != 0:
            print(PATH_CREATE_ERROR_MSG.format(vm_output_path, amended_result["error"]))

        # Resize the vm disk image
        resize_command = ["qemu-img", "resize", vm_output_path, vm_size]
        resize_result = run(resize_command)
        if resize_result["returncode"] != 0:
            print(
                "Failed to resize the downloaded image: {}".format(
                    resize_result["error"]
                )
            )

        # Check that the vm disk is consistent
        check_command = ["qemu-img", "check", "-f", vm_output_format, vm_output_path]
        check_result = run(check_command)
        if check_result["returncode"] != 0:
            print("The check of the vm disk failed: {}".format(check_result["error"]))


def cli():
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--architecture-path",
        default="architecture.yml",
        help="The path to the architecture file that defines the images to build",
    )
    parser.add_argument(
        "--images-output-directory",
        default=GENERATED_IMAGE_DIR,
        help="The path to the output directory where the images will be saved",
    )
    parser.add_argument(
        "--generate-gocd-config",
        action="store_true",
        help="Generate a GoCD config based on the architecture file",
    )
    parser.add_argument(
        "--gocd-config-name",
        default="1.gocd.yml",
        help="Name of the generated gocd config file",
    )
    parser.add_argument(
        "--gocd-build-branch",
        default="main",
        help="The branch that GoCD should use to build images",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Print verbose output",
    )
    args = parser.parse_args()

    architecture_path = args.architecture_path
    images_output_directory = args.images_output_directory
    generate_gocd_config = args.generate_gocd_config
    gocd_config_name = args.gocd_config_name
    gocd_build_branch = args.gocd_build_branch
    verbose = args.verbose

    build_architecture(architecture_path, images_output_directory, verbose)
    if generate_gocd_config:
        build_gocd_config(
            architecture_path, gocd_config_name, gocd_build_branch, verbose
        )
    exit(0)


if __name__ == "__main__":
    cli()
