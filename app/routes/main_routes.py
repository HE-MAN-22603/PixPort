"""
Main page routes for PixPort
"""

from flask import Blueprint, render_template, jsonify, request, current_app, abort, send_file
import os
import re
import time
from pathlib import Path
from typing import Dict, Any, Optional
from functools import wraps
from werkzeug.exceptions import BadRequest, NotFound, InternalServerError

main_bp = Blueprint('main', __name__)

# Security utilities
def sanitize_filename(filename: str) -> Optional[str]:
    """Sanitize and validate filename to prevent directory traversal attacks."""
    if not filename or not isinstance(filename, str):
        return None
    
    # Remove any path separators and suspicious characters
    filename = re.sub(r'[^a-zA-Z0-9._-]', '', filename)
    
    # Check for empty filename or only dots/dashes
    if not filename or filename in ['.', '..'] or filename.startswith('.'):
        return None
    
    # Limit filename length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename

def validate_request_data(data: Dict[str, Any], required_fields: list) -> Dict[str, Any]:
    """Validate request data contains required fields."""
    errors = []
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")
    
    if errors:
        raise BadRequest(f"Validation errors: {', '.join(errors)}")
    
    return data

def add_security_headers(response):
    """Add security headers to response."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

def rate_limit_decorator(max_requests: int = 10, window: int = 60):
    """Simple rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting using IP address
            # In production, use Redis or a proper rate limiting solution
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = int(time.time())
            
            # For demo purposes, we'll just log the attempt
            current_app.logger.info(f"API request from {client_ip} at {current_time}")
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@main_bp.route('/health')
def health():
    """Health check endpoint"""
    try:
        import time
        return jsonify({
            'status': 'healthy',
            'service': 'PixPort',
            'version': '1.0.0',
            'timestamp': int(time.time()),
            'environment': 'railway' if os.environ.get('RAILWAY_ENVIRONMENT_NAME') else 'local'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@main_bp.route('/status')
def status():
    """Application status endpoint"""
    upload_folder_exists = os.path.exists(current_app.config['UPLOAD_FOLDER'])
    processed_folder_exists = os.path.exists(current_app.config['PROCESSED_FOLDER'])
    
    return jsonify({
        'status': 'operational',
        'upload_folder': upload_folder_exists,
        'processed_folder': processed_folder_exists,
        'max_file_size': current_app.config['MAX_CONTENT_LENGTH'],
        'allowed_extensions': list(current_app.config['ALLOWED_EXTENSIONS'])
    })

@main_bp.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({'message': 'pong'})

@main_bp.route('/features')
def features():
    """Features page"""
    features_list = [
        {
            'title': 'AI-Powered Background Removal',
            'description': 'Automatically remove photo backgrounds using advanced ML models',
            'icon': '🤖'
        },
        {
            'title': 'Smart Background Changing',
            'description': 'Replace backgrounds with solid colors or custom images',
            'icon': '🎨'
        },
        {
            'title': 'Passport Size Compliance',
            'description': 'Support for 60+ international passport photo dimensions',
            'icon': '📐'
        },
        {
            'title': 'Photo Enhancement',
            'description': 'Improve photo quality with professional-grade processing',
            'icon': '🔧'
        },
        {
            'title': 'User-Friendly Interface',
            'description': 'Modern, responsive design with drag-and-drop functionality',
            'icon': '📱'
        },
        {
            'title': 'Fast Processing',
            'description': 'Optimized for quick turnaround times',
            'icon': '⚡'
        }
    ]
    
    return render_template('features.html', features=features_list)

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')

@main_bp.route('/preview/<filename>')
def preview(filename):
    """Preview uploaded image"""
    # Sanitize filename for security
    sanitized_filename = sanitize_filename(filename)
    if not sanitized_filename:
        current_app.logger.warning(f"Invalid filename attempted in preview: {filename}")
        abort(400)
    
    return render_template('preview.html', filename=sanitized_filename)

@main_bp.route('/result/<filename>')
def result(filename):
    """Show processing result"""
    import datetime
    
    # Sanitize and validate filename
    sanitized_filename = sanitize_filename(filename)
    if not sanitized_filename:
        current_app.logger.warning(f"Invalid filename attempted: {filename}")
        abort(400)
    
    try:
        # Check if processed file exists
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
        
        if not os.path.exists(processed_path):
            # Try to find similar files (for files with different processing suffixes)
            try:
                if os.path.exists(current_app.config['PROCESSED_FOLDER']):
                    files = os.listdir(current_app.config['PROCESSED_FOLDER'])
                    base_name = sanitized_filename.split('.')[0]
                    # Look for files with the same base name but different suffixes
                    similar_files = [f for f in files if base_name.split('_')[0] in f]
                    if similar_files:
                        # Use the most recent match
                        sanitized_filename = max(similar_files, key=lambda x: os.path.getmtime(
                            os.path.join(current_app.config['PROCESSED_FOLDER'], x)))
                        current_app.logger.info(f"Redirected to similar file: {sanitized_filename}")
                    else:
                        current_app.logger.warning(f"No processed file found for: {sanitized_filename}")
                        abort(404)
                else:
                    current_app.logger.error("Processed folder does not exist")
                    abort(404)
            except OSError as e:
                current_app.logger.error(f"Error accessing processed folder: {str(e)}")
                abort(404)
        
        return render_template('result.html', 
                             filename=sanitized_filename, 
                             current_date=datetime.datetime.now())
                             
    except Exception as e:
        # Don't catch abort exceptions - let them bubble up
        if hasattr(e, 'code') and hasattr(e, 'name'):
            # This is a Werkzeug HTTP exception (like abort(404)), re-raise it
            raise e
        
        current_app.logger.error(f"Unexpected error in result route: {str(e)}")
        abort(500)

# Redirect routes for old URLs
@main_bp.route('/processed/<filename>')
def redirect_processed(filename):
    """Redirect old processed URLs to static routes"""
    from flask import redirect
    return redirect(f'/static/processed/{filename}', code=301)

@main_bp.route('/uploads/<filename>')
def redirect_uploads(filename):
    """Redirect old upload URLs to static routes"""
    from flask import redirect
    return redirect(f'/static/uploads/{filename}', code=301)

# API Routes
@main_bp.route('/api/image-info/<filename>')
def image_info(filename):
    """Get image information"""
    try:
        from PIL import Image
        import time
        
        # Sanitize and validate filename
        sanitized_filename = sanitize_filename(filename)
        if not sanitized_filename:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        # Check in both upload and processed folders
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sanitized_filename)
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
        
        image_path = None
        if os.path.exists(processed_path):
            image_path = processed_path
        elif os.path.exists(upload_path):
            image_path = upload_path
        else:
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
        
        # Get file stats
        file_stats = os.stat(image_path)
        file_size = file_stats.st_size
        modified_time = time.ctime(file_stats.st_mtime)
        
        # Get image information
        with Image.open(image_path) as img:
            width, height = img.size
            format = img.format
            mode = img.mode
            
            # Get DPI if available
            dpi = img.info.get('dpi', (300, 300))
            if isinstance(dpi, tuple):
                dpi = dpi[0]
        
        return jsonify({
            'success': True,
            'filename': sanitized_filename,
            'width': width,
            'height': height,
            'format': format,
            'mode': mode,
            'file_size': file_size,
            'dpi': int(dpi) if dpi else 300,
            'color_space': 'sRGB',  # Assume sRGB for web images
            'modified': modified_time,
            'processing_time': getattr(current_app, 'last_processing_time', 0.0)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get image info',
            'message': str(e)
        }), 500

@main_bp.route('/api/download/<filename>')
@rate_limit_decorator(max_requests=50, window=60)
def download_image(filename):
    """Download processed image"""
    try:
        from PIL import Image
        import io
        import tempfile
        
        # Optional reportlab import for PDF functionality
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.units import inch
            REPORTLAB_AVAILABLE = True
        except ImportError:
            REPORTLAB_AVAILABLE = False
        
        # Sanitize and validate filename
        sanitized_filename = sanitize_filename(filename)
        if not sanitized_filename:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        # Get format and quality from query parameters
        requested_format = request.args.get('format', 'JPEG').upper()
        quality = int(request.args.get('quality', 95))
        
        # Validate format
        allowed_formats = ['JPEG', 'PNG', 'WEBP', 'PDF']
        if requested_format not in allowed_formats:
            requested_format = 'JPEG'
        
        # Validate quality
        quality = max(60, min(100, quality))
        
        # Check if file exists in processed folder
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
        
        if not os.path.exists(processed_path):
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        try:
            if requested_format == 'PDF':
                # Check if reportlab is available for PDF generation
                if not REPORTLAB_AVAILABLE:
                    return jsonify({
                        'success': False,
                        'error': 'PDF generation not available - reportlab not installed'
                    }), 501
                
                # Create PDF with the image
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                    # Open the image
                    with Image.open(processed_path) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'LA', 'P'):
                            img = img.convert('RGB')
                        
                        # Calculate image size for PDF (fit to letter size with margins)
                        img_width, img_height = img.size
                        max_width = 6.5 * inch  # Letter width minus margins
                        max_height = 9 * inch   # Letter height minus margins
                        
                        # Calculate scaling to fit within bounds
                        scale_x = max_width / img_width
                        scale_y = max_height / img_height
                        scale = min(scale_x, scale_y, 1.0)  # Don't upscale
                        
                        pdf_img_width = img_width * scale
                        pdf_img_height = img_height * scale
                        
                        # Center the image on the page
                        x = (letter[0] - pdf_img_width) / 2
                        y = (letter[1] - pdf_img_height) / 2
                        
                        # Save image to temporary buffer for PDF
                        img_buffer = io.BytesIO()
                        img.save(img_buffer, format='JPEG', quality=quality)
                        img_buffer.seek(0)
                        
                        # Create PDF
                        c = canvas.Canvas(temp_file.name, pagesize=letter)
                        
                        # Save image to another temp file for PDF canvas
                        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as img_temp:
                            img.save(img_temp.name, format='JPEG', quality=quality)
                            c.drawImage(img_temp.name, x, y, pdf_img_width, pdf_img_height)
                            
                            # Clean up temp image file
                            try:
                                os.unlink(img_temp.name)
                            except:
                                pass
                        
                        c.save()
                    
                    # Generate download filename
                    base_name = os.path.splitext(sanitized_filename)[0]
                    download_filename = f"{base_name}.pdf"
                    
                    # Send PDF file
                    response = send_file(
                        temp_file.name,
                        as_attachment=True,
                        download_name=download_filename,
                        mimetype='application/pdf'
                    )
                    
                    # Clean up temp file after sending
                    def remove_temp_file(response):
                        try:
                            os.unlink(temp_file.name)
                        except:
                            pass
                        return response
                    response.call_on_close(lambda: os.unlink(temp_file.name) if os.path.exists(temp_file.name) else None)
                    
            else:
                # Handle image formats (JPEG, PNG, WEBP)
                if requested_format == 'PNG':
                    # For PNG, send the original file if it's already PNG
                    original_ext = os.path.splitext(sanitized_filename)[1].lower()
                    if original_ext == '.png':
                        response = send_file(
                            processed_path,
                            as_attachment=True,
                            download_name=sanitized_filename,
                            mimetype='image/png'
                        )
                    else:
                        # Convert to PNG
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                            with Image.open(processed_path) as img:
                                # Ensure RGBA mode for PNG with transparency support
                                if img.mode != 'RGBA':
                                    img = img.convert('RGBA')
                                img.save(temp_file.name, format='PNG', optimize=True)
                            
                            # Generate download filename
                            base_name = os.path.splitext(sanitized_filename)[0]
                            download_filename = f"{base_name}.png"
                            
                            response = send_file(
                                temp_file.name,
                                as_attachment=True,
                                download_name=download_filename,
                                mimetype='image/png'
                            )
                            
                            # Clean up temp file
                            response.call_on_close(lambda: os.unlink(temp_file.name) if os.path.exists(temp_file.name) else None)
                            
                else:
                    # Handle JPEG and WEBP
                    with tempfile.NamedTemporaryFile(suffix=f'.{requested_format.lower()}', delete=False) as temp_file:
                        with Image.open(processed_path) as img:
                            # Convert to RGB for JPEG/WEBP (remove transparency)
                            if img.mode in ('RGBA', 'LA', 'P'):
                                # Create white background for transparent images
                                background = Image.new('RGB', img.size, (255, 255, 255))
                                if img.mode == 'P':
                                    img = img.convert('RGBA')
                                background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                                img = background
                            elif img.mode != 'RGB':
                                img = img.convert('RGB')
                            
                            # Save with format-specific options
                            save_kwargs = {'format': requested_format, 'quality': quality, 'optimize': True}
                            if requested_format == 'JPEG':
                                save_kwargs['progressive'] = True
                            
                            img.save(temp_file.name, **save_kwargs)
                        
                        # Generate download filename
                        base_name = os.path.splitext(sanitized_filename)[0]
                        file_ext = 'jpg' if requested_format == 'JPEG' else requested_format.lower()
                        download_filename = f"{base_name}.{file_ext}"
                        
                        # Determine MIME type
                        mime_types = {
                            'JPEG': 'image/jpeg',
                            'PNG': 'image/png',
                            'WEBP': 'image/webp'
                        }
                        
                        response = send_file(
                            temp_file.name,
                            as_attachment=True,
                            download_name=download_filename,
                            mimetype=mime_types.get(requested_format, 'image/jpeg')
                        )
                        
                        # Clean up temp file
                        response.call_on_close(lambda: os.unlink(temp_file.name) if os.path.exists(temp_file.name) else None)
            
            # Add security headers
            response = add_security_headers(response)
            
            return response
            
        except Exception as e:
            current_app.logger.error(f"Error processing download for {sanitized_filename} in {requested_format} format: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to convert image to {requested_format} format'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in download_image: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@main_bp.route('/api/testroute/<filename>')
def test_route(filename):
    """Test route to debug issues"""
    return jsonify({
        'success': True,
        'message': 'Test route working',
        'filename': filename
    })

@main_bp.route('/api/comparison/<filename>')
def comparison_images(filename):
    """Get original and processed image for comparison"""
    try:
        # Sanitize and validate filename
        sanitized_filename = sanitize_filename(filename)
        if not sanitized_filename:
            current_app.logger.warning(f"Invalid filename in comparison: {filename}")
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        # Log the comparison request for debugging
        current_app.logger.info(f"Comparison request for filename: {sanitized_filename}")
        
        # Check if processed file exists first
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
        if not os.path.exists(processed_path):
            current_app.logger.warning(f"Processed file not found for comparison: {sanitized_filename}")
            return jsonify({
                'success': False,
                'error': 'Processed file not found',
                'debug': f'Path checked: {processed_path}'
            }), 404
        
        # Try to find the original filename by removing processing suffixes
        original_filename = sanitized_filename
        suffixes = ['_no_bg', '_bg_white', '_bg_light_blue', '_bg_light_gray', '_bg_cream', 
                   '_enhanced', '_passport_us', '_passport_uk', '_passport_photo', 
                   '_professional_passport', '_processed', '_bg_removed', '_bg_changed', '_resized',
                   '_print_sheet', '_4x6', '_copies']
        
        # Remove suffixes in order of likelihood
        for suffix in suffixes:
            if suffix in original_filename:
                original_filename = original_filename.replace(suffix, '', 1)
                break
        
        # Remove any trailing suffixes that might have been added during processing
        # Handle cases like '_4x6_4copies_hashcode'
        import re
        original_filename = re.sub(r'_\d+x\d+.*$', '', original_filename)  # Remove dimension specs
        original_filename = re.sub(r'_\d+copies.*$', '', original_filename)  # Remove copy specs
        original_filename = re.sub(r'_[a-f0-9]{8,}.*$', '', original_filename)  # Remove hash codes
        
        current_app.logger.info(f"Looking for original file: {original_filename}")
        
        # Verify original file exists
        original_path = os.path.join(current_app.config['UPLOAD_FOLDER'], original_filename)
        if not os.path.exists(original_path):
            # Try to find any file with similar name
            try:
                if os.path.exists(current_app.config['UPLOAD_FOLDER']):
                    upload_files = os.listdir(current_app.config['UPLOAD_FOLDER'])
                    base_name = original_filename.split('.')[0]
                    # More flexible matching for original files
                    matching_files = []
                    
                    # First try exact base name match
                    for f in upload_files:
                        if base_name in f.split('.')[0] or f.split('.')[0] in base_name:
                            matching_files.append(f)
                    
                    if matching_files:
                        # Use the most recent match
                        original_filename = max(matching_files, key=lambda x: os.path.getmtime(
                            os.path.join(current_app.config['UPLOAD_FOLDER'], x)))
                        current_app.logger.info(f"Found matching original file: {original_filename}")
                    else:
                        current_app.logger.warning(f"No original file found. Checked {len(upload_files)} files in upload folder")
                        return jsonify({
                            'success': False,
                            'error': 'Original file not found',
                            'debug': f'Base name: {base_name}, Upload files: {upload_files[:10]}'
                        }), 404
                else:
                    current_app.logger.error("Upload folder does not exist")
                    return jsonify({
                        'success': False,
                        'error': 'Upload folder not accessible'
                    }), 404
            except Exception as e:
                current_app.logger.error(f"Error searching for original file: {str(e)}")
                return jsonify({
                    'success': False,
                    'error': 'Unable to locate original file',
                    'debug': str(e)
                }), 404
        
        response = jsonify({
            'success': True,
            'original_filename': original_filename,
            'processed_filename': sanitized_filename
        })
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in comparison_images: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get comparison data',
            'message': str(e)
        }), 500

