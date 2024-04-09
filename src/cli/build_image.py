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
    IMAGE_DIR,
    TMP_DIR,
    GOCD_FORMAT_VERSION,
    GO_REVISION_COMMIT_VAR,
)
from src.utils.io import load, exists, makedirs, write, chown
from src.utils.user import lookup_uid, lookup_gid
from src.utils.job import run


current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)


def get_pipelines(architectures):
    pipelines = []
    for build in architectures:
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
    parser = argparse.ArgumentParser(prog=PACKAGE_NAME)
    parser.add_argument(
        "--architecture-path",
        default="architecture.yml",
        help="The path to the architecture file that is used to configure the images to be built",
    )
    parser.add_argument(
        "--config-name", default="1.gocd.yml", help="Name of the output gocd config"
    )
    parser.add_argument(
        "--branch", default="main", help="The branch that should be built"
    )
    parser.add_argument(
        "--makefile", default="Makefile", help="The makefile that defines the images"
    )
    parser.add_argument(
        "--image-output-path",
        default=os.path.join(IMAGE_DIR, "image.qcow2"),
        help="The output path of the built image",
    )
    parser.add_argument(
        "--image-owner",
        default="qemu",
        help="Set the owner of the configured image to this user",
    )
    parser.add_argument(
        "--generate-gocd-config",
        action="store_true",
        help="Generate a GOCD config based on the architecture file",
    )
    args = parser.parse_args()

    architecture_path = args.architecture_path
    config_name = args.config_name
    branch = args.branch
    makefile = args.makefile
    image_output_path = args.image_output_path
    image_owner = args.image_owner
    generate_gocd_config = args.generate_gocd_config

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

    architecture = architecture.get("architecture", None)
    if not architecture:
        print("Failed to find the architecture in: {}".format(architecture_path))
        exit(-1)

    required_attributes = ["name", "version", "cloud_img", "size"]
    # Generate the image configuration
    for build, build_data in architecture.items():
        for attr in required_attributes:
            if attr not in build_data:
                print("Missing required attribute '{}': in {}".format(attr, build_data))
                exit(-2)
        vm_name = build_data["name"]
        vm_version = build_data["version"]
        vm_image = build_data["cloud_img"]
        vm_size = build_data["size"]

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
        cloud_img_url = vm_image
        cloud_img_filename = cloud_img_url.split("/")[-1]
        cloud_img_path = os.path.join(temporary_image_dir, cloud_img_filename)
        cloud_image = None
        if not exists(cloud_img_path):
            print("Downloading image from: {}".format(cloud_img_url))
            with requests.get(cloud_img_url, stream=True) as r:
                # check header to get content length, in bytes
                total_length = int(r.headers.get("Content-Length"))
                # implement progress bar via tqdm
                with tqdm.wrapattr(r.raw, "read", total=total_length, desc="") as raw:
                    # Save the output
                    with open(cloud_img_path, "wb") as output:
                        shutil.copyfileobj(raw, output)

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
            cloud_img_path,
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
        user_uid = lookup_uid(image_owner)
        user_gid = lookup_gid(image_owner)
        if user_uid and user_gid:
            chown_result = chown(image_output_path, user_uid, user_gid)
            if not chown_result[0]:
                print(
                    "Failed to set the owner of the image: {}".format(chown_result[1])
                )

    if generate_gocd_config:
        # GOCD file
        list_architectures = list(architecture.keys())

        # Get all pipelines
        pipelines = get_pipelines(list_architectures)

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
        for build, build_data in architecture.items():
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

        path = os.path.join(current_dir, config_name)
        if not write(path, generated_config, handler=yaml):
            print("Failed to save config")
            exit(-1)
        print("Generated a new GOCD config in: {}".format(path))


if __name__ == "__main__":
    run_build_image()
