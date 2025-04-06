#!/usr/bin/env bash

# Exit on error
set -o errexit

# Set environment variables for pip
export PIP_NO_BUILD_ISOLATION=true
export PIP_ONLY_BINARY=:all:

# Install Python 3.10
apt-get update
apt-get install -y python3.10 python3.10-dev python3.10-venv

# Create a virtual environment with Python 3.10
python3.10 -m venv .venv
source .venv/bin/activate

# Verify Python version
python --version

# Upgrade pip
python -m pip install --upgrade pip

# Install numpy first with specific version and binary only
pip install --no-cache-dir --only-binary=numpy numpy==1.23.5

# Install other dependencies
pip install --no-cache-dir -r requirements.txt

# Create necessary directories
mkdir -p static/uploads
mkdir -p static/images
mkdir -p database

# Set permissions
chmod -R 755 static
chmod -R 755 database 