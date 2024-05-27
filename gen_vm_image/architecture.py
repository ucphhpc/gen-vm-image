import yaml
from gen_vm_image.common.errors import (
    PATH_NOT_FOUND_ERROR,
    PATH_NOT_FOUND_ERROR_MSG,
    PATH_LOAD_ERROR,
    PATH_LOAD_ERROR_MSG,
    MISSING_ATTRIBUTE_ERROR,
    MISSING_ATTRIBUTE_ERROR_MSG,
)
from gen_vm_image.utils.io import exists, load


def load_architecture(architecture_path):
    if not exists(architecture_path):
        return PATH_NOT_FOUND_ERROR, PATH_NOT_FOUND_ERROR_MSG.format(
            architecture_path, "Failed to find the architecture file."
        )
    architecture = load(architecture_path, handler=yaml, Loader=yaml.FullLoader)
    if not architecture:
        return PATH_LOAD_ERROR, PATH_LOAD_ERROR_MSG.format(
            architecture_path, "Failed to load the architecture file."
        )
    return architecture, None


def correct_architecture_structure(architecture):
    owner = architecture.get("owner", None)
    if not owner:
        return MISSING_ATTRIBUTE_ERROR, MISSING_ATTRIBUTE_ERROR_MSG.format(
            "owner", architecture
        )
    images = architecture.get("images", None)
    if not images:
        return MISSING_ATTRIBUTE_ERROR, MISSING_ATTRIBUTE_ERROR_MSG.format(
            "images", architecture
        )

    required_attributes = ["name", "version", "size"]
    for image_name, image_data in images.items():
        for attribute in required_attributes:
            if attribute not in image_data:
                return MISSING_ATTRIBUTE_ERROR, MISSING_ATTRIBUTE_ERROR_MSG.format(
                    attribute, image_name
                )
    return True, None
