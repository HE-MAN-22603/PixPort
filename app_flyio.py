#!/usr/bin/env python3
"""
PixPort - Fly.io Deployment Version
Optimized for isnet-general-use model and FREE PLAN (256MB)
"""

# Set environment variables early for Fly.io
import os
os.environ.setdefault('REMBG_MODEL', 'isnet-general-use')
os.environ.setdefault('FLY_DEPLOYMENT', 'true')
os.environ.setdefault('MEMORY_CONSTRAINED', 'true')
os.environ.setdefault('FLASK_ENV', 'production')

from app import create_app
import logging
import time
import gc

# Configure logging for Fly.io
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def optimize_for_flyio():
    """Apply Fly.io specific optimizations"""
    
    # Force garbage collection
    gc.collect()
    
    # Set memory limits
    os.environ['MAX_CONTENT_LENGTH'] = '8388608'  # 8MB max upload
    
    # Optimize model loading for isnet-general-use
    logger.info("🚀 Fly.io deployment detected - optimizing for 256MB memory limit")
    
    try:
        # Pre-warm the isnet-general-use model
        logger.info("🔥 Pre-warming isnet-general-use model...")
        start_time = time.time()
        
        from rembg import new_session
        session = new_session('isnet-general-use')
        
        load_time = time.time() - start_time
        logger.info(f"✅ Model pre-warmed in {load_time:.2f}s")
        
        # Force cleanup after preload
        del session
        gc.collect()
        
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Model pre-warming failed: {e}")
        logger.info("🔄 Model will be loaded on first request")
        return False

def get_memory_usage():
    """Get current memory usage for monitoring"""
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        percent = process.memory_percent()
        
        return {
            'memory_mb': round(memory_mb, 2),
            'memory_percent': round(percent, 2),
            'limit_mb': 256,  # Free plan limit
            'usage_ratio': round(memory_mb / 256, 2)
        }
    except:
        return {'error': 'Unable to get memory info'}

# Detect Fly.io environment
is_flyio = os.environ.get('FLY_APP_NAME') is not None or os.environ.get('FLY_DEPLOYMENT')

if is_flyio:
    logger.info('🪂 Starting PixPort on Fly.io FREE PLAN')
    logger.info('🎯 Using isnet-general-use model for optimal memory usage')
    
    # Apply Fly.io optimizations
    optimize_for_flyio()
    
    # Log memory usage
    memory_info = get_memory_usage()
    logger.info(f"💾 Memory usage: {memory_info}")
    
else:
    logger.info('💻 Starting PixPort in local development mode')

# Create Flask app
app = create_app()

# Add Fly.io specific route for debugging
@app.route('/flyio-status')
def flyio_status():
    """Fly.io specific status endpoint"""
    memory_info = get_memory_usage()
    
    return {
        'platform': 'Fly.io',
        'model': 'isnet-general-use',
        'memory': memory_info,
        'environment': os.environ.get('FLY_DEPLOYMENT', 'unknown'),
        'region': os.environ.get('FLY_REGION', 'unknown'),
        'app_name': os.environ.get('FLY_APP_NAME', 'unknown'),
        'free_plan': True,
        'status': 'healthy'
    }

# Add memory monitoring endpoint
@app.route('/memory')
def memory_status():
    """Memory usage monitoring for free plan"""
    memory_info = get_memory_usage()
    
    status = 'healthy'
    if memory_info.get('usage_ratio', 0) > 0.9:  # > 90%
        status = 'warning'
    elif memory_info.get('usage_ratio', 0) > 0.95:  # > 95%
        status = 'critical'
    
    return {
        'status': status,
        'memory': memory_info,
        'recommendations': {
            'upgrade_plan': memory_info.get('usage_ratio', 0) > 0.8,
            'clear_cache': memory_info.get('usage_ratio', 0) > 0.9
        }
    }

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Fly.io production settings
    if is_flyio:
        logger.info(f'🪂 Fly.io app starting on port {port}')
        logger.info(f'🎯 Model: isnet-general-use')
        logger.info(f'💾 Memory limit: 256MB (FREE PLAN)')
        logger.info(f'🌍 Region: {os.environ.get("FLY_REGION", "unknown")}')
        
        # Use gunicorn in production (handled by Dockerfile CMD)
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Development mode
        app.run(host='0.0.0.0', port=port, debug=True)
