# FaceSwap CPU container (experimental).
#
# Builds the deepfakes/faceswap repo inside Ubuntu 24.04 with Python 3.12.
# The container stays alive so the operator can run the extract/train/convert
# workflow and the main app can invoke it via FACESWAP_COMMAND.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV FACESWAP_BACKEND=cpu

RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 python3 python3-pip python3-venv python3-tk git curl ca-certificates && \
    rm -rf /var/lib/apt/lists/* && \
    ln -s $(which python3) /usr/local/bin/python

RUN git clone --depth 1 --no-single-branch https://github.com/deepfakes/faceswap.git /faceswap
WORKDIR /faceswap

# Use a venv to avoid conflicting with the Ubuntu system packages.
RUN python -m venv /opt/faceswap-venv && \
    /opt/faceswap-venv/bin/pip install --upgrade pip && \
    /opt/faceswap-venv/bin/pip --no-cache-dir install \
        -r ./requirements/requirements_cpu.txt

ENV PATH=/opt/faceswap-venv/bin:$PATH
CMD ["tail", "-f", "/dev/null"]
