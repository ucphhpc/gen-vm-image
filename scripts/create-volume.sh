#!/bin/bash

XML_DIR=../xmls
POOL_NAME=vmdisks

virsh vol-create $POOL_NAME $XML_DIR/create-volume.xml
