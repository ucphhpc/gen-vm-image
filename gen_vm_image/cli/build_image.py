import argparse
import os
import yaml
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
    RESIZE_ERROR,
    RESIZE_ERROR_MSG,
    CHECK_ERROR,
    CHECK_ERROR_MSG,
)
from gen_vm_image.architecture import load_architecture, correct_architecture_structure
from gen_vm_image.utils.io import exists, makedirs, write, hashsum
from gen_vm_image.utils.job import run
from gen_vm_image.utils.net import download_file


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
    command = ["qemu-img", "create", "-f", image_format, image_name, size]
    result = run(command, format_output_str=True)
    if result["returncode"] != "0":
        return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(
            image_name, result["error"]
        )
    return result, None


def convert_image(input_path, output_path, input_format="qcow2", output_format="qcow2"):
    command = [
        "qemu-img",
        "convert",
        "-f",
        input_format,
        "-O",
        output_format,
        input_path,
        output_path,
    ]
    result = run(command, format_output_str=True)
    if result["returncode"] != "0":
        return PATH_CREATE_ERROR, PATH_CREATE_ERROR_MSG.format(
            input_path, result["error"]
        )
    return result, None


def resize_image(path, size):
    command = ["qemu-img", "resize", path, size]
    result = run(command, format_output_str=True)
    if result["returncode"] != "0":
        return RESIZE_ERROR, RESIZE_ERROR_MSG.format(result["error"])
    return result, None


def check_image(path, image_format="qcow2"):
    command = ["qemu-img", "check", "-f", image_format, path]
    result = run(command, format_output_str=True)
    if result["returncode"] != "0":
        return CHECK_ERROR, CHECK_ERROR_MSG.format(result["error"])
    return result, None


def build_gocd_config(architecture, gocd_name, branch, verbose=False):
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
                "PUSH_DIRECTORY": "publish-python-scripts",
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


def build_architecture(architecture_path, images_output_directory, verbose=False):
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
                if "url" not in vm_input or "path" not in vm_input:
                    print(
                        MISSING_ATTRIBUTE_ERROR_MSG.format(
                            "'url' or 'path' must be in the architecture input section",
                            vm_input,
                        )
                    )
                    exit(MISSING_ATTRIBUTE_ERROR)

                if "url" in vm_input and "path" in vm_input:
                    print(
                        "Both 'url' and 'path' are defined in the architecture input section. Only one can be defined"
                    )
                    exit(INVALID_ATTRIBUTE_TYPE_ERROR)

                if "url" in vm_input:
                    if not isinstance(vm_input["url"], str):
                        print(
                            INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                                type(vm_input["url"]), vm_input["url"], "string"
                            )
                        )
                        exit(INVALID_ATTRIBUTE_TYPE_ERROR)

                if "path" in vm_input:
                    if not isinstance(vm_input["path"], str):
                        print(
                            INVALID_ATTRIBUTE_TYPE_ERROR_MSG.format(
                                type(vm_input["path"]), vm_input["path"], "string"
                            )
                        )
                        exit(INVALID_ATTRIBUTE_TYPE_ERROR)

                # If a checksum is present, then validate that it is correctly structured
                vm_input_checksum = None
                if "checksum" in vm_input:
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
                            print(PATH_CREATE_ERROR_MSG.format(TMP_DIR, msg))
                            exit(PATH_CREATE_ERROR)

                    input_url_filename = vm_input_url.split("/")[-1]
                    input_vm_path = os.path.join(TMP_DIR, input_url_filename)
                    if not exists(input_vm_path):
                        if verbose:
                            print("Downloading image from: {}".format(vm_input_url))
                        download_file(vm_input_url, input_vm_path)
                elif "path" in vm_input:
                    input_vm_path = vm_input["path"]
                    if not exists(input_vm_path):
                        print(
                            PATH_NOT_FOUND_ERROR_MSG.format(
                                input_vm_path,
                                "the defined input path to the does not exist",
                            )
                        )
                        exit(PATH_NOT_FOUND_ERROR)

                if vm_input_checksum:
                    checksum_type = vm_input_checksum["type"]
                    checksum_value = vm_input_checksum["value"]
                    calculated_checksum = hashsum(
                        input_vm_path, algorithm=checksum_type
                    )
                    if not calculated_checksum:
                        print(
                            "Failed to calculate the checksum of the downloaded image"
                        )
                        exit(CHECKSUM_ERROR)

                    if calculated_checksum != checksum_value:
                        print(
                            "The checksum of the downloaded image: {} does not match the expected checksum: {}".format(
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

            converted_result, msg = convert_image(
                input_vm_path,
                vm_output_path,
                input_format=vm_input_format,
                output_format=vm_output_format,
            )
            if not converted_result:
                print(msg)
                exit(converted_result)

            # Resize the vm disk image
            resized_result, resized_msg = resize_image(vm_output_path, vm_size)
            if not resized_result:
                print(resized_msg)
                exit(resized_result)
        else:
            # If no input is specified, then we assume that we are creating a new disc image
            create_image_result, msg = create_image(
                vm_input, vm_version, vm_size, image_format=vm_output_format
            )
            if not create_image_result:
                print(msg)
                exit(create_image_result)
            else:
                if verbose:
                    print(
                        "Generated image at: {}".format(os.path.abspath(vm_output_path))
                    )

        # TODO, check if the image in question is a rhel9 based image
        # Amend to qcow2 version 3 which is required in RHEL 9
        amend_command = ["qemu-img", "amend", "-o", "compat=v3", vm_output_path]
        amended_result = run(amend_command, format_output_str=True)
        if amended_result["returncode"] != "0":
            print(PATH_CREATE_ERROR_MSG.format(vm_output_path, amended_result["error"]))

        check_result, check_msg = check_image(
            vm_output_path, image_format=vm_output_format
        )
        if not check_result:
            print(check_msg)
            exit(check_result)


def cli():
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME, formatter_class=argparse.ArgumentDefaultsHelpFormatter
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

    build_architecture(architecture_path, images_output_directory, verbose=verbose)
    if generate_gocd_config:
        build_gocd_config(
            architecture_path, gocd_config_name, gocd_build_branch, verbose=verbose
        )
    exit(0)


if __name__ == "__main__":
    cli()
