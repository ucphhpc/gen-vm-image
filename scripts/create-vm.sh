#!/bin/bash

qemu-system-x86_64 \
    -net nic \
    -net user \
    -m 1024 \
    -nographic \
    -hda image/Rocky-9-GenericCloud-Base.latest.x86_64.qcow2 \
    -hdb cloud-init-config/seed.img \
    -device pvpanic
