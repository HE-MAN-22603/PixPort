import requests

try:
    # Test the download API with a real file - allow redirects
    response = requests.get('http://127.0.0.1:5000/api/download/0950ef76-281d-42ea-981f-a71e0ea6e6b5_time_enhanced.png', allow_redirects=True)
    print(f'Download API Status: {response.status_code}')
    print(f'Location header: {response.headers.get("Location", "None")}')
    print(f'Response text: {response.text[:200]}')
    
    # Follow the redirect manually if it's a redirect
    if response.status_code in [301, 302]:
        redirect_url = response.headers.get('Location')
        if redirect_url:
            print(f'Following redirect to: {redirect_url}')
            follow_response = requests.get(redirect_url)
            print(f'Final Status: {follow_response.status_code}')
            print(f'Content-Type: {follow_response.headers.get("Content-Type", "None")}')
            print(f'Content-Length: {follow_response.headers.get("Content-Length", "None")}')
            if follow_response.headers.get('Content-Disposition'):
                print(f'Content-Disposition: {follow_response.headers.get("Content-Disposition")}')
except Exception as e:
    print(f'Error: {e}')
