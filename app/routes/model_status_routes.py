"""
Model Status and Monitoring Routes
Shows which background removal models are currently loaded and active
"""

from flask import Blueprint, jsonify, request
import os
import psutil
import logging

logger = logging.getLogger(__name__)
model_status_bp = Blueprint('model_status', __name__)

@model_status_bp.route('/api/model/status', methods=['GET'])
def get_model_status():
    """Get current model status and memory usage"""
    try:
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None
        
        status = {
            'environment': 'Railway' if is_railway else 'Local',
            'deployment_optimized': True,
            'models': {}
        }
        
        # Check Railway BG Remover
        try:
            from app.services.railway_bg_remover import railway_bg_remover
            railway_memory = railway_bg_remover.get_memory_usage()
            status['models']['railway_bg_remover'] = {
                'loaded': True,
                'model_name': railway_memory.get('model_name', 'isnet-general-use'),
                'memory_mb': round(railway_memory.get('rss_mb', 0), 1),
                'model_loaded': railway_memory.get('model_loaded', False),
                'priority': 1 if is_railway else 3,
                'description': 'isnet-general-use (tiny ~1.6MB model)'
            }
        except Exception as e:
            status['models']['railway_bg_remover'] = {
                'loaded': False,
                'error': str(e)
            }
        
        # Check Minimal BG Remover
        try:
            from app.services.minimal_bg_remover import minimal_bg_remover
            minimal_memory = minimal_bg_remover.get_memory_usage()
            status['models']['minimal_bg_remover'] = {
                'loaded': True,
                'model_name': minimal_memory.get('model_name', 'opencv_cv'),
                'memory_mb': round(minimal_memory.get('rss_mb', 0), 1),
                'model_loaded': minimal_memory.get('model_loaded', False),
                'priority': 2 if is_railway else 2,
                'description': 'OpenCV computer vision (<100MB RAM)'
            }
        except Exception as e:
            status['models']['minimal_bg_remover'] = {
                'loaded': False,
                'error': str(e)
            }
        
        # Check Tiny U2Net (for local)
        if not is_railway:
            try:
                from app.services.tiny_u2net_service import tiny_u2net_service
                tiny_memory = tiny_u2net_service.get_memory_usage()
                status['models']['tiny_u2net'] = {
                    'loaded': True,
                    'model_name': 'u2netp',
                    'memory_mb': round(tiny_memory.get('rss_mb', 0), 1),
                    'model_loaded': tiny_memory.get('model_loaded', False),
                    'priority': 1,
                    'description': 'Tiny U²-Net (u2netp model)'
                }
            except Exception as e:
                status['models']['tiny_u2net'] = {
                    'loaded': False,
                    'error': str(e)
                }
        
        # Check Model Manager (legacy AI models)
        if not is_railway:
            try:
                from app.services.model_manager import model_manager
                manager_memory = model_manager.get_memory_info()
                status['models']['model_manager'] = {
                    'loaded': True,
                    'model_name': manager_memory.get('current_model', 'None'),
                    'memory_mb': round(manager_memory.get('rss', 0), 1),
                    'model_loaded': manager_memory.get('current_model') is not None,
                    'priority': 4,
                    'description': 'Legacy AI models (u2net, u2netp, silueta)'
                }
            except Exception as e:
                status['models']['model_manager'] = {
                    'loaded': False,
                    'error': str(e)
                }
        
        # Add system memory info
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            virtual_memory = psutil.virtual_memory()
            
            status['system_memory'] = {
                'process_memory_mb': round(memory_info.rss / 1024 / 1024, 1),
                'process_memory_percent': round(process.memory_percent(), 2),
                'available_memory_mb': round(virtual_memory.available / 1024 / 1024, 1),
                'total_memory_mb': round(virtual_memory.total / 1024 / 1024, 1),
                'memory_percent_used': round(virtual_memory.percent, 1)
            }
            
            # Railway compatibility check
            if is_railway:
                railway_limit_mb = 512
                current_usage = memory_info.rss / 1024 / 1024
                status['railway_compatibility'] = {
                    'memory_limit_mb': railway_limit_mb,
                    'current_usage_mb': round(current_usage, 1),
                    'usage_percent': round((current_usage / railway_limit_mb) * 100, 1),
                    'compatible': current_usage < (railway_limit_mb * 0.8),  # 80% threshold
                    'status': 'SAFE' if current_usage < (railway_limit_mb * 0.8) else 'WARNING'
                }
        
        except Exception as e:
            status['system_memory'] = {'error': str(e)}
        
        # Add processing strategy
        if is_railway:
            status['processing_strategy'] = [
                '1. Railway BG Remover (isnet-general-use)',
                '2. Minimal BG Remover (OpenCV)',
                '3. Simple Fallback'
            ]
        else:
            status['processing_strategy'] = [
                '1. Tiny U²-Net (u2netp)',
                '2. Minimal BG Remover (OpenCV)', 
                '3. Legacy AI Models',
                '4. Simple Fallback'
            ]
        
        return jsonify(status), 200
        
    except Exception as e:
        logger.error(f"Error getting model status: {e}")
        return jsonify({
            'error': 'Failed to get model status',
            'message': str(e)
        }), 500

