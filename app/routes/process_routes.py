"""
Image processing routes for PixPort
"""

import os
import uuid
from flask import Blueprint, request, jsonify, current_app, redirect, url_for
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from ..services.bg_remover_lite import remove_background
from ..services.bg_changer import change_background, smart_background_change
from ..services.enhancer import enhance_image
from ..services.photo_resizer import resize_to_passport
from ..services.utils import allowed_file, save_uploaded_file, validate_image_file
from ..services.model_manager import model_manager

process_bp = Blueprint('process', __name__)

# Initialize limiter for processing routes with improved limits
limiter = Limiter(key_func=get_remote_address)

# Memory management helper function
def check_memory_availability():
    """Check if system has enough memory for AI processing"""
    try:
        import psutil
        memory = psutil.virtual_memory()
        process = psutil.Process()
        
        # Get current memory usage
        process_memory_mb = process.memory_info().rss / 1024 / 1024
        available_memory_mb = memory.available / 1024 / 1024
        
        # Check if we have at least 200MB available and process is under 400MB
        if available_memory_mb < 200 or process_memory_mb > 400:
            return False, f"Insufficient memory (Available: {available_memory_mb:.1f}MB, Process: {process_memory_mb:.1f}MB)"
        
        return True, "Memory OK"
        
    except Exception as e:
        # If we can't check memory, allow processing but log warning
        current_app.logger.warning(f"Memory check failed: {e}")
        return True, "Memory check unavailable"

# Input validation helper functions
def validate_filename_parameter(filename):
    """Validate filename parameter for security"""
    if not filename:
        return False, "No filename provided"
    
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False, "Invalid filename - path traversal detected"
    
    # Check filename length
    if len(filename) > 255:
        return False, "Filename too long"
    
    # Check for valid extension
    if '.' not in filename:
        return False, "No file extension found"
    
    ext = filename.rsplit('.', 1)[1].lower()
    allowed_extensions = {'jpg', 'jpeg', 'png', 'heic', 'webp'}
    if ext not in allowed_extensions:
        return False, f"Invalid file extension. Allowed: {allowed_extensions}"
    
    return True, "Valid filename"

def validate_enhancement_parameters(params):
    """Validate enhancement parameter values"""
    valid_ranges = {
        'contrast': (-100, 100),
        'brightness': (-100, 100),
        'sharpness': (0, 100),
        'saturation': (-100, 100),
        'hue': (-180, 180),
        'noise': (0, 100),
        'blur': (0, 50),
        'highlight': (-100, 100),
        'shadow': (-100, 100),
        'temperature': (-100, 100),
        'tint': (-100, 100)
    }
    
    for param, value in params.items():
        if param in valid_ranges:
            min_val, max_val = valid_ranges[param]
            try:
                value = float(value)
                if value < min_val or value > max_val:
                    return False, f"Parameter '{param}' must be between {min_val} and {max_val}"
            except (ValueError, TypeError):
                return False, f"Parameter '{param}' must be a number"
    
    return True, "Valid parameters"

def find_input_file(filename, config):
    """Find input file in upload or processed folder"""
    # Check upload folder first
    upload_path = os.path.join(config['UPLOAD_FOLDER'], filename)
    if os.path.exists(upload_path):
        return upload_path
    
    # Check processed folder
    processed_path = os.path.join(config['PROCESSED_FOLDER'], filename)
    if os.path.exists(processed_path):
        return processed_path
    
    return None

# Custom rate limit error handler
@process_bp.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please wait before trying again.',
        'retry_after': getattr(e, 'retry_after', None),
        'description': str(e.description)
    }), 429

@process_bp.route('/upload', methods=['POST'])
@limiter.limit("30 per minute; 5 per 10 seconds")  # Allow bursts but limit sustained usage
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename, current_app.config['ALLOWED_EXTENSIONS']):
        return jsonify({
            'error': 'Invalid file type',
            'allowed_types': list(current_app.config['ALLOWED_EXTENSIONS'])
        }), 400
    
    try:
        # Generate unique filename
        filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
        filepath = save_uploaded_file(file, filename, current_app.config['UPLOAD_FOLDER'])
        
        return jsonify({
            'success': True,
            'filename': filename,
            'message': 'File uploaded successfully',
            'redirect': url_for('main.preview', filename=filename)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Upload failed',
            'message': str(e)
        }), 500

@process_bp.route('/remove_background/<filename>', methods=['POST'])
@limiter.limit("5 per minute")
def remove_bg(filename):
    """Remove background from image"""
    # Check memory availability first
    memory_ok, memory_msg = check_memory_availability()
    if not memory_ok:
        current_app.logger.warning(f"Memory check failed for background removal: {memory_msg}")
        return jsonify({
            'error': 'Service temporarily unavailable',
            'message': 'Server is under high load. Please try again in a few moments.',
            'fallback_available': True
        }), 503
    
    # Get additional options from JSON body if provided
    data = request.get_json() or {}
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
    try:
        # Generate output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_no_bg{ext}"
        output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
        
        # Process image
        remove_background(input_path, output_path, current_app.config['REMBG_MODEL'])
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'message': 'Background removed successfully',
            'preview_url': url_for('static', filename='processed/' + output_filename)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Background removal failed',
            'message': str(e)
        }), 500

