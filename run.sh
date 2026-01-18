#!/bin/bash
# Simple runner script for dotfiles installation using uv

set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Ensure latest production Python is installed
uv python install --latest

# Run the dotfiles script with uv using latest Python
uv run --python latest dotfiles.py "$@"
