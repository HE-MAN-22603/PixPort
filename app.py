#!/usr/bin/env python3
"""
PixPort - AI Passport Photo Maker
Optimized for Railway deployment with u2netp model
"""

# Set numba environment variables early to prevent cache issues
import os
os.environ.setdefault('NUMBA_DISABLE_JIT', '1')
os.environ.setdefault('NUMBA_CACHE_DIR', '/tmp/.numba_cache')
os.environ.setdefault('NUMBA_DISABLE_PERFORMANCE_WARNINGS', '1')

from app import create_app
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
# 🚄 RAILWAY OPTIMIZED DEPLOYMENT
# ==========================================

# Use on-demand model loading for Railway's 512MB memory limit
if is_railway:
    logger.info("🚄 Railway deployment detected - using memory-optimized configuration")
    logger.info("📦 Models: u2netp (~4.7MB) + isnet-general-use for Railway optimization")
    logger.info("💾 Memory limit: 512MB (models load on-demand to save memory)")
else:
    logger.info("⏩ Using on-demand model loading with u2netp")
    
logger.info("🤖 Models will load automatically when first background removal is requested")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    # Print startup information
    print(f'\n🚀 Starting PixPort Server on port {port}')
    print(f'📊 Debug mode: {"ON" if debug else "OFF"}')
    print(f'🌍 Environment: {"Production" if os.environ.get("RAILWAY_ENVIRONMENT_NAME") else "Development"}')
    print(f'🔗 Local URL: http://127.0.0.1:{port}')
    print(f'🔗 Network URL: http://0.0.0.0:{port}')
    
    # Display AI model information
    try:
        from app.services.model_manager import model_manager
        print('\n🤖 AI Model Information:')
        print(f'   Model: u2netp (Railway optimized)')
        print(f'   Size: ~4.7MB (memory efficient)')
        print(f'   Status: Ready for background removal')
        
        # Try to get memory info if available
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            print(f'   Memory: {memory_mb:.1f} MB')
        except:
            print(f'   Memory: Monitoring not available')
            
    except Exception as e:
        print(f'\n⚠️ AI Model: Error loading model info - {e}')
    
    print('\n✅ Server ready to accept connections!')
    print('='*50)
    
    app.run(host='0.0.0.0', port=port, debug=debug)
