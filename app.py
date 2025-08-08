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
        print('Checking AI models...')
        from rembg import new_session
        # Test if models are available
        session = new_session('u2net')
        print('✅ AI models are ready')
        if 'logger' in locals():
            logger.info('AI models are ready')
        return True
    except Exception as e:
        print(f'⚠️ AI models not ready: {e}')
        print('Models will be downloaded when first needed')
        return False

# Only try to ensure models if not in Railway startup
if not os.environ.get('RAILWAY_ENVIRONMENT_NAME'):
    ensure_models()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Print startup information
    print(f'\n🚀 Starting PixPort Server on port {port}')
    print(f'📊 Debug mode: {"ON" if debug else "OFF"}')
    print(f'🌍 Environment: {"Production" if os.environ.get("RAILWAY_ENVIRONMENT_NAME") else "Development"}')
    print(f'🔗 Local URL: http://127.0.0.1:{port}')
    print(f'🔗 Network URL: http://0.0.0.0:{port}')
    print('\n✅ Server ready to accept connections!')
    print('='*50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
