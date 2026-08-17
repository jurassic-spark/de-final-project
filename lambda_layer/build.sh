#!/usr/bin/env bash

# Exit if a command fails, a variable is undefined, or a pipeline fails.
set -euo pipefail

# Get the absolute path of the directory containing this script.
LAYER_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Remove any previous layer build.
rm -rf "${LAYER_DIR}/build"

# Create the AWS Lambda Python layer directory structure.
mkdir -p "${LAYER_DIR}/build/python"

# Build the layer using Python 3.13 in a Linux container.
docker run --rm \
    -v "${LAYER_DIR}:/layer" \
    python:3.13 \
    python -m pip install \
        -r /layer/requirements.txt \
        -t /layer/build/python