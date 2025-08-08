#!/usr/bin/env python3
"""
Test script to verify download format functionality
"""

import requests
import os

def test_download_formats():
    """Test different download formats"""
    
    # Base URL - adjust this to match your server
    base_url = "http://localhost:5000"
    
    # Test filename - you'll need to have an actual processed image file
    test_filename = "your_test_image.jpg"  # Replace with actual filename
    
    # Test formats
    formats = [
        ('PNG', 'image/png'),
        ('JPEG', 'image/jpeg'), 
        ('PDF', 'application/pdf'),
        ('WEBP', 'image/webp')
    ]
    
    print("Testing download format functionality...")
    print("=" * 50)
    
    for format_name, expected_mime in formats:
        print(f"\nTesting {format_name} format...")
        
        # Build download URL with format parameter
        url = f"{base_url}/api/download/{test_filename}?format={format_name}&quality=95"
        
        try:
            response = requests.get(url, stream=True)
            
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                content_disposition = response.headers.get('Content-Disposition', '')
                
                print(f"  ✅ Status: {response.status_code}")
                print(f"  ✅ Content-Type: {content_type}")
                print(f"  ✅ Content-Disposition: {content_disposition}")
                
                # Check if the content type matches expected
                if expected_mime in content_type:
                    print(f"  ✅ MIME type correct: {content_type}")
                else:
                    print(f"  ❌ MIME type mismatch. Expected: {expected_mime}, Got: {content_type}")
                
                # Check content length
                content_length = len(response.content)
                print(f"  ✅ Content size: {content_length} bytes")
                
                # Save a sample file to verify it's valid
                sample_filename = f"sample_{format_name.lower()}.{format_name.lower() if format_name != 'JPEG' else 'jpg'}"
                with open(sample_filename, 'wb') as f:
                    f.write(response.content)
                print(f"  ✅ Sample saved as: {sample_filename}")
                
            else:
                print(f"  ❌ Request failed with status: {response.status_code}")
                if response.headers.get('Content-Type') == 'application/json':
                    error_data = response.json()
                    print(f"  ❌ Error: {error_data}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Request error: {e}")
        except Exception as e:
            print(f"  ❌ Unexpected error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_download_formats()
