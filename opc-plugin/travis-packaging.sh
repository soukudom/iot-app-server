#!/bin/sh

sudo apt-get install qemu-user qemu-user-static
echo 'qemu installed'

FILE1=opc-plugin/Dockerfile
FILE2=opc-plugin/opcPlugin.py
FILE3=opc-plugin/package_config.ini
FILE4=opc-plugin/requirements.txt
if [ -f "$FILE1" -a -f "$FILE2" -a -f "$FILE3" -a -f "$FILE4" ]; then
	echo "$FILE1"
	echo "$FILE2"
	echo "$FILE3"
        echo "$FILE4"
	echo "are present. Commencing packaging"
        docker build --tag iox-opc opc-plugin
        rm -rf opc-plugin/iox-opc-aarch64 && mkdir opc-plugin/iox-opc-aarch64
        docker save -o rootfs.tar iox-opc
        mv rootfs.tar opc-plugin/iox-opc-aarch64/
else
	echo "One or more of the files not present. Cannot create container"
fi

echo 'descriptor-schema-version: "2.7"

info:
  name: "iox_opc_app"
  description: "OPC/UA to MQTT plugin"
  version: "1.0"
  author-link: "http://www.cisco.com"
  author-name: "CSAP Tiger Team"

app:
  cpuarch: "aarch64"
  type: "docker"
  resources:
    profile: c1.tiny
    network:
      - interface-name: eth0
        ports: {}

  startup:
    rootfs: rootfs.tar
    target: ["python3","/opcPlugin.py"]' > opc-plugin/package.yaml

mv opc-plugin/package.yaml opc-plugin/iox-opc-aarch64/
cp opc-plugin/package_config.ini opc-plugin/iox-opc-aarch64
chmod 777 opc-plugin/ioxclient 
opc-plugin/ioxclient package opc-plugin/iox-opc-aarch64
