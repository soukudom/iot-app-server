FROM multiarch/qemu-user-static as qemu
FROM arm64v8/alpine:3.7
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin

RUN apk update
RUN apk add --upgrade apk-tools
RUN apk upgrade --available
RUN apk add --no-cache python3 && \
    pip3 install --upgrade pip setuptools
RUN apk add --no-cache --virtual .build-deps \
        g++ \
	gcc \
	libxml2 \
	libxml2-dev \
	py3-lxml && \
    apk add libxslt-dev

COPY requirements.txt .
COPY opcPlugin.py .
COPY package_config.ini .

RUN chmod 777 opcPlugin.py
RUN chmod 644 package_config.ini
RUN chmod 644 requirements.txt
RUN pip3 install -r requirements.txt

ENTRYPOINT python3 opcPlugin.py
