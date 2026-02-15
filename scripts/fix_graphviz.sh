#!/usr/bin/env bash
set -euo pipefail

# Generate Graphviz plugin config files if missing
# Needed for graphviz conda-forge feedstock for osx-arm64
# https://github.com/conda-forge/graphviz-feedstock/issues/152

compgen -G "$CONDA_PREFIX/lib/graphviz/config*" > /dev/null \
    || dot -c \
    || true
