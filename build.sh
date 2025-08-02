#!/usr/bin/env bash
set -e

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

# Create virtual environment
uv venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .