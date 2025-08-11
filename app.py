#!/usr/bin/env python3
"""
PixPort - AI Passport Photo Maker
Optimized for Google Cloud Run with preloaded AI models
"""

from app import create_app
import os
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Detect deployment environment
is_cloud_run = os.environ.get('K_SERVICE') is not None
is_railway = os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None

if is_cloud_run:
    logger.info('🚀 Starting PixPort on Google Cloud Run')
elif is_railway:
    logger.info('🚄 Starting PixPort on Railway')
else:
    logger.info('💻 Starting PixPort in local development mode')

app = create_app()

# ==========================================
# 🚀 OPTIMIZED MODEL PRELOADING FOR CLOUD RUN
# ==========================================

def preload_ai_models():
    """
    Preload AI models during container startup for faster first requests.
    This eliminates the 10-15 second delay on first background removal.
    """
    start_time = time.time()
    
    try:
        logger.info("📦 Preloading AI models for optimal Cloud Run performance...")
        
        # Import our optimized model manager
        from model_utils import load_model
        
        # Preload the model during startup
        success = load_model()
        
        if success:
            preload_time = time.time() - start_time
            logger.info(f"✅ AI model preloaded in {preload_time:.2f}s - first requests will be fast!")
            return True
        else:
            logger.warning("⚠️ Model preload failed - models will load on first request")
            return False
            
    except Exception as e:
        load_time = time.time() - start_time
        logger.error(f"❌ Model preload failed after {load_time:.2f}s: {e}")
        logger.info("🔄 Falling back to on-demand model loading")
        return False

# Preload models based on environment
if is_cloud_run or (not is_railway and not os.environ.get('SKIP_AI_MODELS')):
    # Preload on Cloud Run and local development
    logger.info("🎯 Environment supports model preloading")
    preload_ai_models()
else:
    # Skip preload on Railway (memory constraints) or when explicitly disabled
    logger.info("⏩ Skipping model preload - using on-demand loading")

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
