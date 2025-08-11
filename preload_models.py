#!/usr/bin/env python3
"""
Model Preloading Script for Docker Build
Attempts to download and cache AI models during container build
"""

print("Pre-downloading AI models for faster cold starts...")

try:
    # Import and trigger model download
    from rembg import new_session
    print("Downloading isnet-general-use model...")
    
    # Create session to trigger download
    session = new_session('isnet-general-use')
    print("Model downloaded and cached successfully!")
    
    # Test basic functionality
    print("Testing model session...")
    if hasattr(session, 'predict') or hasattr(session, 'remove'):
        print("Model session is functional!")
    
    # Free memory
    del session
    print("Model preload completed successfully!")
    
except ImportError as e:
    print(f"rembg not available: {e}")
    print("Models will be downloaded on first request.")
    
except Exception as e:
    print(f"Model download failed: {e}")
    print("Models will be downloaded on first request.")
    
print("Model preloading script finished.")
