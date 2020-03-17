#!/bin/bash

FILE1=full/path/to/iot-app-server/opc-plugin/Dockerfile
FILE2=full/path/to/iot-app-server/opc-plugin/opcPlugin.py
FILE3=full/path/to/iot-app-server/opc-plugin/package_config.ini
if [ -f "$FILE1" -a -f "$FILE2" -a -f "$FILE3" ]; then
	echo "$FILE1"
	echo "$FILE2"
	echo "$FILE3"
	echo "are present. Commencing packaging"
        docker build -t IOx-Application .
	ioxclient docker package -a IOx-Application .
else
	echo "One or more of the files not present. Cannot commence packaging"
fi

