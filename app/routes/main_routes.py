"""
Main page routes for PixPort
"""

from flask import Blueprint, render_template, jsonify, request, current_app
import os

main_bp = Blueprint('main', __name__)

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
    return render_template('preview.html', filename=filename)

@main_bp.route('/result/<filename>')
def result(filename):
    """Show processing result"""
    return render_template('result.html', filename=filename)

# API Routes
@main_bp.route('/api/image-info/<filename>')
def image_info(filename):
    """Get image information"""
    try:
        from PIL import Image
        import time
        
        # Check in both upload and processed folders
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        
        image_path = None
        if os.path.exists(processed_path):
            image_path = processed_path
        elif os.path.exists(upload_path):
            image_path = upload_path
        else:
            return jsonify({'error': 'Image not found'}), 404
        
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
            'filename': filename,
            'width': width,
            'height': height,
            'format': format,
            'mode': mode,
            'file_size': file_size,
            'dpi': int(dpi) if dpi else 300,
            'color_space': 'sRGB',  # Assume sRGB for web images
            'modified': modified_time
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to get image info',
            'message': str(e)
        }), 500

@main_bp.route('/api/download/<filename>')
def download_image(filename):
    """Download processed image with format/quality options"""
    try:
        from flask import send_file, request
        from PIL import Image
        import io
        
        # Get query parameters
        format = request.args.get('format', 'JPEG').upper()
        quality = int(request.args.get('quality', 95))
        
        # Check if file exists in processed folder
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        
        if not os.path.exists(processed_path):
            return jsonify({'error': 'File not found'}), 404
        
        # If no conversion needed, send file directly
        if format == 'PDF':
            # Convert to PDF
            with Image.open(processed_path) as img:
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                pdf_buffer = io.BytesIO()
                img.save(pdf_buffer, format='PDF', quality=95)
                pdf_buffer.seek(0)
                
                return send_file(
                    pdf_buffer,
                    as_attachment=True,
                    download_name=f"passport_photo.pdf",
                    mimetype='application/pdf'
                )
        else:
            # Handle image formats
            with Image.open(processed_path) as img:
                # Convert mode if necessary
                if format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                elif format == 'PNG' and img.mode not in ('RGBA', 'RGB', 'P', 'L'):
                    img = img.convert('RGBA')
                
                # Save to buffer
                img_buffer = io.BytesIO()
                save_kwargs = {'format': format}
                
                if format in ('JPEG', 'WEBP'):
                    save_kwargs['quality'] = quality
                    save_kwargs['optimize'] = True
                
                img.save(img_buffer, **save_kwargs)
                img_buffer.seek(0)
                
                # Determine MIME type
                mime_types = {
                    'JPEG': 'image/jpeg',
                    'PNG': 'image/png',
                    'WEBP': 'image/webp'
                }
                
                return send_file(
                    img_buffer,
                    as_attachment=True,
                    download_name=f"passport_photo.{format.lower()}",
                    mimetype=mime_types.get(format, 'image/jpeg')
                )
                
    except Exception as e:
        return jsonify({
            'error': 'Download failed',
            'message': str(e)
        }), 500

@main_bp.route('/api/comparison/<filename>')
def comparison_images(filename):
    """Get original and processed image for comparison"""
    try:
        # Try to find the original filename by removing processing suffixes
        original_filename = filename
        suffixes = ['_no_bg', '_bg_white', '_bg_light_blue', '_bg_light_gray', '_bg_cream', 
                   '_enhanced', '_passport_us', '_passport_uk', '_passport_photo', 
                   '_professional_passport']
        
        for suffix in suffixes:
            if suffix in original_filename:
                original_filename = original_filename.replace(suffix, '', 1)
                break
        
        return jsonify({
            'success': True,
            'original_filename': original_filename,
            'processed_filename': filename
        })
        
    except Exception as e:
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
        # Check if file exists in upload folder
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        
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
            'filename': filename,
            'file_size': file_size,
            'exists': True
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to check upload status',
            'message': str(e)
        }), 500
