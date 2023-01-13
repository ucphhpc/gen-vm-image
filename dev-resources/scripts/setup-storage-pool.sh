#!/bin/bash

virsh pool-define define-storage-pool.xml
virsh pool-start define-storage-pool.xml
virsh pool-autostart define-storage-pool.xml
