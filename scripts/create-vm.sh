#!/bin/bash

virt-install \
    --name "vm" \
    --disk "vmdisks/Rocky-disk.qcow2",device=disk,bus=virtio \
    --disk "vmdisks/seed.img",device=cdrom \
    --os-variant="rocky9" \
    --virt-type kvm \
    --graphics none \
    --vcpus "2" \
    --memory "2048" \
    --console pty,target_type=serial \
    --import
