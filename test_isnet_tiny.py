"""
Test script for ISNet Tiny Background Removal Service
"""

import sys
import os
import requests
import time
from pathlib import Path

# Add app to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_service_locally():
    """Test the service running locally"""
    
    # Test if service is available
    try:
        response = requests.get('http://localhost:5000/api/bg/status', timeout=10)
        print(f"✅ Service status: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Service not available: {e}")
        return False
    
    # Test health endpoint
    try:
        response = requests.get('http://localhost:5000/api/bg/health', timeout=10)
        print(f"✅ Health check: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    return True

def test_background_removal(image_path, output_dir="test_outputs"):
    """Test background removal with a real image"""
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Test background removal
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(
                'http://localhost:5000/api/bg/remove',
                files=files,
                timeout=60
            )
        
        if response.status_code == 200:
            output_path = os.path.join(output_dir, 'removed_bg.png')
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Background removal successful: {output_path}")
            print(f"Output size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Background removal failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Background removal request failed: {e}")
        return False

def test_color_change(image_path, color="#FF0000", output_dir="test_outputs"):
    """Test background color change with a real image"""
    
    if not os.path.exists(image_path):
        print(f"❌ Test image not found: {image_path}")
        return False
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Test color change
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            data = {'color': color}
            response = requests.post(
                'http://localhost:5000/api/bg/change_color',
                files=files,
                data=data,
                timeout=60
            )
        
        if response.status_code == 200:
            output_path = os.path.join(output_dir, f'color_{color.replace("#", "")}.jpg')
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"✅ Color change successful: {output_path}")
            print(f"Output size: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ Color change failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Color change request failed: {e}")
        return False

def test_direct_service():
    """Test the service directly without HTTP"""
    print("\n🔧 Testing service directly...")
    
    try:
        from app.services.isnet_tiny_service import isnet_tiny_service
        
        # Test memory usage
        memory_info = isnet_tiny_service.get_memory_usage()
        print(f"Memory info: {memory_info}")
        
        # Test model loading (this will trigger download if needed)
        print("Testing model access...")
        session = isnet_tiny_service._get_session()
        if session:
            print("✅ Model loaded successfully")
        else:
            print("❌ Failed to load model")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Direct service test failed: {e}")
        return False

def main():
    print("🧪 Testing ISNet Tiny Background Removal Service\n")
    
    # Test 1: Direct service test
    if not test_direct_service():
        print("❌ Direct service test failed, skipping HTTP tests")
        return
    
    print("\n🌐 Testing HTTP service...")
    print("Make sure to start the service with: python app_isnet_tiny.py")
    print("Waiting 3 seconds for service to be ready...")
    time.sleep(3)
    
    # Test 2: Service availability
    if not test_service_locally():
        print("❌ Service not available, skipping image tests")
        return
    
    # Test 3: Find a test image
    test_image = None
    potential_test_images = [
        "test_image.jpg",
        "test.jpg",
        "sample.png",
        "app/static/uploads/test.jpg",
        # Add paths where you might have test images
    ]
    
    for img_path in potential_test_images:
        if os.path.exists(img_path):
            test_image = img_path
            break
    
    if not test_image:
        print("\n⚠️  No test image found. Please provide a test image as 'test_image.jpg'")
        print("Skipping image processing tests...")
        return
    
    print(f"\n📸 Using test image: {test_image}")
    
    # Test 4: Background removal
    print("\n🔄 Testing background removal...")
    test_background_removal(test_image)
    
    # Test 5: Color change
    print("\n🎨 Testing background color change...")
    test_color_change(test_image, "#00FF00")  # Green background
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
