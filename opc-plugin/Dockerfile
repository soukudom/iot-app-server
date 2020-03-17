#Using Cisco Docker image for IR1101 - with dev toolset for extended functionality
FROM devhub-docker.cisco.com/iox-docker/ir1101/base-rootfs-dev

RUN opkg update && opkg install python3
CMD pip3 install --upgrade pip3
CMD pip3 install opcua
CMD pip3 install paho-mqtt
CMD pip3 install configparser

COPY opcPlugin.py /usr/bin/opcPlugin.py
COPY package_config.ini /usr/bin/package_config.ini
RUN chmod 777 /usr/bin/opcPlugin.py
RUN chmod 644 /usr/bin/package_config.ini

CMD /usr/bin/opcPlugin.py
