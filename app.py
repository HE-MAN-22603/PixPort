#!/usr/bin/env python3
"""
PixPort - AI Passport Photo Maker
Main Flask application entry point
"""

from app import create_app
import os
import logging

# Configure logging for production
if os.environ.get('RAILWAY_ENVIRONMENT_NAME'):
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    logger.info('Starting PixPort in production mode')

app = create_app()

# Download AI models on startup if not exists
def ensure_models():
    """Ensure AI models are available"""
    try:
        from rembg import new_session
        # Test if models are available
        session = new_session('u2net')
        logger.info('AI models are ready') if 'logger' in locals() else None
    except Exception as e:
        print(f'Downloading AI models: {e}')
        try:
            import subprocess
            subprocess.run(['python', 'download_models.py'], check=True)
        except Exception as download_error:
            print(f'Model download error: {download_error}')

# Ensure models are available on startup
ensure_models()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
