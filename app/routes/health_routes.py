"""
Health and monitoring routes optimized for Google Cloud Run
"""

from flask import Blueprint, jsonify
import psutil
import os
import time
from ..services.model_manager import model_manager

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Cloud Run health check endpoint - must respond quickly"""
    try:
        # Quick health check for Cloud Run
        environment = 'cloud-run' if os.environ.get('K_SERVICE') else \
                     'railway' if os.environ.get('RAILWAY_ENVIRONMENT_NAME') else \
                     'development'
        
        return jsonify({
            'status': 'healthy',
            'environment': environment,
            'timestamp': time.time()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@health_bp.route('/warmup', methods=['GET', 'POST'])
def warmup():
    """
    Warmup endpoint for Cloud Run - runs dummy AI inference
    This endpoint makes the first real user request much faster
    """
    try:
        from model_utils import model_manager as optimized_manager
        
        # Check if model is ready
        if not optimized_manager.is_ready():
            return jsonify({
                'status': 'warming',
                'message': 'Model not ready yet'
            }), 202
        
        # Check if already warmed up
        if optimized_manager.is_warmed_up():
            return jsonify({
                'status': 'ready',
                'message': 'Model already warmed up',
                'model_ready': True,
                'warmup_complete': True
            })
        
        # Model is ready but not warmed up yet - warmup happens in background
        # Just return success since warmup runs async
        return jsonify({
            'status': 'warming',
            'message': 'Warmup in progress',
            'model_ready': True,
            'warmup_complete': False
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@health_bp.route('/ready')
def readiness_check():
    """Cloud Run readiness probe - checks if AI model is loaded"""
    try:
        from model_utils import model_manager as optimized_manager
        
        model_ready = optimized_manager.is_ready()
        warmup_complete = optimized_manager.is_warmed_up()
        
        if model_ready:
            return jsonify({
                'status': 'ready',
                'model_ready': model_ready,
                'warmup_complete': warmup_complete,
                'performance_tip': 'First request will be fast!' if warmup_complete else 'First request may be slower'
            })
        else:
            return jsonify({
                'status': 'not_ready',
                'model_ready': False,
                'message': 'AI model not loaded'
            }), 503
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@health_bp.route('/memory')  
def memory_status():
    """Memory usage endpoint"""
    try:
        # System memory
        memory = psutil.virtual_memory()
        
        # Process memory
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # Model manager info
        model_info = model_manager.get_memory_info()
        
        # Check if lightweight processor is available
        lightweight_status = 'available'
        try:
            from ..services.lightweight_bg_removal import lightweight_remover
            lightweight_ready = lightweight_remover.initialized
        except Exception:
            lightweight_status = 'unavailable'
            lightweight_ready = False
        
        return jsonify({
            'system_memory': {
                'total_mb': round(memory.total / 1024 / 1024, 2),
                'available_mb': round(memory.available / 1024 / 1024, 2),
                'used_percent': memory.percent
            },
            'process_memory': {
                'rss_mb': round(process_memory.rss / 1024 / 1024, 2),
                'vms_mb': round(process_memory.vms / 1024 / 1024, 2),
                'percent': round(process.memory_percent(), 2)
            },
            'ai_models': model_info,
            'lightweight_processor': {
                'status': lightweight_status,
                'ready': lightweight_ready,
                'memory_footprint': '~20MB'
            },
            'processing_strategy': 'lightweight_first',
            'worker_pid': os.getpid()
        })
    except Exception as e:
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500
