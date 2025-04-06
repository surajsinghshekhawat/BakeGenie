#!/bin/bash
# exit on error
set -o errexit

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install --no-cache-dir -r requirements.txt

# Create necessary directories
mkdir -p static/uploads
mkdir -p static/images
mkdir -p database

# Set permissions
chmod -R 755 static
chmod -R 755 database 