@process_bp.route('/change_background/<filename>', methods=['POST'])
@limiter.limit("5 per minute")
def change_bg(filename):
    """Change background color - always removes background first, then applies new color"""
    data = request.get_json() or {}
    
    color = data.get('color', 'white')
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
    # Handle hex colors and predefined colors
    rgb_color = None
    
    if color in current_app.config['BACKGROUND_COLORS']:
        # Predefined color
        rgb_color = current_app.config['BACKGROUND_COLORS'][color]
    elif color.startswith('#') and len(color) == 7:
        # Hex color validation and conversion
        try:
            hex_color = color[1:]
            if all(c in '0123456789ABCDEFabcdef' for c in hex_color):
                rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            else:
                raise ValueError("Invalid hex color format")
        except (ValueError, IndexError):
            return jsonify({
                'error': 'Invalid hex color format',
                'message': 'Hex color must be in format #RRGGBB (e.g., #ffffff)'
            }), 400
    else:
        return jsonify({
            'error': 'Invalid color format',
            'message': 'Color must be a predefined name or hex format (#RRGGBB)',
            'available_colors': list(current_app.config['BACKGROUND_COLORS'].keys()),
            'hex_example': '#ffffff'
        }), 400
    
    try:
        # Generate intermediate and final output filenames
        name, ext = os.path.splitext(filename)
        
        # Step 1: Always remove background first to prevent color overlapping
        temp_no_bg_filename = f"{name}_temp_no_bg_{uuid.uuid4().hex[:8]}{ext}"
        temp_no_bg_path = os.path.join(current_app.config['PROCESSED_FOLDER'], temp_no_bg_filename)
        
        # Remove background using AI model
        remove_background(input_path, temp_no_bg_path, current_app.config['REMBG_MODEL'])
        
        # Step 2: Apply new background color to clean transparent image
        # Sanitize color name for filename
        if color.startswith('#'):
            color_name = f"hex_{color[1:]}"
        else:
            color_name = color
        output_filename = f"{name}_bg_{color_name}{ext}"
        output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
        
        # Apply new background color to the clean transparent image
        change_background(temp_no_bg_path, output_path, rgb_color)
        
        # Clean up temporary file
        try:
            os.remove(temp_no_bg_path)
        except:
            pass  # Ignore cleanup errors
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'message': f'Background changed to {color}',
            'processing_steps': ['Background removed', f'{color} background applied'],
            'preview_url': url_for('static', filename='processed/' + output_filename)
        }), 200
        
    except Exception as e:
        # Clean up temporary file in case of error
        try:
            if 'temp_no_bg_path' in locals():
                os.remove(temp_no_bg_path)
        except:
            pass
        
        return jsonify({
            'error': 'Background change failed',
            'message': str(e)
        }), 500

@process_bp.route('/enhance/<filename>', methods=['POST'])
@limiter.limit("5 per minute")
def enhance(filename):
    """Enhance image quality"""
    data = request.get_json() or {}
    
    # Extract enhancement parameters
    enhancement_params = {
        'contrast': data.get('contrast', 0),
        'brightness': data.get('brightness', 0),
        'sharpness': data.get('sharpness', 0),
        'saturation': data.get('saturation', 0),
        'hue': data.get('hue', 0),
        'noise': data.get('noise', 0),
        'blur': data.get('blur', 0),
        'highlight': data.get('highlight', 0),
        'shadow': data.get('shadow', 0),
        'temperature': data.get('temperature', 0),
        'tint': data.get('tint', 0)
    }
    
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
    try:
        # Generate output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_enhanced{ext}"
        output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
        
        # Process image with enhancement parameters
        enhance_image(input_path, output_path, enhancement_params)
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'message': 'Image enhanced successfully',
            'applied_enhancements': {k: v for k, v in enhancement_params.items() if v != 0},
            'preview_url': url_for('static', filename='processed/' + output_filename)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Image enhancement failed',
            'message': str(e)
        }), 500

