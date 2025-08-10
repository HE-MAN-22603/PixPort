"""
Health and monitoring routes
"""

from flask import Blueprint, jsonify
import psutil
import os
from ..services.model_manager import model_manager
from ..services.model_warmer import get_warming_status

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Enhanced health check with model warming status"""
    try:
        warming_status = get_warming_status()
        models_ready = any(status == 'ready' for status in warming_status.values())
        
        return jsonify({
            'status': 'healthy',
            'models_ready': models_ready,
            'model_warming': warming_status,
            'environment': os.environ.get('RAILWAY_ENVIRONMENT_NAME', 'development'),
            'cold_start_optimized': True
        })
    except Exception as e:
        return jsonify({
            'status': 'healthy',
            'models_ready': False,
            'error': str(e),
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
