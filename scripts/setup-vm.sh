#!/bin/bash

ROCKY_IMAGE=Rocky-9.1-x86_64-minimal.iso
OS_VARIANT=rocky9
VM_NAME=rocky-linux-9
IMAGE_DIR=/var/lib/libvirt/images
VOLUME_PATH=/vmdisks
VOLUME_NAME=rhel-9.qcow2

CONFIG_DIR=../config

virt-install \
  --name=$VM_NAME \
  --memory=1024 \
  --vcpus=1 \
  --location $IMAGE_DIR/$ROCKY_IMAGE \
  --disk vol=$VOLUME_PATH/$VOLUME_NAME  \
  --network bridge=virbr0 \
  --graphics=none \
  --os-variant=$OS_VARIANT \
  --console pty,target_type=serial \
  --initrd-inject $CONFIG_DIR/ks.cfg \
  --extra-args "inst.ks=file:/ks.cfg console=tty0 console=ttyS0,115200n8"