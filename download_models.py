#!/usr/bin/env python3
"""
Download AI models for PixPort
This script downloads the required models for background removal
"""

import os
import sys

def download_models():
    """Download required AI models for background removal"""
    try:
        print("📥 Downloading AI models for PixPort...")
        
        # Import rembg here to handle import errors gracefully
        from rembg import new_session
        
        # Only download u2netp model for Railway (smallest and most efficient)
        model_name = 'u2netp'
        print(f"⏳ Downloading {model_name}...")
        session = new_session(model_name)
        print(f"✅ {model_name} downloaded successfully!")
        
        print("🎉 Model download complete!")
        return True
        
    except ImportError as e:
        print(f"⚠️ Import error: {str(e)}")
        print("Models will be downloaded when the app starts.")
        return False
    except Exception as e:
        print(f"⚠️ Warning: Could not download models: {str(e)}")
        print("Models will be downloaded when needed.")
        return False

def test_model_availability():
    """Test if at least one model is available"""
    try:
        from rembg import new_session
        session = new_session('u2netp')
        print("✅ AI models are ready for use")
        return True
    except Exception as e:
        print(f"⚠️ Models will be downloaded on first use: {str(e)}")
        return False

if __name__ == "__main__":
    success = download_models()
    if success:
        test_model_availability()
