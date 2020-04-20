  #!/bin/sh


mkdir opc-plugin/iox-opc-aarch64
docker save -o rootfs.tar iox-opc
mv rootfs.tar opc-plugin/iox-opc-aarch64/

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
chmod -x  dopc-plugin/ioxclient 
opc-plugin/ioxclient package opc-plugin/iox-opc-aarch64
