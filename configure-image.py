import argparse
import os
from src.common.defaults import CLOUD_CONFIG_DIR, IMAGE_CONFIG_DIR
from src.utils.job import run
from src.utils.io import exists, makedirs

SCRIPT_NAME = __file__


def generate_image_configuration(
    user_data_path, metadata_path, vendordata_path, output_path
):
    # Setup the cloud init configuration
    # Generate a disk with user-supplied data
    if not exists(user_data_path):
        print(
            "Failed to find a cloud-init user-data file at: {}".format(user_data_path)
        )
        return False

    if not exists(metadata_path):
        print("Failed to find a cloud-init meta-data file at: {}".format(metadata_path))
        return False

    if not exists(vendordata_path):
        print(
            "Failed to find a cloud-init vendor-data file at: {}".format(
                vendordata_path
            )
        )
        return False

    # Generated the configuration image
    localds_command = [
        "cloud-localds",
        output_path,
        user_data_path,
        metadata_path,
        "-V",
        vendordata_path,
    ]
    localds_result = run(localds_command)
    if localds_result["returncode"] != 0:
        print("Failed to generate cloud-localds: {}".format(localds_result))
        return False
    return True


def configure_image(image, cloud_init_config_path):
    """Configures the image by booting the image with qemu to allow
    for cloud init to apply the configuration"""

    configure_command = [
        "qemu-kvm",
        "-name",
        "vm",
        "-cpu",
        "IvyBridge",
        "-m",
        "2048",
        "-nographic",
        "-hda",
        image,
        "-hdb",
        cloud_init_config_path,
    ]
    configure_result = run(configure_command)
    if configure_result["returncode"] != 0:
        print("Failed to configure image: {}".format(configure_result))
        return False
    return True


def reset_image(image):
    """Resets the image such that it is ready to be started
    in production"""
    # Ensure that the virt-sysprep doesn't try to use libvirt
    # but qemu instead
    # LIBGUESTFS_BACKEND=direct
    reset_command = ["virt-sysprep", "-a", image]
    reset_result = run(reset_command)
    if reset_result["returncode"] != 0:
        print("Failed to reset image: {}".format(reset_result))
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog=SCRIPT_NAME)
    parser.add_argument(
        "--image-path",
        default="vmdisks/image.qcow2",
        help="The path to the image that is to be configured",
    )
    parser.add_argument(
        "--config-user-data-path",
        default=os.path.join(CLOUD_CONFIG_DIR, "user-data"),
        help="The path to the cloud-init user-data configuration file",
    )
    parser.add_argument(
        "--config-meta-data-path",
        default=os.path.join(CLOUD_CONFIG_DIR, "meta-data"),
        help="The path to the cloud-init meta-data configuration file",
    )
    parser.add_argument(
        "--config-vendor-data-path",
        default=os.path.join(CLOUD_CONFIG_DIR, "vendor-data"),
        help="The path to the cloud-init vendor-data configuration file",
    )
    parser.add_argument(
        "--config-seed-output-path",
        default=os.path.join(IMAGE_CONFIG_DIR, "seed.img"),
        help="""The path to the cloud-init output seed image file that is generated
        based on the data defined in the user-data, meta-data, and vendor-data configs""",
    )

    args = parser.parse_args()

    image_path = args.image_path
    user_data_path = args.config_user_data_path
    meta_data_path = args.config_meta_data_path
    vendor_data_path = args.config_vendor_data_path
    seed_output_path = args.config_seed_output_path

    # Ensure that the cloud init seed directory exists
    if not exists(os.path.dirname(seed_output_path)):
        created, msg = makedirs(os.path.dirname(seed_output_path))
        if not created:
            print(msg)
            exit(1)

    generated = generate_image_configuration(
        user_data_path, meta_data_path, vendor_data_path, seed_output_path
    )
    if not generated:
        print("Failed to generate the image configuration")
        exit(2)

    configured = configure_image(image_path, seed_output_path)
    if not configured:
        print("Failed to configure image: {}".format(image_path))
        exit(3)

    reset = reset_image(image_path)
    if not reset:
        print("Failed to reset image: {}".format(image_path))
        exit(4)