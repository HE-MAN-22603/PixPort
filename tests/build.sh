#!/bin/bash
echo "🚀 Building PixPort for Railway..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download AI models (optional, will fallback if fails)
echo "🤖 Downloading AI models..."
python download_models.py || echo "⚠️ Model download skipped, will download on first use"

echo "✅ Build complete!"
