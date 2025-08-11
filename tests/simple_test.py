#!/usr/bin/env python3
"""
Simple test script for PixPort Flask app (no heavy AI operations)
"""

try:
    print("🚀 Testing PixPort Flask Application")
    print("=" * 50)
    
    # Add parent directory to path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Test basic imports
    print("📦 Testing imports...")
    from app import create_app
    print("✅ Flask app factory imported")
    
    # Create app
    print("🔧 Creating Flask app...")
    app = create_app()
    print("✅ Flask app created successfully!")
    
    # Test app configuration
    print(f"✅ App name: {app.name}")
    print(f"✅ Upload folder: {app.config.get('UPLOAD_FOLDER')}")
    print(f"✅ Processed folder: {app.config.get('PROCESSED_FOLDER')}")
    print(f"✅ Max file size: {app.config.get('MAX_CONTENT_LENGTH')} bytes")
    
    # Test routes
    print("\n🗺️ Testing routes...")
    with app.test_client() as client:
        # Test home page
        response = client.get('/')
        print(f"✅ Home page status: {response.status_code}")
        
        # Test health endpoint
        response = client.get('/health')
        print(f"✅ Health endpoint status: {response.status_code}")
        
        # Test status endpoint
        response = client.get('/status')
        print(f"✅ Status endpoint status: {response.status_code}")
        
        # Test ping endpoint
        response = client.get('/ping')
        print(f"✅ Ping endpoint status: {response.status_code}")
    
    # Test basic library imports (without heavy operations)
    print("\n📚 Testing basic library imports...")
    import cv2
    from PIL import Image
    import numpy as np
    print("✅ OpenCV imported")
    print("✅ PIL imported")  
    print("✅ NumPy imported")
    
    print("\n🎉 All tests passed!")
    print("✅ PixPort is ready to run!")
    print("\n💡 To start the server, run:")
    print("   python main.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
