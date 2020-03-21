#!/bin/bash

FILE1=/c/Simac/IOx/iot-app-server/opc-plugin/Dockerfile
FILE2=/c/Simac/IOx/iot-app-server/opc-plugin/opcPlugin.py
FILE3=/c/Simac/IOx/iot-app-server/opc-plugin/package_config.ini
FILE4=/c/Simac/IOx/iot-app-server/opc-plugin/requirements.txt
if [ -f "$FILE1" -a -f "$FILE2" -a -f "$FILE3" -a -f "$FILE4" ]; then
	echo "$FILE1"
	echo "$FILE2"
	echo "$FILE3"
	echo "$FILE4"
	echo "are present. Commencing packaging"
	docker build -t iox-opcua-app:1.0 .
	rm -rf iox-opc-aarch64 && mkdir iox-opc-aarch64
	docker save -o rootfs.tar iox-opcua-app:1.0
	mv rootfs.tar iox-opc-aarch64/
else
	echo "One or more of the files not present. Cannot create container"
fi

echo 'descriptor-schema-version: "2.4"

info:
  name: iox_opc_app
  description: "simple lxc plc polling app"
  version: "1.0"
  author-link: "http://www.cisco.com"
  author-name: "Dominik Soukup"

app:
  cpuarch: "aarch64"
  type: "lxc"
  kernel-version: "1.0"
  resources:
    profile: c1.tiny

  startup:
    rootfs: rootfs.tar
    target: "opcPlugin.py"' > package.yaml

mv package.yaml iox-opc-aarch64/

ioxclient package iox-opc-aarch64 .
echo 'IOx Application Package tar file created. Ready to upload to Cisco Kinetic GMM'