@main_bp.route('/api/save-image', methods=['POST'])
def save_image():
    """Save processed image to downloads or user specified location"""
    try:
        # Get form data
        action = request.form.get('action', 'save_image')
        image_data = request.form.get('image_data')
        
        if not image_data:
            return jsonify({
                'success': False,
                'error': 'No image data provided'
            }), 400
        
        # For now, we'll just return success since the frontend handles download
        # In a real implementation, you might save to user's account or cloud storage
        return jsonify({
            'success': True,
            'message': 'Image saved successfully',
            'saved_path': 'downloads/processed_image.png'  # Simulated path
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to save image',
            'message': str(e)
        }), 500

@main_bp.route('/api/upload-status/<filename>')
def upload_status(filename):
    """Check upload status and file information"""
    try:
        # Sanitize and validate filename
        sanitized_filename = sanitize_filename(filename)
        if not sanitized_filename:
            return jsonify({
                'success': False,
                'error': 'Invalid filename'
            }), 400
        
        # Check if file exists in upload folder
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], sanitized_filename)
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
        
        if os.path.exists(processed_path):
            status = 'processed'
            file_path = processed_path
        elif os.path.exists(upload_path):
            status = 'uploaded'
            file_path = upload_path
        else:
            return jsonify({
                'success': False,
                'status': 'not_found',
                'error': 'File not found'
            }), 404
        
        # Get file stats
        file_stats = os.stat(file_path)
        file_size = file_stats.st_size
        
        return jsonify({
            'success': True,
            'status': status,
            'filename': sanitized_filename,
            'file_size': file_size,
            'exists': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to check upload status',
            'message': str(e)
        }), 500

