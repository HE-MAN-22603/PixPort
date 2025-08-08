#!/usr/bin/env python3
"""
Test script to verify the image info API is working correctly
"""

import os
import sys
import requests
import time
from PIL import Image
import threading
from app import create_app

# Create app instance
app = create_app()

def start_server():
    """Start the Flask server in a separate thread"""
    print("Starting Flask server...")
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True, use_reloader=False)

def test_api():
    """Test the image info API"""
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    # Create a test image
    test_image_path = os.path.join(app.config['UPLOAD_FOLDER'], 'test_image.jpg')
    
    if not os.path.exists(test_image_path):
        # Create a simple test image
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (413, 531), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([50, 50, 363, 481], outline='blue', width=3)
        draw.text((150, 250), "TEST IMAGE", fill='black')
        img.save(test_image_path, 'JPEG')
        print(f"Created test image: {test_image_path}")
    
    # Test the API
    try:
        response = requests.get('http://127.0.0.1:5001/api/image-info/test_image.jpg', timeout=10)
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Content: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ API is working correctly!")
                print(f"Image dimensions: {data.get('width')}x{data.get('height')}")
                print(f"Image format: {data.get('format')}")
                return True
            else:
                print("❌ API returned success=False")
                return False
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("Testing PixPort Image Info API Fix")
    print("=" * 40)
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test the API
    success = test_api()
    
    if success:
        print("\n✅ The fix is working! Image information should now display correctly.")
    else:
        print("\n❌ The fix needs more work. Check the API implementation.")
        
    print("\nTest complete. Check your browser at: http://127.0.0.1:5001")
    print("Upload an image and check if the image information displays correctly.")
    
    # Keep server running for manual testing
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == "__main__":
    main()
