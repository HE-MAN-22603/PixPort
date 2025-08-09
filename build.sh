#!/bin/bash
# Build script for Railway deployment
# Optimized for fast build times and memory constraints

echo "🚂 Starting Railway build process..."

# Set build environment variables
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1  
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Update system packages quickly
echo "📦 Installing system dependencies..."
apt-get update -qq
apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

# Upgrade pip and install wheel for faster builds
echo "🔧 Upgrading pip and build tools..."
pip install --no-cache-dir --upgrade pip wheel setuptools

# Install Python packages
echo "🐍 Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

# Create necessary directories
echo "📁 Creating application directories..."
mkdir -p /tmp/pixport/uploads
mkdir -p /tmp/pixport/processed

# Verify installation
echo "✅ Verifying installation..."
python -c "
import flask
import rembg
import cv2
import PIL
from app import create_app
print('✅ All core dependencies installed successfully')
print(f'Flask version: {flask.__version__}')
"

echo "🎉 Build completed successfully!"