@main_bp.route('/api/download-print-sheet', methods=['POST'])
def download_print_sheet():
    """Download print sheet in specified format"""
    try:
        from .print_routes import create_print_sheet
        
        data = request.get_json()
        
        # Validate input
        image_url = data.get('image_url', '')
        paper_size = data.get('paper_size', 'A4')
        images_per_row = int(data.get('images_per_row', 3))
        images_per_col = int(data.get('images_per_col', 3)) 
        add_cut_guides = data.get('add_cut_guides', True)
        output_format = data.get('format', 'PNG').upper()
        
        # Validate format
        if output_format not in ['PNG', 'JPEG', 'PDF']:
            return jsonify({'success': False, 'error': 'Invalid format'}), 400
        
        # Extract filename from image_url if it's a relative path
        filename = None
        if image_url:
            if image_url.startswith('/static/processed/'):
                filename = image_url.replace('/static/processed/', '')
            elif '/' in image_url:
                filename = image_url.split('/')[-1]
            else:
                filename = image_url
        
        # Sanitize filename
        filename = sanitize_filename(filename) if filename else None
        if not filename:
            return jsonify({'success': False, 'error': 'Invalid filename'}), 400
        
        # Check if source file exists
        source_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'error': 'Source file not found'}), 404
        
        # Create parameters for the print sheet generation
        # Convert images_per_row/col to sheet_type and num_photos format
        sheet_type = paper_size
        num_photos = images_per_row * images_per_col
        photo_size = 'US'  # Default to US passport size
        margin_size = 'normal'
        
        # Generate print sheet in requested format
        sheet_filename = create_print_sheet(
            source_path, 
            filename,
            sheet_type, 
            num_photos, 
            photo_size, 
            margin_size, 
            add_cut_guides,
            output_format
        )
        
        sheet_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sheet_filename)
        
        # Determine MIME type
        if output_format == 'PDF':
            mimetype = 'application/pdf'
        elif output_format == 'JPEG':
            mimetype = 'image/jpeg'
        else:  # PNG
            mimetype = 'image/png'
        
        return send_file(
            sheet_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=sheet_filename
        )
        
    except ImportError as e:
        current_app.logger.error(f"Import error in download_print_sheet: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Print functionality not available',
            'message': str(e)
        }), 500
    except Exception as e:
        current_app.logger.error(f"Error downloading print sheet: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Failed to download print sheet',
            'message': str(e)
        }), 500
