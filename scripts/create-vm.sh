#!/bin/bash

virt-install \
    --name "vm" \
    --disk "/var/lib/libvirt/images/saga-base.qcow2",device=disk,bus=virtio \
    --boot hd \
    --boot loader=/usr/share/edk2/ovmf/OVMF_CODE.fd,loader.readonly=yes,loader.type=pflash \
    --os-variant="rocky9" \
    --launchSecurity type=sev,kernelHashes=yes,policy=0x0001,cbitpos=47,reducedPhysBits=1 \
    --virt-type kvm \
    --network bridge="br200" \
    --machine q35 \
    --nographic \
    --cpu host \
    --vcpus "2" \
    --memory "2048" \
    --memorybacking locked=on \
    --console pty,target_type=serial \
    --import \
    --autostart \
    --cloud-init user-data=cloud-init-config/user-data,meta-data=cloud-init-config/meta-data
