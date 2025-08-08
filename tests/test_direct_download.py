#!/usr/bin/env python3

from app import create_app
from app.routes.main_routes import download_image
from flask import Flask

# Create app context
app = create_app()

with app.app_context():
    with app.test_request_context('/api/download/0950ef76-281d-42ea-981f-a71e0ea6e6b5_time_enhanced.png'):
        try:
            # Call the function directly
            result = download_image('0950ef76-281d-42ea-981f-a71e0ea6e6b5_time_enhanced.png')
            print(f"Result type: {type(result)}")
            print(f"Result: {result}")
            if hasattr(result, 'data'):
                print(f"Response data: {result.data}")
            if hasattr(result, 'status_code'):
                print(f"Status code: {result.status_code}")
            if hasattr(result, 'headers'):
                print(f"Headers: {dict(result.headers)}")
        except Exception as e:
            import traceback
            print(f"Exception: {e}")
            print(f"Traceback: {traceback.format_exc()}")
