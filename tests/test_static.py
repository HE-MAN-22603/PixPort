import requests

try:
    # Test the static file URL directly
    response = requests.get('http://127.0.0.1:5000/static/processed/0950ef76-281d-42ea-981f-a71e0ea6e6b5_time_enhanced.png?download=true')
    print(f'Static file Status: {response.status_code}')
    print(f'Content-Type: {response.headers.get("Content-Type", "None")}')
    print(f'Content-Length: {response.headers.get("Content-Length", "None")}')
    print(f'Content-Disposition: {response.headers.get("Content-Disposition", "None")}')
    if response.status_code >= 400:
        print(f'Response text: {response.text[:500]}')
except Exception as e:
    print(f'Error: {e}')
