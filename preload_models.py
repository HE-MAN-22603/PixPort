#!/usr/bin/env python3
"""
Model Preloading Script for Docker Build
Attempts to download and cache AI models during container build
Includes fixes for pymatting/numba cache issues
"""

import os
import sys

# Set environment variables to fix pymatting/numba issues before importing
os.environ['NUMBA_DISABLE_JIT'] = '1'
os.environ['NUMBA_CACHE_DIR'] = '/tmp/.numba_cache'
os.environ['NUMBA_DISABLE_PERFORMANCE_WARNINGS'] = '1'

print("🚀 Pre-downloading AI models for faster cold starts...")
print("🔧 Numba JIT disabled to avoid cache issues in containers")

try:
    # Import and trigger model download
    print("📦 Importing rembg...")
    from rembg import new_session
    print("📥 Downloading isnet-general-use model...")
    
    # Create session to trigger download
    session = new_session('isnet-general-use')
    print("✅ Model downloaded and cached successfully!")
    
    # Test basic functionality
    print("🔍 Testing model session...")
    if hasattr(session, 'predict') or hasattr(session, 'remove'):
        print("✅ Model session is functional!")
    else:
        print("⚠️ Model session created but functionality unclear")
    
    # Free memory
    del session
    print("✅ Model preload completed successfully!")
    
except ImportError as e:
    print(f"❌ rembg not available: {e}")
    print("ℹ️ Models will be downloaded on first request.")
    
except Exception as e:
    print(f"❌ Model download failed: {e}")
    print(f"🔍 Error type: {type(e).__name__}")
    if "pymatting" in str(e).lower() or "numba" in str(e).lower():
        print("🔧 This appears to be a pymatting/numba issue.")
        print("🔧 The runtime environment variables should resolve this.")
    print("ℹ️ Models will be downloaded on first request.")
    
print("🏁 Model preloading script finished.")
