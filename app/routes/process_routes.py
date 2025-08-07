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
from ..services.bg_changer import change_background
from ..services.enhancer import enhance_image
from ..services.photo_resizer import resize_to_passport
from ..services.utils import allowed_file, save_uploaded_file

process_bp = Blueprint('process', __name__)

# Initialize limiter for processing routes
limiter = Limiter(key_func=get_remote_address)

@process_bp.route('/upload', methods=['POST'])
@limiter.limit("10 per minute")
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
    """Change background color"""
    data = request.get_json() or {}
    
    color = data.get('color', 'white')
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
    if color not in current_app.config['BACKGROUND_COLORS']:
        return jsonify({
            'error': 'Invalid color',
            'available_colors': list(current_app.config['BACKGROUND_COLORS'].keys())
        }), 400
    
    try:
        # Generate output filename
        name, ext = os.path.splitext(filename)
        output_filename = f"{name}_bg_{color}{ext}"
        output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
        
        # Process image
        rgb_color = current_app.config['BACKGROUND_COLORS'][color]
        change_background(input_path, output_path, rgb_color)
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'message': f'Background changed to {color}',
            'preview_url': url_for('static', filename='processed/' + output_filename)
        }), 200
        
    except Exception as e:
        return jsonify({
            'error': 'Background change failed',
            'message': str(e)
        }), 500

@process_bp.route('/enhance/<filename>', methods=['POST'])
@limiter.limit("5 per minute")
def enhance(filename):
    """Enhance image quality"""
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
        output_filename = f"{name}_enhanced{ext}"
        output_path = os.path.join(current_app.config['PROCESSED_FOLDER'], output_filename)
        
        # Process image
        enhance_image(input_path, output_path)
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'message': 'Image enhanced successfully',
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
    """Resize image to passport dimensions"""
    data = request.get_json() or {}
    
    country = data.get('country', 'US')
    # Check both upload and processed folders
    input_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        input_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if not os.path.exists(input_path):
            return jsonify({'error': 'File not found'}), 404
    
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