@model_status_bp.route('/api/model/clear-memory', methods=['POST'])
def clear_model_memory():
    """Clear all model memory to free RAM"""
    try:
        cleared_models = []
        
        # Clear Railway BG Remover
        try:
            from app.services.railway_bg_remover import railway_bg_remover
            railway_bg_remover.clear_memory()
            cleared_models.append('railway_bg_remover')
        except Exception as e:
            logger.warning(f"Failed to clear railway_bg_remover: {e}")
        
        # Clear Tiny U2Net
        try:
            from app.services.tiny_u2net_service import tiny_u2net_service
            tiny_u2net_service.clear_memory()
            cleared_models.append('tiny_u2net_service')
        except Exception as e:
            logger.warning(f"Failed to clear tiny_u2net_service: {e}")
        
        # Clear Model Manager
        try:
            from app.services.model_manager import model_manager
            model_manager.clear_all()
            cleared_models.append('model_manager')
        except Exception as e:
            logger.warning(f"Failed to clear model_manager: {e}")
        
        # Force garbage collection
        import gc
        gc.collect()
        
        return jsonify({
            'success': True,
            'message': 'Model memory cleared',
            'cleared_models': cleared_models
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing model memory: {e}")
        return jsonify({
            'error': 'Failed to clear model memory',
            'message': str(e)
        }), 500

@model_status_bp.route('/api/model/test-processing', methods=['POST'])
def test_model_processing():
    """Test which model would be used for processing"""
    try:
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None
        
        # Simulate the model selection logic from bg_remover_lite
        file_size = request.json.get('file_size', 1024000) if request.json else 1024000  # 1MB default
        
        selected_models = []
        
        if is_railway or file_size > 5 * 1024 * 1024:
            selected_models.append({
                'priority': 1,
                'model': 'Railway BG Remover',
                'service': 'railway_bg_remover',
                'model_name': 'isnet-general-use',
                'reason': 'Railway deployment or large file (>5MB)'
            })
        
        if not is_railway:
            selected_models.append({
                'priority': 2,
                'model': 'Tiny U²-Net',
                'service': 'tiny_u2net_service', 
                'model_name': 'u2netp',
                'reason': 'Local deployment'
            })
        
        selected_models.append({
            'priority': 3,
            'model': 'Minimal CV',
            'service': 'minimal_bg_remover',
            'model_name': 'opencv_cv',
            'reason': 'Guaranteed fallback'
        })
        
        if not is_railway:
            selected_models.append({
                'priority': 4,
                'model': 'Legacy AI',
                'service': 'model_manager',
                'model_name': 'u2netp',
                'reason': 'Final AI fallback for local'
            })
        
        selected_models.append({
            'priority': 5,
            'model': 'Simple Fallback',
            'service': 'bg_remover_lite',
            'model_name': 'edge_detection',
            'reason': 'Ultimate fallback'
        })
        
        return jsonify({
            'environment': 'Railway' if is_railway else 'Local',
            'file_size_bytes': file_size,
            'file_size_mb': round(file_size / 1024 / 1024, 2),
            'processing_order': selected_models,
            'primary_model': selected_models[0] if selected_models else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error testing model processing: {e}")
        return jsonify({
            'error': 'Failed to test model processing',
            'message': str(e)
        }), 500
