import argparse
import os
import subprocess
import multiprocessing as mp
from src.common.defaults import CLOUD_CONFIG_DIR, IMAGE_CONFIG_DIR, IMAGE_DIR
from src.utils.job import run, run_popen
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


def configure_vm(image, configuration_path, cpu_model, output_queue):
    """This launches a subprocess that configures the VM image on boot."""
    configure_command = [
        "qemu-kvm",
        "-name",
        "vm",
        "-cpu",
        cpu_model,
        "-m",
        "2048",
        "-nographic",
        # https://unix.stackexchange.com/questions/426652/connect-to-running-qemu-instance-with-qemu-monitor
        # Allow the qemu instance to be shutdown via a socket signal
        "-monitor",
        "unix:qemu-monitor-socket,server,nowait",
        "-hda",
        image,
        "-hdb",
        configuration_path,
    ]
    configuring_results = run_popen(
        configure_command, stdout=subprocess.PIPE, universal_newlines=True
    )
    for line in iter(configuring_results["output"].readline, ""):
        output_queue.put(line)
    configuring_results["output"].close()
    return_code = configuring_results["wait"]()
    if return_code:
        raise subprocess.CalledProcessError(return_code, configure_command)
    return True


def shutdown_vm(q):
    value = q.get()
    # [  518.433552] cloud-init[1188]: Cloud-init v. 22.1-5.el9.0.1 finished at Fri, 10 Mar 2023 06:55:05 +0000. Datasource DataSourceNoCloud [seed=/dev/sdb][dsmode=net].  Up 517.94 seconds
    if "Cloud-init" in value and "finished at" in value:
        print("Found finish message: {}".format(value))
        shutdown_cmd = [
            "echo",
            "system_powerdown",
            "|",
            "socat",
            "-",
            "unix-connect:/var/lib/go-agent/pipelines/sif-compute-base/sif-vm-images/qemu-monitor-socket",
        ]
        shutdown_result = run(shutdown_cmd)
    if shutdown_result["returncode"] != 0:
        raise subprocess.CalledProcessError(
            "Failed to shutdown the configured VM: {}".format(shutdown_result),
            shutdown_cmd,
        )


def configure_image(image, configuration_path, cpu_model="host"):
    """Configures the image by booting the image with qemu to allow
    for cloud init to apply the configuration"""

    queue = mp.Queue()
    configuring_vm = mp.Process(
        target=configure_vm,
        args=(
            image,
            configuration_path,
            cpu_model,
            queue,
        ),
    )
    shutdowing_vm = mp.Process(target=shutdown_vm, args=(queue,))

    # Start the sub processes
    configuring_vm.start()
    shutdowing_vm.start()

    # Wait for them to finish
    shutdowing_vm.join()
    configuring_vm.join()
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
        "--image-input-path",
        default=os.path.join(IMAGE_DIR, "image.qcow2"),
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
    parser.add_argument(
        "--qemu-cpu-model",
        default="host",
        help="The default cpu model for configuring the image",
    )

    args = parser.parse_args()

    image_path = args.image_input_path
    user_data_path = args.config_user_data_path
    meta_data_path = args.config_meta_data_path
    vendor_data_path = args.config_vendor_data_path
    seed_output_path = args.config_seed_output_path
    qemu_cpu_model = args.qemu_cpu_model

    # Ensure that the required output directories exists
    image_output_dir = os.path.dirname(image_path)
    image_config_dir = os.path.dirname(seed_output_path)

    for d in [image_output_dir, image_config_dir]:
        if not exists(IMAGE_CONFIG_DIR):
            created, msg = makedirs(IMAGE_CONFIG_DIR)
            if not created:
                print(msg)
                exit(1)

    generated = generate_image_configuration(
        user_data_path, meta_data_path, vendor_data_path, seed_output_path
    )
    if not generated:
        print("Failed to generate the image configuration")
        exit(2)

    configured = configure_image(image_path, seed_output_path, cpu_model=qemu_cpu_model)
    if not configured:
        print("Failed to configure image: {}".format(image_path))
        exit(3)

    reset = reset_image(image_path)
    if not reset:
        print("Failed to reset image: {}".format(image_path))
        exit(4)
