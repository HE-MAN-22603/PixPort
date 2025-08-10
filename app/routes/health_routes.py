"""
Health and monitoring routes
"""

from flask import Blueprint, jsonify
import psutil
import os
from ..services.model_manager import model_manager

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'environment': os.environ.get('RAILWAY_ENVIRONMENT_NAME', 'development')
    })

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
