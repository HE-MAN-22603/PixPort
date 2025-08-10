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
        
        # Get upload folder from config (handles both development and Railway)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        file_path = os.path.join(upload_folder, filename)
        
        logger.info(f"Attempting to serve upload file: {filename} from path: {file_path}")
        logger.info(f"Upload folder configured as: {upload_folder}")
        logger.info(f"File exists: {os.path.exists(file_path)}")
        
        # Ensure the file is within the upload directory (prevent path traversal)
        if not os.path.abspath(file_path).startswith(os.path.abspath(upload_folder)):
            logger.error(f"Path traversal attempt blocked: {filename} from IP: {request.remote_addr}")
            abort(403)  # Forbidden
        
        # Check if file exists and is a file (not directory)
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.warning(f"Upload file not found: {filename} at path: {file_path}")
            # List available files for debugging
            try:
                if os.path.exists(upload_folder):
                    available_files = os.listdir(upload_folder)
                    logger.info(f"Available files in upload folder: {available_files}")
                else:
                    logger.error(f"Upload folder does not exist: {upload_folder}")
            except Exception as e:
                logger.error(f"Error listing upload folder contents: {str(e)}")
            abort(404)
        
        # Check file size (prevent serving huge files)
        file_size = os.path.getsize(file_path)
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)  # 16MB default
        if file_size > max_size:
            logger.warning(f"File too large: {filename} ({file_size} bytes)")
            abort(413)  # Payload Too Large
        
        # Add security headers and serve file
        # Check if this is a download request (has download parameter)
        is_download = request.args.get('download', 'false').lower() == 'true'
        
        response = send_file(
            file_path,
            as_attachment=is_download,
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
        
        logger.info(f"Attempting to serve processed file: {filename} from path: {file_path}")
        logger.info(f"Processed folder configured as: {processed_folder}")
        logger.info(f"File exists: {os.path.exists(file_path)}")
        
        # Ensure the file is within the processed directory
        if not os.path.abspath(file_path).startswith(os.path.abspath(processed_folder)):
            logger.error(f"Path traversal attempt blocked: {filename} from IP: {request.remote_addr}")
            abort(403)
        
        # Check if file exists and is a file
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            logger.warning(f"Processed file not found: {filename} at path: {file_path}")
            # Try multiple fallback strategies
            
            # Strategy 1: Look for similar files with different processing suffixes
            try:
                processed_files = os.listdir(processed_folder)
                base_name = filename.split('.')[0].split('_')[0]  # Get base UUID
                
                # Look for files starting with the same UUID base
                similar_files = [f for f in processed_files if f.startswith(base_name) and f != filename]
                
                if similar_files:
                    logger.info(f"Found similar files for {filename}: {similar_files}")
                    # Use the most recent similar file
                    newest_file = max(similar_files, key=lambda x: os.path.getmtime(
                        os.path.join(processed_folder, x)))
                    logger.info(f"Redirecting to similar file: {newest_file}")
                    from flask import redirect, url_for
                    return redirect(url_for('static_files.serve_processed', filename=newest_file))
                
                # Strategy 2: Look for files with partial UUID match (handle truncated UUIDs)
                if len(base_name) < 36:  # UUID should be 36 chars with dashes
                    logger.info(f"Detected potentially truncated UUID: {base_name}")
                    partial_matches = [f for f in processed_files 
                                     if f.startswith(base_name[:8])  # First 8 chars
                                     and f != filename]
                    
                    if partial_matches:
                        logger.info(f"Found partial UUID matches: {partial_matches}")
                        newest_file = max(partial_matches, key=lambda x: os.path.getmtime(
                            os.path.join(processed_folder, x)))
                        logger.info(f"Redirecting to partial match: {newest_file}")
                        from flask import redirect, url_for
                        return redirect(url_for('static_files.serve_processed', filename=newest_file))
                
                # Strategy 3: Look for any files with similar timestamps or names
                name_part = filename.split('_')[1] if '_' in filename else None
                if name_part:
                    name_matches = [f for f in processed_files 
                                  if name_part in f and f != filename]
                    if name_matches:
                        logger.info(f"Found name-based matches: {name_matches}")
                        newest_file = max(name_matches, key=lambda x: os.path.getmtime(
                            os.path.join(processed_folder, x)))
                        logger.info(f"Redirecting to name-based match: {newest_file}")
                        from flask import redirect, url_for
                        return redirect(url_for('static_files.serve_processed', filename=newest_file))
                        
            except Exception as e:
                logger.error(f"Error looking for similar files: {str(e)}")
            
            # Log the missing file for debugging
            logger.error(f"No fallback found for missing file: {filename}")
            logger.error(f"Available files in processed folder: {os.listdir(processed_folder) if os.path.exists(processed_folder) else 'Folder does not exist'}")
            abort(404)
        
        # Check file size
        file_size = os.path.getsize(file_path)
        max_size = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if file_size > max_size:
            logger.warning(f"Processed file too large: {filename} ({file_size} bytes)")
            abort(413)
        
        # Add security headers and serve file
        # Check if this is a download request (has download parameter)
        is_download = request.args.get('download', 'false').lower() == 'true'
        
        response = send_file(
            file_path,
            as_attachment=is_download,
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
