FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    openscad \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# BOSL2 library included by the OpenSCAD design
RUN mkdir -p /usr/share/openscad/libraries \
    && git clone --depth 1 https://github.com/BelfryScad/BOSL2.git /usr/share/openscad/libraries/BOSL2

# Verifier dependencies (the verifier runs in this same container)
RUN pip3 install --no-cache-dir --break-system-packages \
    pytest==8.4.1 \
    trimesh \
    numpy \
    scipy \
    rtree \
    shapely \
    manifold3d \
    python-fcl

WORKDIR /workspace
