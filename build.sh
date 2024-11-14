#!/bin/bash
# Create necessary directories
mkdir -p static/css
mkdir -p static/js
mkdir -p static/images

# Copy static files if they exist
if [ -d "src/static" ]; then
    cp -r src/static/* static/
fi 