#!/bin/bash

XML_DIR=../xmls
POOL_NAME=vmdisks
IMAGE_NAME=rocky9.qcow2
IMAGE_PATH=/var/lib/libvirt/images/${IMAGE_NAME}
IMAGE_SIZE=20G

# create the image
qemu-img create -o preallocation=metadata -f qcow2 ${IMAGE_PATH} ${IMAGE_SIZE}