#!/usr/bin/env python3
"""
Test basic startup without AI models
"""

try:
    print("🧪 Testing PixPort startup...")
    
    # Test basic imports
    from app import create_app
    print("✅ Flask app import successful")
    
    # Create app
    app = create_app()
    print("✅ Flask app created")
    
    # Test basic routes
    with app.test_client() as client:
        response = client.get('/health')
        print(f"✅ Health check: {response.status_code}")
        
        response = client.get('/ping')
        print(f"✅ Ping: {response.status_code}")
    
    print("🎉 Basic startup test passed!")
    
except Exception as e:
    print(f"❌ Startup test failed: {e}")
    import traceback
    traceback.print_exc()
