#!/usr/bin/env python3
"""
Download AI models for PixPort
This script downloads the required models for background removal
"""

import os
import sys
from rembg import new_session

def download_models():
    """Download required AI models for background removal"""
    models = ['u2net', 'u2netp', 'silueta']
    
    print("📥 Downloading AI models for PixPort...")
    
    for model_name in models:
        try:
            print(f"⏳ Downloading {model_name}...")
            session = new_session(model_name)
            print(f"✅ {model_name} downloaded successfully!")
        except Exception as e:
            print(f"❌ Error downloading {model_name}: {str(e)}")
            continue
    
    print("🎉 Model download complete!")

if __name__ == "__main__":
    download_models()
