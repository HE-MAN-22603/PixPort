"""
Static file serving routes for Railway deployment with enhanced security
"""

import os
import logging
from flask import Blueprint, send_file, current_app, abort, request
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
static_bp = Blueprint('static_files', __name__)

def validate_filename(filename):
    """Validate filename for security"""
    if not filename:
        return False
    
    # Secure the filename to prevent path traversal
    secured = secure_filename(filename)
    if secured != filename:
        logger.warning(f"Potentially malicious filename blocked: {filename}")
        return False
    
    # Check file extension
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'jpg', 'jpeg', 'png', 'heic', 'webp'})
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        logger.warning(f"Disallowed file extension: {ext}")
        return False
    
    # Additional security checks
    dangerous_patterns = ['..', '/', '\\', '~', '$', '&', '|', ';', '<', '>', '`']
    if any(pattern in filename for pattern in dangerous_patterns):
        logger.warning(f"Dangerous pattern in filename: {filename}")
        return False
    
    return True

def get_cache_headers():
    """Get appropriate cache headers for images"""
    return {
        'Cache-Control': 'public, max-age=3600',  # 1 hour cache
        'Expires': (datetime.now() + timedelta(hours=1)).strftime('%a, %d %b %Y %H:%M:%S GMT'),
        'ETag': str(hash(request.path))
    }

@static_bp.route('/uploads/<filename>')
def serve_upload(filename):
    """Securely serve uploaded files with validation and caching"""
    try:
        # Validate filename
        if not validate_filename(filename):
            logger.warning(f"Invalid filename requested: {filename} from IP: {request.remote_addr}")
            abort(400)  # Bad Request instead of 404 to indicate invalid request
        
        # Construct safe path
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        # Ensure the file is within the upload directory (prevent path traversal)
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            logger.error(f"Path traversal attempt blocked: {filename} from IP: {request.remote_addr}")
            abort(403)  # Forbidden
        
        # Check if file exists and is a file (not directory)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.info(f"File not found: {filename}")
            abort(404)
        
        # Check file size (prevent serving huge files)
        file_size = os.path.getsize(file_path)
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB default
        if file_size > max_size:
            logger.warning(f"File too large: {filename} ({file_size} bytes)")
            abort(413)  # Payload Too Large
        
        # Add security headers and serve file
        response = send_file(
            file_path,
            as_attachment=False,
            conditional=True  # Enable conditional requests for better caching
        )
        
        # Add cache headers
        for key, value in get_cache_headers().items():
            response.headers[key] = value
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving upload file {filename}: {str(e)}")
        abort(500)

@static_bp.route('/processed/<filename>')
def serve_processed(filename):
    """Securely serve processed files with validation and caching"""
    try:
        # Validate filename
        if not validate_filename(filename):
            logger.warning(f"Invalid processed filename requested: {filename} from IP: {request.remote_addr}")
            abort(400)
        
        # Construct safe path
        processed_folder = current_app.config['PROCESSED_FOLDER']
        file_path = os.path.join(processed_folder, filename)
        
        # Ensure the file is within the processed directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(processed_folder)):
            logger.error(f"Path traversal attempt blocked: {filename} from IP: {request.remote_addr}")
            abort(403)
        
        # Check if file exists and is a file
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.info(f"Processed file not found: {filename}")
            abort(404)
        
        # Check file size
        file_size = os.path.getsize(file_path)
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            logger.warning(f"Processed file too large: {filename} ({file_size} bytes)")
            abort(413)
        
        # Add security headers and serve file
        response = send_file(
            file_path,
            as_attachment=False,
            conditional=True
        )
        
        # Add cache headers (longer cache for processed files)
        response.headers['Cache-Control'] = 'public, max-age=7200'  # 2 hours
        response.headers['Expires'] = (datetime.now() + timedelta(hours=2)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        response.headers['ETag'] = str(hash(request.path + str(os.path.getmtime(file_path))))
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        return response
        
    except Exception as e:
        logger.error(f"Error serving processed file {filename}: {str(e)}")
        abort(500)
