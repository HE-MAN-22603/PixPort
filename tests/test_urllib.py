import urllib.request
import urllib.error

try:
    # Test the download API
    url = 'http://127.0.0.1:5000/api/download/0950ef76-281d-42ea-981f-a71e0ea6e6b5_time_enhanced.png'
    
    # Use urllib to make request
    req = urllib.request.Request(url)
    
    try:
        response = urllib.request.urlopen(req)
        print(f'Status: {response.getcode()}')
        print(f'Headers: {dict(response.headers)}')
        print(f'URL after redirects: {response.geturl()}')
        
        # Read a small portion of the response
        data = response.read(100)
        print(f'Response data (first 100 bytes): {data}')
        
    except urllib.error.HTTPError as e:
        print(f'HTTP Error: {e.code}')
        print(f'Response: {e.read().decode()}')
        
except Exception as e:
    print(f'Error: {e}')
