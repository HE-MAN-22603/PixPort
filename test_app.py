#!/usr/bin/env python3
"""
Simple test script to verify PixPort Flask app works
"""

try:
    from app import create_app
    
    print("✅ Creating Flask app...")
    app = create_app()
    
    print("✅ App created successfully!")
    print(f"✅ App name: {app.name}")
    print(f"✅ Upload folder configured: {app.config.get('UPLOAD_FOLDER')}")
    print(f"✅ Processed folder configured: {app.config.get('PROCESSED_FOLDER')}")
    print(f"✅ Max file size: {app.config.get('MAX_CONTENT_LENGTH')} bytes")
    
    # Test importing services
    print("\n🔧 Testing AI services import...")
    from app.services.bg_remover_lite import remove_background
    from app.services.bg_changer import change_background
    from app.services.enhancer import enhance_image
    from app.services.photo_resizer import resize_to_passport
    from app.services.utils import allowed_file
    
    print("✅ All services imported successfully!")
    
    # Test rembg import
    print("\n🤖 Testing AI libraries...")
    import rembg
    import cv2
    from PIL import Image
    import numpy as np
    
    print("✅ All AI libraries imported successfully!")
    print("✅ rembg version:", rembg.__version__ if hasattr(rembg, '__version__') else "installed")
    print("✅ OpenCV version:", cv2.__version__)
    print("✅ PIL version:", Image.__version__ if hasattr(Image, '__version__') else "installed")
    print("✅ NumPy version:", np.__version__)
    
    print("\n🎉 PixPort is ready to run!")
    print("You can start the server with: python app.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
