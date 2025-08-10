"""
Flask API for Ultra-Lightweight Background Removal
Uses ONLY isnet-general-tiny model - optimized for Railway 512MB deployment
"""

import os
import time
import uuid
import logging
from flask import Blueprint, request, send_file, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import tempfile
import shutil

from ..services.isnet_tiny_service import isnet_tiny_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask Blueprint
bg_api = Blueprint('bg_api', __name__, url_prefix='/api/bg')

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB for Railway safety
MAX_DIMENSION = 1024  # Maximum image dimension
TEMP_DIR = None

def init_temp_dir():
    """Initialize temporary directory for processing"""
    global TEMP_DIR
    try:
        TEMP_DIR = tempfile.mkdtemp(prefix='pixport_isnet_')
        logger.info(f"Created temp directory: {TEMP_DIR}")
    except Exception as e:
        logger.error(f"Failed to create temp directory: {e}")
        TEMP_DIR = tempfile.gettempdir()

def cleanup_temp_dir():
    """Clean up temporary directory"""
    global TEMP_DIR
    if TEMP_DIR and os.path.exists(TEMP_DIR):
        try:
            shutil.rmtree(TEMP_DIR)
            logger.info(f"Cleaned up temp directory: {TEMP_DIR}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_request():
    """Validate incoming request for file upload"""
    # Check if file is present
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400
    
    file = request.files['file']
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    # Check file extension
    if not allowed_file(file.filename):
        return {'error': f'Invalid file type. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}, 400
    
    # Check file size (done by Flask config as well)
    if hasattr(file, 'content_length') and file.content_length > MAX_FILE_SIZE:
        return {'error': f'File too large. Maximum {MAX_FILE_SIZE//1024//1024}MB allowed'}, 413
    
    return None, None

def save_upload_file(file):
    """Save uploaded file to temporary location"""
    try:
        # Generate unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        temp_filename = f"{uuid.uuid4().hex[:8]}.{file_ext}"
        temp_path = os.path.join(TEMP_DIR, temp_filename)
        
        # Save file
        file.save(temp_path)
        
        # Additional size check after saving
        file_size = os.path.getsize(temp_path)
        if file_size > MAX_FILE_SIZE:
            os.remove(temp_path)
            return None, f"File too large: {file_size} bytes"
        
        logger.info(f"Saved upload: {temp_path} ({file_size} bytes)")
        return temp_path, None
        
    except Exception as e:
        logger.error(f"Error saving upload file: {e}")
        return None, f"Failed to save file: {e}"

def cleanup_file(filepath):
    """Clean up temporary file"""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        logger.warning(f"Failed to cleanup file {filepath}: {e}")

@bg_api.route('/remove', methods=['POST'])
def remove_background():
    """
    Remove background from uploaded image using isnet-general-tiny
    
    Form data:
    - file: Image file to process
    
    Returns:
    - PNG image with transparent background
    """
    start_time = time.time()
    input_path = None
    output_path = None
    
    try:
        # Validate request
        error, status_code = validate_request()
        if error:
            return jsonify(error), status_code
        
        file = request.files['file']
        
        # Save uploaded file
        input_path, error = save_upload_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Generate output path
        output_filename = f"{uuid.uuid4().hex[:8]}_nobg.png"
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        # Check memory before processing
        memory_info = isnet_tiny_service.get_memory_usage()
        logger.info(f"Memory before processing: {memory_info}")
        
        # Process with isnet-general-tiny
        success = isnet_tiny_service.remove_background(input_path, output_path)
        
        if not success:
            return jsonify({'error': 'Background removal failed'}), 500
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Output file not created'}), 500
        
        # Log processing time
        processing_time = time.time() - start_time
        output_size = os.path.getsize(output_path)
        logger.info(f"✅ Background removed in {processing_time:.2f}s, output: {output_size} bytes")
        
        # Return processed file
        return send_file(
            output_path,
            mimetype='image/png',
            as_attachment=True,
            download_name=f"nobg_{file.filename.rsplit('.', 1)[0]}.png"
        )
        
    except RequestEntityTooLarge:
        return jsonify({'error': f'File too large. Maximum {MAX_FILE_SIZE//1024//1024}MB allowed'}), 413
        
    except Exception as e:
        logger.error(f"Error in remove_background: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
        
    finally:
        # Always cleanup temp files
        cleanup_file(input_path)
        # Note: output_path will be cleaned up by Flask after send_file

@bg_api.route('/change_color', methods=['POST'])
def change_background_color():
    """
    Remove background and replace with solid color
    
    Form data:
    - file: Image file to process
    - color: Background color (hex format like '#FF0000' or RGB like '255,0,0')
    
    Returns:
    - Image with new background color (PNG or JPEG)
    """
    start_time = time.time()
    input_path = None
    output_path = None
    
    try:
        # Validate request
        error, status_code = validate_request()
        if error:
            return jsonify(error), status_code
        
        file = request.files['file']
        
        # Get background color
        bg_color = request.form.get('color', '#FFFFFF')
        
        # Parse color
        try:
            if bg_color.startswith('#'):
                # Hex color
                parsed_color = bg_color
            elif ',' in bg_color:
                # RGB format like "255,0,0"
                rgb = [int(c.strip()) for c in bg_color.split(',')]
                if len(rgb) != 3 or any(c < 0 or c > 255 for c in rgb):
                    raise ValueError("Invalid RGB values")
                parsed_color = tuple(rgb)
            else:
                # Default to white if can't parse
                logger.warning(f"Invalid color format '{bg_color}', using white")
                parsed_color = '#FFFFFF'
        except Exception as e:
            return jsonify({'error': f'Invalid color format: {bg_color}. Use hex (#FF0000) or RGB (255,0,0)'}), 400
        
        # Save uploaded file
        input_path, error = save_upload_file(file)
        if error:
            return jsonify({'error': error}), 400
        
        # Generate output path
        output_ext = 'png' if isinstance(parsed_color, str) else 'jpg'
        output_filename = f"{uuid.uuid4().hex[:8]}_colored.{output_ext}"
        output_path = os.path.join(TEMP_DIR, output_filename)
        
        # Check memory before processing
        memory_info = isnet_tiny_service.get_memory_usage()
        logger.info(f"Memory before processing: {memory_info}")
        
        # Process with background color change
        success = isnet_tiny_service.change_background_color(
            input_path, output_path, parsed_color
        )
        
        if not success:
            return jsonify({'error': 'Background color change failed'}), 500
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Output file not created'}), 500
        
        # Log processing time
        processing_time = time.time() - start_time
        output_size = os.path.getsize(output_path)
        logger.info(f"✅ Background color changed in {processing_time:.2f}s, output: {output_size} bytes")
        
        # Return processed file
        mimetype = 'image/png' if output_ext == 'png' else 'image/jpeg'
        download_name = f"colored_{file.filename.rsplit('.', 1)[0]}.{output_ext}"
        
        return send_file(
            output_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )
        
    except RequestEntityTooLarge:
        return jsonify({'error': f'File too large. Maximum {MAX_FILE_SIZE//1024//1024}MB allowed'}), 413
        
    except Exception as e:
        logger.error(f"Error in change_background_color: {e}")
        return jsonify({'error': f'Processing failed: {str(e)}'}), 500
        
    finally:
        # Always cleanup temp files
        cleanup_file(input_path)
        # Note: output_path will be cleaned up by Flask after send_file

@bg_api.route('/status', methods=['GET'])
def get_status():
    """Get service status and memory usage"""
    try:
        memory_info = isnet_tiny_service.get_memory_usage()
        
        return jsonify({
            'status': 'ready',
            'model': 'isnet-general-tiny',
            'memory': memory_info,
            'max_file_size_mb': MAX_FILE_SIZE // 1024 // 1024,
            'max_dimension': MAX_DIMENSION,
            'allowed_extensions': list(ALLOWED_EXTENSIONS),
            'endpoints': {
                'remove_background': '/api/bg/remove',
                'change_color': '/api/bg/change_color'
            }
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@bg_api.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    try:
        # Quick memory check
        memory_info = isnet_tiny_service.get_memory_usage()
        
        if 'error' in memory_info:
            return jsonify({
                'status': 'unhealthy',
                'error': memory_info['error']
            }), 500
        
        # Check if memory usage is reasonable
        if memory_info.get('rss_mb', 0) > 400:  # Conservative for 512MB Railway
            return jsonify({
                'status': 'warning',
                'message': 'High memory usage',
                'memory_mb': memory_info.get('rss_mb', 0)
            }), 200
        
        return jsonify({
            'status': 'healthy',
            'memory_mb': memory_info.get('rss_mb', 0),
            'model_loaded': memory_info.get('model_loaded', False)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@bg_api.route('/clear_cache', methods=['POST'])
def clear_cache():
    """Clear model cache and free memory (for debugging/recovery)"""
    try:
        isnet_tiny_service.clear_memory()
        
        return jsonify({
            'status': 'cache_cleared',
            'message': 'Model cache cleared successfully'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Error handlers
@bg_api.errorhandler(413)
def request_entity_too_large(error):
    return jsonify({
        'error': f'File too large. Maximum {MAX_FILE_SIZE//1024//1024}MB allowed'
    }), 413

@bg_api.errorhandler(400)
def bad_request(error):
    return jsonify({
        'error': 'Bad request'
    }), 400

@bg_api.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        'error': 'Internal server error'
    }), 500

# Initialize temp directory when blueprint is registered
init_temp_dir()

# Register cleanup function (called on app shutdown)
import atexit
atexit.register(cleanup_temp_dir)
