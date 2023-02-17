#!/bin/bash

XML_DIR=../xmls
POOL_NAME=vmdisks
STORAGE_POOL_DIR=/var/lib/libvirt/$POOL_NAME

virsh pool-define $XML_DIR/define-storage-pool.xml

mkdir -p $STORAGE_POOL_DIR

virsh pool-start $POOL_NAME
virsh pool-autostart $POOL_NAME