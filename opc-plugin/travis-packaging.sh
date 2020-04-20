  #!/bin/sh


mv ioxclient /usr/local/bin

mkdir iox-opc-aarch64
docker save -o rootfs.tar iox-opc
mv rootfs.tar iox-opc-aarch64/

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
    target: ["python3","/opcPlugin.py"]' > package.yaml

mv package.yaml iox-opc-aarch64/
cp package_config.ini iox-opc-aarch64
ioxclient package iox-opc-aarch64
echo 'IOx Application Package tar file created. Ready to upload to Cisco Kinetic GMM'
