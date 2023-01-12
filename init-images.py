import argparse
import os
import yaml
from jinja2 import Template
from setup.io import load, write, copy

current_dir = os.path.abspath(os.path.dirname(__file__))
parent_dir = os.path.dirname(current_dir)

PACKAGE_NAME = "generate-gocd-config"
REPO_NAME = "sif-vm-images"
gocd_format_version = 10


def get_pipelines(images):
    pipelines = []
    for image, versions in images.items():
        for version, build_data in versions.items():
            version_name = "{}-{}".format(image, version)
            pipelines.append(version_name)
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
        "template": "vm_image",
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


def get_materials(image, upstream_pipeline=None, stage=None):
    materials = {}
    common_materials = get_common_materials()
    materials.update(common_materials)
    if upstream_pipeline and stage:
        upstream_materials = get_upstream_materials(image, upstream_pipeline, stage)
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

    images = architecture.get("architecture", None)
    if not images:
        print("Failed to find the architecture in: {}".format(architecture_path))
        exit(-1)

    list_images = list(images.keys())
    num_images = len(list_images) - 1

    print()
    # Get all pipelines
    pipelines = get_pipelines(images)

    # GOCD environment
    common_environments = get_common_environment(pipelines)

    # Common GOCD pipeline params
    common_pipeline_attributes = get_common_pipeline()

    generated_config = {
        "format_version": gocd_format_version,
        **common_environments,
        "pipelines": {},
    }

    # Generate the image configuration
    for image, versions in images.items():
        for version, build_data in versions.items():
            parent = build_data.get("parent", None)
            if not parent:
                print("Missing required parent for image: {}".format(image))
                exit(-2)

            if "owner" not in parent:
                print("Missing required parent attribute 'owner': {}".format(image))
                exit(-2)

            if "image" not in parent:
                print("Missing required parent attribute 'image': {}".format(image))
                exit(-2)

            if "tag" not in parent:
                print("Missing required parent attribute 'tag': {}".format(image))
                exit(-2)

            parent_image = "{}/{}:{}".format(
                parent["owner"], parent["image"], parent["tag"]
            )

            template_file = build_data.get("file", "{}/Dockerfile.j2".format(image))
            output_file = "{}/Dockerfile.{}".format(image, version)
            template_content = load(template_file)
            if not template_content:
                print("Could not find the template file: {}".format(template_file))
                exit(-3)

            template = Template(template_content)
            output_content = None
            template_parameters = {"parent": parent_image}

            extra_template_file = build_data.get("extra_template", None)
            if extra_template_file:
                extra_template = load(extra_template_file)
                template_parameters["extra_template"] = extra_template

                # Check for additional template files that should
                # be copied over.
                extra_template_files = build_data.get("extra_template_files", [])
                target_dir = os.path.join(current_dir, image)
                for extra_file_path in extra_template_files:
                    extra_file_name = extra_file_path.split("/")[-1]
                    success, msg = copy(
                        extra_file_path, os.path.join(target_dir, extra_file_name)
                    )
                    if not success:
                        print(msg)
                        exit(-4)

            build_parameters = build_data.get("parameters", None)
            if build_parameters:
                template_parameters.update(**build_parameters)

            # Format the jinja2 template
            output_content = template.render(**template_parameters)

            # Save rendered template to a file
            write(output_file, output_content)
            print("Generated the file: {}".format(output_file))

    # Generate the GOCD build config
    for image, versions in images.items():
        for version, build_data in versions.items():
            parent = build_data.get("parent", None)
            if (
                parent
                and "pipeline_dependent" in parent
                and parent["pipeline_dependent"]
            ):
                parent_pipeline = "{}-{}".format(parent["image"], parent["tag"])
                materials = get_materials(
                    image, upstream_pipeline=parent_pipeline, stage="push"
                )
            else:
                materials = get_materials(image)

            image_version_name = "{}-{}".format(image, version)
            image_pipeline = {
                **common_pipeline_attributes,
                "materials": materials,
                "parameters": {
                    "IMAGE": image,
                    "IMAGE_PIPELINE": image_version_name,
                    "DEFAULT_TAG": version,
                    "SRC_DIRECTORY": REPO_NAME,
                    "TEST_DIRECTORY": REPO_NAME,
                    "PUSH_DIRECTORY": "publish-docker-scripts",
                    "COMMIT_TAG": "GO_REVISION_UCPHHPC_IMAGES",
                    "ARGS": "",
                },
            }
            generated_config["pipelines"][image_version_name] = image_pipeline

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
