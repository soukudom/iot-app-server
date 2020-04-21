#!/bin/sh

sudo apt-get install qemu-user qemu-user-static
echo 'qemu installed'

echo 'global:
  version: "1.0"
  active: default
  debug: false
  fogportalprofile:
    fogpip: ""
    fogpport: ""
    fogpapiprefix: ""
    fogpurlscheme: ""
  dockerconfig:
    server_uri: ""
    api_version: ""
author:
  name: |
    Cisco
  link: www.cisco.com
profiles: {default: {host_ip: 127.0.0.1, host_port: 8443, auth_keys: cm9vdDo=, auth_token: "",
    local_repo: /software/downloads, api_prefix: /iox/api/v2/hosting/, url_scheme: https,
    ssh_port: 22, rsa_key: "", certificate: "", cpu_architecture: "", middleware: {
      mw_ip: "", mw_port: "", mw_baseuri: "", mw_urlscheme: "", mw_access_token: ""}}}' >  /home/travis/.ioxclientcfg.yaml

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
opc-plugin/ioxclient package opc-plugin/iox-opc-aarch64