@process_bp.route('/resize/<filename>', methods=['POST'])
@limiter.limit("5 per minute")
def resize(filename):
    """Resize image to passport dimensions or custom size"""
    data = request.get_json() or {}
    
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
    # Check if custom width/height are provided
    width = data.get('width')
    height = data.get('height')
    
    if width and height:
        # Custom resize mode
        try:
            width = int(width)
            height = int(height)
            
            if width <= 0 or height <= 0:
                return jsonify({'error': 'Width and height must be positive integers'}), 400
                
            if width > 10000 or height > 10000:
                return jsonify({'error': 'Maximum dimension is 10000 pixels'}), 400
            
            # Generate output filename
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_resized_{width}x{height}{ext}"
            output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
            
            # Import custom resize function
            from app.services.photo_resizer import custom_resize
            
            # Process image with custom dimensions
            custom_resize(input_path, output_path, width, height, maintain_aspect=True)
            
            return jsonify({
                'success': True,
                'output_filename': output_filename,
                'message': f'Image resized to {width}x{height} pixels',
                'dimensions': {'width': width, 'height': height},
                'preview_url': url_for('static', filename='processed/' + output_filename)
            }), 200
            
        except ValueError:
            return jsonify({'error': 'Width and height must be valid integers'}), 400
        except Exception as e:
            return jsonify({
                'error': 'Custom resize failed',
                'message': str(e)
            }), 500
    else:
        # Passport resize mode (original functionality)
        country = data.get('country', 'US')
        
        if country not in current_app.config['PASSPORT_SIZES']:
            return jsonify({
                'error': 'Invalid country',
                'available_countries': list(current_app.config['PASSPORT_SIZES'].keys())
            }), 400
        
        try:
            # Generate output filename
            name, ext = os.path.splitext(filename)
            output_filename = f"{name}_passport_{country.lower()}{ext}"
            output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
            
            # Process image
            dimensions = current_app.config['PASSPORT_SIZES'][country]
            resize_to_passport(input_path, output_path, dimensions)
            
            return jsonify({
                'success': True,
                'output_filename': output_filename,
                'message': f'Image resized to {country} passport standards',
                'dimensions': dimensions,
                'preview_url': url_for('static', filename='processed/' + output_filename)
            }), 200
            
        except Exception as e:
            return jsonify({
                'error': 'Image resize failed',
                'message': str(e)
            }), 500

@process_bp.route('/quick_passport/<filename>', methods=['POST'])
@limiter.limit("3 per minute")
def quick_passport(filename):
    """Quick passport photo processing (remove background + resize)"""
    data = request.get_json() or {}
    country = data.get('country', 'US')
    
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
    try:
        # Step 1: Remove background
        name, ext = os.path.splitext(filename)
        temp_filename = f"{name}_temp_bg_removed{ext}"
        temp_path = os.path.join(current_app.config['PROCESSED_FOLDER'], temp_filename)
        
        remove_background(input_path, temp_path, current_app.config['REMBG_MODEL'])
        
        # Step 2: Change background to white
        temp2_filename = f"{name}_temp_white_bg{ext}"
        temp2_path = os.path.join(current_app.config['PROCESSED_FOLDER'], temp2_filename)
        
        white_color = current_app.config['BACKGROUND_COLORS']['white']
        change_background(temp_path, temp2_path, white_color)
        
        # Step 3: Resize to passport dimensions
        output_filename = f"{name}_passport_photo{ext}"
        output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
        
        dimensions = current_app.config['PASSPORT_SIZES'][country]
        resize_to_passport(temp2_path, output_path, dimensions)
        
        # Clean up temp files
        try:
            os.remove(temp_path)
            os.remove(temp2_path)
        except:
            pass
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'message': 'Quick passport photo created successfully',
            'processing_steps': ['Background removed', 'White background applied', f'Resized to {country} standards'],
            'preview_url': url_for('static', filename='processed/' + output_filename)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Quick passport processing failed',
            'message': str(e)
        }), 500

@process_bp.route('/professional/<filename>', methods=['POST'])
@limiter.limit("2 per minute")
def professional(filename):
    """Professional processing package (all enhancements)"""
    data = request.get_json() or {}
    country = data.get('country', 'US')
    color = data.get('color', 'white')
    
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
    try:
        name, ext = os.path.splitext(filename)
        
        # Step 1: Enhance image quality
        temp1_filename = f"{name}_temp_enhanced{ext}"
        temp1_path = os.path.join(current_app.config['PROCESSED_FOLDER'], temp1_filename)
        enhance_image(input_path, temp1_path)
        
        # Step 2: Remove background
        temp2_filename = f"{name}_temp_no_bg{ext}"
        temp2_path = os.path.join(current_app.config['PROCESSED_FOLDER'], temp2_filename)
        remove_background(temp1_path, temp2_path, current_app.config['REMBG_MODEL'])
        
        # Step 3: Change background
        temp3_filename = f"{name}_temp_new_bg{ext}"
        temp3_path = os.path.join(current_app.config['PROCESSED_FOLDER'], temp3_filename)
        rgb_color = current_app.config['BACKGROUND_COLORS'][color]
        change_background(temp2_path, temp3_path, rgb_color)
        
        # Step 4: Resize to passport
        output_filename = f"{name}_professional_passport{ext}"
        output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
        dimensions = current_app.config['PASSPORT_SIZES'][country]
        resize_to_passport(temp3_path, output_path, dimensions)
        
        # Clean up temp files
        for temp_file in [temp1_path, temp2_path, temp3_path]:
            try:
                os.remove(temp_file)
            except:
                pass
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'message': 'Professional processing completed successfully',
            'processing_steps': ['Enhanced quality', 'Background removed', f'{color.title()} background applied', f'Resized to {country} standards'],
            'preview_url': url_for('static', filename='processed/' + output_filename)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Professional processing failed',
            'message': str(e)
        }), 500
