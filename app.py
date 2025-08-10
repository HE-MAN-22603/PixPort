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
    """Ensure AI models are available and show which one is active"""
    try:
        print('🔍 Checking AI models...')
        
        # Import configuration to get active model
        from app.config import Config
        config = Config()
        active_model = config.REMBG_MODEL
        
        print(f'📦 Configured model: {active_model}')
        
        # Check if we're on Railway for model selection
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None
        
        if is_railway:
            print('🚄 Railway deployment detected - using memory-optimized models')
            
            # For Railway, try ISNet first (most memory efficient)
            try:
                from rembg import new_session
                print('   Testing isnet-general-use (Railway-optimized, ~1.6MB)...')
                session = new_session('isnet-general-use')
                print('✅ Primary model: isnet-general-use (Railway-optimized)')
                print('   📊 Memory usage: ~150MB peak')
                print('   🎯 Features: Background removal + color change')
                if 'logger' in locals():
                    logger.info('Railway: isnet-general-use model ready')
                return True
            except Exception as isnet_error:
                print(f'⚠️ isnet-general-use failed: {isnet_error}')
                
                # Fallback to Tiny U²-Net
                try:
                    print('   Trying u2netp (Tiny U²-Net, ~176KB)...')
                    session = new_session('u2netp')
                    print('✅ Fallback model: u2netp (Tiny U²-Net)')
                    print('   📊 Memory usage: ~120MB peak')
                    if 'logger' in locals():
                        logger.info('Railway: u2netp model ready (fallback)')
                    return True
                except Exception as u2netp_error:
                    print(f'⚠️ u2netp failed: {u2netp_error}')
        else:
            print('💻 Local deployment detected')
            
            # For local, try the configured model first
            try:
                from rembg import new_session
                print(f'   Testing {active_model}...')
                session = new_session(active_model)
                
                # Show model info
                model_info = {
                    'u2net': ('U²-Net', '~176MB', '~300MB peak'),
                    'u2netp': ('Tiny U²-Net', '~176KB', '~120MB peak'),
                    'isnet-general-use': ('ISNet General', '~1.6MB', '~150MB peak'),
                    'u2net_human_seg': ('U²-Net Human', '~176MB', '~350MB peak')
                }
                
                name, size, memory = model_info.get(active_model, (active_model, 'Unknown', 'Unknown'))
                print(f'✅ Primary model: {name} ({active_model})')
                print(f'   💾 Model size: {size}')
                print(f'   📊 Memory usage: {memory}')
                
                if 'logger' in locals():
                    logger.info(f'Local: {active_model} model ready')
                return True
                
            except Exception as model_error:
                print(f'⚠️ {active_model} failed: {model_error}')
        
        # Show available fallback methods
        print('🔄 Available fallback methods:')
        print('   • Minimal CV (OpenCV-based, <100MB memory)')
        print('   • Smart background detection')
        print('   • External API (if configured)')
        print('🚀 Models will be downloaded when first needed')
        
        if 'logger' in locals():
            logger.info('Model check completed - fallbacks available')
        return True
        
    except Exception as e:
        print(f'⚠️ Model system error: {e}')
        print('🔄 Fallback methods will be used')
        return False

# Skip model loading on Railway to prevent startup memory issues
if not os.environ.get('RAILWAY_ENVIRONMENT_NAME') and not os.environ.get('SKIP_AI_MODELS'):
    ensure_models()
else:
    if 'logger' in locals():
        logger.info('Skipping AI model preload - models will load on first request')
    else:
        print('⏩ Skipping AI model preload - models will load on first request')

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
