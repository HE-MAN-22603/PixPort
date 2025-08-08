import requests

try:
    # Test the image-info API instead
    response = requests.get('http://127.0.0.1:5000/api/image-info/0950ef76-281d-42ea-981f-a71e0ea6e6b5_time_enhanced.png')
    print(f'Image Info API Status: {response.status_code}')
    print(f'Response text: {response.text[:500]}')
    
    # Test the ping endpoint
    response2 = requests.get('http://127.0.0.1:5000/ping')
    print(f'Ping API Status: {response2.status_code}')
    print(f'Ping response: {response2.text}')
    
except Exception as e:
    print(f'Error: {e}')
