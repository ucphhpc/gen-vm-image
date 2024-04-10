import argparse
import os
import yaml
import requests
import shutil
from tqdm.auto import tqdm
from src.common.defaults import (
    GOCD_GROUP,
    GOCD_TEMPLATE,
    REPO_NAME,
    PACKAGE_NAME,
    GENERATED_IMAGE_DIR,
    TMP_DIR,
    GOCD_FORMAT_VERSION,
    GO_REVISION_COMMIT_VAR,
)
from src.utils.io import load, exists, makedirs, write, chown, hashsum
from src.utils.user import lookup_uid, lookup_gid
from src.utils.job import run


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


def run_build_image():
    parser = argparse.ArgumentParser(
        prog=PACKAGE_NAME, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--architecture-path",
        default="architecture.yml",
        help="The path to the architecture file that is used to configure the images to be built",
    )
    parser.add_argument(
        "--image-output-path",
        default=os.path.join(GENERATED_IMAGE_DIR, "image.qcow2"),
        help="The output path of the built image",
    )
    parser.add_argument(
        "--generated-image-owner",
        default="qemu",
        help="Set the uid owner of the configured image",
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
    args = parser.parse_args()

    architecture_path = args.architecture_path
    image_output_path = args.image_output_path
    generated_image_owner = args.generated_image_owner
    generate_gocd_config = args.generate_gocd_config
    gocd_config_name = args.gocd_config_name
    gocd_build_branch = args.gocd_build_branch

    image_output_dir = os.path.dirname(image_output_path)
    temporary_image_dir = TMP_DIR

    # Load the architecture file
    architecture = load(architecture_path, handler=yaml, Loader=yaml.FullLoader)
    if not architecture:
        print("Failed to load architecture file: {}".format(architecture_path))
        exit(-1)

    owner = architecture.get("owner", None)
    if not owner:
        print("Failed to find architecture the owner in: {}".format(architecture_path))
        exit(-1)

    images = architecture.get("images", None)
    if not images:
        print("Failed to find 'images' in: {}".format(architecture_path))
        exit(-1)

    required_attributes = ["name", "version", "get_url", "checksum", "size"]
    required_checksum_attributes = ["type", "value"]
    # Generate the image configuration
    for build, build_data in images.items():
        for attr in required_attributes:
            if attr not in build_data:
                print("Missing required attribute '{}': in {}".format(attr, build_data))
                exit(-2)
        vm_name = build_data["name"]
        vm_version = build_data["version"]
        vm_image_url = build_data["get_url"]
        vm_size = build_data["size"]

        vm_checksum = build_data["checksum"]
        if not isinstance(vm_checksum, dict):
            print("Invalid checksum format: {}".format(vm_checksum))
            exit(-3)
        for attr in required_checksum_attributes:
            if attr not in vm_checksum:
                print(
                    "Missing required attribute '{}': in {}".format(attr, vm_checksum)
                )
                exit(-4)

        # Prepare the temporary directory
        # where the image will be prepared
        if not exists(temporary_image_dir):
            created, msg = makedirs(temporary_image_dir)
            if not created:
                print(
                    "Failed to create temporary image directory: {} - {}".format(
                        temporary_image_dir, msg
                    )
                )

        # Download the image and save it into
        # a tmp directory
        get_url_filename = vm_image_url.split("/")[-1]
        get_url_path = os.path.join(temporary_image_dir, get_url_filename)
        cloud_image = None
        if not exists(get_url_path):
            print("Downloading image from: {}".format(vm_image_url))
            with requests.get(vm_image_url, stream=True) as r:
                # check header to get content length, in bytes
                total_length = int(r.headers.get("Content-Length"))
                # implement progress bar via tqdm
                with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
                    # Save the output
                    with open(get_url_path, "wb") as output:
                        shutil.copyfileobj(raw, output)

        checksum_type = vm_checksum["type"]
        checksum_value = vm_checksum["value"]
        calculated_checksum = hashsum(get_url_path, algorithm=checksum_type)
        if not calculated_checksum:
            print("Failed to calculate the checksum of the downloaded image")
            exit(-5)

        if calculated_checksum != checksum_value:
            print(
                "The checksum of the downloaded image does not match the expected checksum: {} != {}".format(
                    calculated_checksum, checksum_value
                )
            )
            exit(-6)
        print(
            "The calculated checksum: {} matches the defined checksum: {}".format(
                calculated_checksum, checksum_value
            )
        )

        # Create an image based on the downloaded image
        if not exists(image_output_dir):
            created, msg = makedirs(image_output_dir)
            if not created:
                print(
                    "Failed to create disk directory: {} - {}".format(
                        image_output_dir, msg
                    )
                )

        create_disk_command = [
            "qemu-img",
            "convert",
            "-f",
            "qcow2",
            "-O",
            "qcow2",
            get_url_path,
            image_output_path,
        ]
        create_disk_result = run(create_disk_command)
        if create_disk_result["returncode"] != 0:
            print(
                "Failed to create a VM disk: {} - {}".format(
                    create_disk_result["error"], create_disk_result["returncode"]
                )
            )
        else:
            print(
                "Created VM disk image at: {}".format(
                    os.path.abspath(image_output_path)
                )
            )

        # Amend to qcow2 version 3 which is required in RHEL 9
        amend_command = ["qemu-img", "amend", "-o", "compat=v3", image_output_path]
        amended_result = run(amend_command)
        if amended_result["returncode"] != 0:
            print("Failed to amend a VM disk: {}".format(amended_result["error"]))

        # Resize the vm disk image
        resize_command = ["qemu-img", "resize", image_output_path, vm_size]
        resize_result = run(resize_command)
        if resize_result["returncode"] != 0:
            print(
                "Failed to resize the downloaded image: {}".format(
                    resize_result["error"]
                )
            )

        # Check that the vm disk is consistent
        check_command = ["qemu-img", "check", "-f", "qcow2", image_output_path]
        check_result = run(check_command)
        if check_result["returncode"] != 0:
            print("The check of the vm disk failed: {}".format(check_result["error"]))

        # Set the owner of the image
        user_uid = lookup_uid(generated_image_owner)
        user_gid = lookup_gid(generated_image_owner)
        if user_uid and user_gid:
            chown_result = chown(image_output_path, user_uid, user_gid)
            if not chown_result[0]:
                print(
                    "Failed to set the owner of the image: {}".format(chown_result[1])
                )

    if generate_gocd_config:
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
            materials = get_materials(name, branch=gocd_build_branch)

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

        gocd_config_path = os.path.join(current_dir, gocd_config_name)
        if not write(gocd_config_path, generated_config, handler=yaml):
            print("Failed to save config")
            exit(-1)
        print("Generated a new GOCD config in: {}".format(gocd_config_path))


if __name__ == "__main__":
    run_build_image()
