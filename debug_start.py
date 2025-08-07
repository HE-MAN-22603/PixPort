#!/usr/bin/env python3
"""
Debug startup script for Railway deployment
"""

import os
import sys
import time

print("🔍 PixPort Debug Startup")
print("=" * 50)

# Print environment info
print(f"Python version: {sys.version}")
print(f"Environment: {os.environ.get('RAILWAY_ENVIRONMENT_NAME', 'local')}")
print(f"Port: {os.environ.get('PORT', '5000')}")
print(f"Workers: 1")

# Test basic imports
print("\n📦 Testing imports...")
try:
    import flask
    print(f"✅ Flask {flask.__version__}")
except Exception as e:
    print(f"❌ Flask: {e}")

try:
    import gunicorn
    print(f"✅ Gunicorn available")
except Exception as e:
    print(f"❌ Gunicorn: {e}")

try:
    from app import create_app
    print("✅ App module imported")
    
    app = create_app()
    print("✅ Flask app created")
    
    # Test health endpoint
    with app.test_client() as client:
        response = client.get('/health')
        print(f"✅ Health check returns: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.get_json()}")
    
except Exception as e:
    print(f"❌ App creation failed: {e}")
    import traceback
    traceback.print_exc()

print("\n🚀 Starting gunicorn server...")
print("Binding to 0.0.0.0:{0}".format(os.environ.get('PORT', '5000')))

# Import and run the actual app
if __name__ == "__main__":
    from app import create_app
    app = create_app()
    
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting on port {port}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False,
        threaded=True
    )
