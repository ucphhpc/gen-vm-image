#!/bin/bash

MYSECRET=`echo "password" | base64`
virsh secret-set-value $1 $MYSECRET