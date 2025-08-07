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
    # Primary model for production
    primary_models = ['u2net']
    # Additional models (optional)
    additional_models = ['u2netp', 'silueta']
    
    print("📥 Downloading AI models for PixPort...")
    
    # Download primary model first
    for model_name in primary_models:
        try:
            print(f"⏳ Downloading {model_name} (primary)...")
            session = new_session(model_name)
            print(f"✅ {model_name} downloaded successfully!")
        except Exception as e:
            print(f"❌ Error downloading {model_name}: {str(e)}")
            # Don't exit on error, continue with other models
            continue
    
    # Download additional models (less critical)
    for model_name in additional_models:
        try:
            print(f"⏳ Downloading {model_name} (additional)...")
            session = new_session(model_name)
            print(f"✅ {model_name} downloaded successfully!")
        except Exception as e:
            print(f"⚠️ Warning: Could not download {model_name}: {str(e)}")
            # Continue with other models
            continue
    
    print("🎉 Model download complete!")
    return True

def test_model_availability():
    """Test if at least one model is available"""
    try:
        session = new_session('u2net')
        print("✅ AI models are ready for use")
        return True
    except Exception as e:
        print(f"❌ Models not ready: {str(e)}")
        return False

if __name__ == "__main__":
    success = download_models()
    test_model_availability()
