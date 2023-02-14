import argparse
import os
import yaml
import wget
from jinja2 import Template
from setup.io import load, write, exists
from setup.job import run


current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)

PACKAGE_NAME = "generate-gocd-config"
REPO_NAME = "sif-vm-images"
GOCD_TEMPLATE = "bare_metal_vm_image"
GOCD_FORMAT_VERSION = 10
GO_REVISION_COMMIT_VAR = "GO_REVISION_SIF_VM_IMAGES"


def get_pipelines(architectures):
    pipelines = []
    for build in architectures:
        pipelines.append(build)
    return pipelines


def get_common_environment(pipelines):
    common_environment = {
        "environments": {
            "vm_image": {
                "environment_variables": {},
                "pipelines": pipelines,
            }
        }
    }
    return common_environment


def get_common_pipeline():
    common_pipeline = {
        "group": "vm_image",
        "label_template": "${COUNT}",
        "lock_behaviour": "none",
        "display_order": -1,
        "template": GOCD_TEMPLATE,
    }
    return common_pipeline


def get_common_materials():
    common_materials = {
        "ucphhpc_images": {
            "git": "https://github.com/ucphhpc/{}.git".format(REPO_NAME),
            "branch": branch,
            "destination": REPO_NAME,
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


def get_materials(name, upstream_pipeline=None, stage=None):
    materials = {}
    common_materials = get_common_materials()
    materials.update(common_materials)
    if upstream_pipeline and stage:
        upstream_materials = get_upstream_materials(name, upstream_pipeline, stage)
        materials.update(upstream_materials)
    return materials


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=PACKAGE_NAME)
    parser.add_argument(
        "--architecture-name",
        default="architecture.yml",
        help="The name of the architecture file that is used to configure the images to be built",
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
    args = parser.parse_args()

    architecture_name = args.architecture_name
    config_name = args.config_name
    branch = args.branch
    makefile = args.makefile

    # Load the architecture file
    architecture_path = os.path.join(current_dir, architecture_name)
    architecture = load(architecture_path, handler=yaml, Loader=yaml.FullLoader)
    owner = architecture.get("owner", None)
    if not owner:
        print("Failed to find architecture the owner in: {}".format(architecture_path))
        exit(-1)

    architecture = architecture.get("architecture", None)
    if not architecture:
        print("Failed to find the architecture in: {}".format(architecture_path))
        exit(-1)

    list_architectures = list(architecture.keys())
    num_builds = len(list_architectures) - 1

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

    required_attributes = [
        "name", "version", "cloud_img", "size"
    ]

    # Generate the image configuration
    for build, build_data in architecture.items():
        for attr in required_attributes:
            if attr not in build_data:
                print("Missing required attribute '{}': in {}".format(attr, build_data))
                exit(-2)

        # Download the cloud_img
        cloud_img_url = build_data.get("cloud_img", None)
        cloud_img_filename = wget.detect_filename(cloud_img_url)
        cloud_img_path = os.path.join("image", cloud_img_filename)
        if not exists(cloud_img_path):
            cloud_img_path = wget.download(cloud_img_url, cloud_img_path)

        # Resize the cloud image
        img_size = build_data.get("size", None)
        command = ["qemu-img", "resize", cloud_img_path, img_size]
        result = run(command)
        if result["returncode"] != 0:
            print("Failed to resize the downloaded image: {}".format(result["stderr"]))

        # Setup the cloud init configuration
        

        # Load and configure the cloud_img template file
        kickstart_template_file = build_data.get("kickstart_file")
        kickstart_content = load(kickstart_template_file)
        if not kickstart_content:
            print(
                "Could not find the kickstart template file: {}".format(
                    kickstart_template_file
                )
            )
            exit(-3)
        kickstart_template = Template(kickstart_content)

        # Kickstart template paramaters
        template_parameters = {}
        build_parameters = build_data.get("parameters", None)
        if build_parameters:
            template_parameters.update(**build_parameters)

        # Output the formatted and paramaterized kickstart file
        kickstart_output_content = kickstart_template.render(**template_parameters)
        kickstart_output_file = os.path.join("config", "ks.cfg")

        # Save rendered template to a file
        write(kickstart_output_file, kickstart_output_content)
        print("Generated kickstart file: {}".format(kickstart_output_file))

    # Generate the GOCD build config
    for build, build_data in architecture.items():
        name = build_data.get("name", None)
        version = build_data.get("version", None)
        materials = get_materials(name)

        build_version_name = "{}-{}".format(name, version)
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

    # Update the Makefile such that it contains every image
    # image
    # makefile_path = os.path.join(current_dir, makefile)
    # makefile_content = load(makefile_path, readlines=True)
    # new_makefile_content = []

    # for line in makefile_content:
    #     if "ALL_IMAGES:=" in line:
    #         images_declaration = "ALL_IMAGES:="
    #         for image in images:
    #             images_declaration += "{} ".format(image)
    #         new_makefile_content.append(images_declaration)
    #         new_makefile_content.append("\n")
    #     else:
    #         new_makefile_content.append(line)

    # Write the new makefile content to the Makefile
    # write(makefile_path, new_makefile_content)
    # print("Generated a new Makefile in: {}".format(makefile_path))
