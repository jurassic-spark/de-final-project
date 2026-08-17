#!/usr/bin/env bash

set -euo pipefail

LAYER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

rm -rf "${LAYER_DIR}/build"

mkdir -p "${LAYER_DIR}/build/python"

docker run --rm \
    --user "$(id -u):$(id -g)" \
    -e HOME=/tmp \
    -v "${LAYER_DIR}:/layer" \
    python:3.14 \
    python -m pip install \
        -r /layer/requirements.txt \
        -t /layer/build/python