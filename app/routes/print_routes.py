"""
Print Layout Sheet Generator Routes
Creates print-ready sheets with multiple passport photo copies
"""

from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from PIL import Image, ImageDraw
import os
import uuid
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch
from ..routes.main_routes import sanitize_filename

print_bp = Blueprint('print', __name__)

# Print sheet configurations (dimensions in pixels at 300 DPI)
SHEET_CONFIGS = {
    'A4': {
        'width': 2480,    # 8.27 inches * 300 DPI
        'height': 3508,   # 11.69 inches * 300 DPI
        'name': 'A4 (8.3×11.7 inch)'
    },
    'LETTER': {
        'width': 2550,    # 8.5 inches * 300 DPI
        'height': 3300,   # 11 inches * 300 DPI
        'name': 'Letter (8.5×11 inch)'
    },
    '4x6': {
        'width': 1800,    # 6 inches * 300 DPI
        'height': 1200,   # 4 inches * 300 DPI
        'name': '4×6 inch'
    },
    '5x7': {
        'width': 2100,    # 7 inches * 300 DPI
        'height': 1500,   # 5 inches * 300 DPI
        'name': '5×7 inch'
    }
}

# Passport photo sizes (width, height in pixels at 300 DPI)
PHOTO_SIZES = {
    'US': (413, 531),        # 2×2 inches
    'EU': (413, 531),        # 35×45mm
    'UK': (413, 531),        # 35×45mm
    'INDIA': (413, 413),     # 35×35mm (square)
    'CHINA': (390, 567),     # 33×48mm
}

@print_bp.route('/print-layout/<filename>')
def print_layout_page(filename):
    """Display the print layout generator page"""
    # Sanitize filename
    sanitized_filename = sanitize_filename(filename)
    if not sanitized_filename:
        return "Invalid filename", 400
    
    # Check if processed file exists
    processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
    if not os.path.exists(processed_path):
        return "File not found", 404
    
    return render_template('print_layout.html', 
                         filename=sanitized_filename,
                         sheet_configs=SHEET_CONFIGS,
                         photo_sizes=PHOTO_SIZES)

@print_bp.route('/api/generate-print-sheet', methods=['POST'])
def generate_print_sheet():
    """Generate a print sheet with multiple photo copies"""
    try:
        data = request.get_json()
        
        # Validate input
        filename = data.get('filename')
        sheet_type = data.get('sheet_type', 'A4')
        num_photos = int(data.get('num_photos', 4))
        photo_size = data.get('photo_size', 'US')
        margin_size = data.get('margin_size', 'normal')
        add_cut_guides = data.get('add_cut_guides', True)
        
        # Sanitize filename
        sanitized_filename = sanitize_filename(filename)
        if not sanitized_filename:
            return jsonify({'success': False, 'error': 'Invalid filename'}), 400
        
        # Check if source file exists
        source_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'error': 'Source file not found'}), 404
        
        # Generate print sheet
        sheet_filename = create_print_sheet(
            source_path, 
            sanitized_filename,
            sheet_type, 
            num_photos, 
            photo_size, 
            margin_size, 
            add_cut_guides
        )
        
        return jsonify({
            'success': True,
            'sheet_filename': sheet_filename,
            'download_url': f'/static/processed/{sheet_filename}'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating print sheet: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Failed to generate print sheet',
            'message': str(e)
        }), 500

def create_print_sheet(source_path, original_filename, sheet_type, num_photos, photo_size, margin_size, add_cut_guides, output_format='PNG'):
    """Create a print sheet with multiple photo copies"""
    
    # Get sheet dimensions
    sheet_config = SHEET_CONFIGS.get(sheet_type, SHEET_CONFIGS['A4'])
    sheet_width = sheet_config['width']
    sheet_height = sheet_config['height']
    
    # Get photo dimensions
    photo_width, photo_height = PHOTO_SIZES.get(photo_size, PHOTO_SIZES['US'])
    
    # Calculate margins
    margin_configs = {
        'small': 30,      # ~0.1 inch
        'normal': 60,     # ~0.2 inch  
        'large': 90       # ~0.3 inch
    }
    margin = margin_configs.get(margin_size, 60)
    
    # Calculate how many photos can fit
    available_width = sheet_width - (2 * margin)
    available_height = sheet_height - (2 * margin)
    
    # Calculate grid layout
    cols = min(num_photos, available_width // photo_width)
    rows = (num_photos + cols - 1) // cols  # Ceiling division
    
    # Adjust if doesn't fit vertically
    if rows * photo_height > available_height:
        rows = available_height // photo_height
        cols = min(available_width // photo_width, num_photos)
    
    actual_photos = min(num_photos, rows * cols)
    
    # Calculate spacing for center alignment
    if cols > 0:
        h_spacing = (available_width - (cols * photo_width)) // max(1, cols - 1) if cols > 1 else 0
        total_width = (cols * photo_width) + ((cols - 1) * h_spacing)
        start_x = margin + (available_width - total_width) // 2
    else:
        h_spacing = 0
        start_x = margin
    
    if rows > 0:
        v_spacing = (available_height - (rows * photo_height)) // max(1, rows - 1) if rows > 1 else 0
        total_height = (rows * photo_height) + ((rows - 1) * v_spacing)
        start_y = margin + (available_height - total_height) // 2
    else:
        v_spacing = 0
        start_y = margin
    
    # Create sheet image
    sheet = Image.new('RGB', (sheet_width, sheet_height), 'white')
    
    # Load and resize source image
    with Image.open(source_path) as source_img:
        # Convert to RGB if necessary
        if source_img.mode != 'RGB':
            source_img = source_img.convert('RGB')
        
        # Resize to passport photo size
        photo_img = source_img.resize((photo_width, photo_height), Image.Resampling.LANCZOS)
        
        # Place photos on sheet
        photo_count = 0
        for row in range(rows):
            for col in range(cols):
                if photo_count >= actual_photos:
                    break
                
                x = start_x + col * (photo_width + h_spacing)
                y = start_y + row * (photo_height + v_spacing)
                
                sheet.paste(photo_img, (x, y))
                photo_count += 1
            
            if photo_count >= actual_photos:
                break
    
    # Add cutting guides if requested
    if add_cut_guides:
        draw = ImageDraw.Draw(sheet)
        
        # Draw cutting lines around each photo
        for row in range(rows):
            for col in range(cols):
                if row * cols + col >= actual_photos:
                    break
                
                x = start_x + col * (photo_width + h_spacing)
                y = start_y + row * (photo_height + v_spacing)
                
                # Draw corner marks (small lines at corners)
                mark_length = 20
                mark_color = '#999999'
                line_width = 1
                
                # Top-left corner
                draw.line([(x-mark_length, y), (x, y)], fill=mark_color, width=line_width)
                draw.line([(x, y-mark_length), (x, y)], fill=mark_color, width=line_width)
                
                # Top-right corner
                draw.line([(x+photo_width, y), (x+photo_width+mark_length, y)], fill=mark_color, width=line_width)
                draw.line([(x+photo_width, y-mark_length), (x+photo_width, y)], fill=mark_color, width=line_width)
                
                # Bottom-left corner
                draw.line([(x-mark_length, y+photo_height), (x, y+photo_height)], fill=mark_color, width=line_width)
                draw.line([(x, y+photo_height), (x, y+photo_height+mark_length)], fill=mark_color, width=line_width)
                
                # Bottom-right corner
                draw.line([(x+photo_width, y+photo_height), (x+photo_width+mark_length, y+photo_height)], fill=mark_color, width=line_width)
                draw.line([(x+photo_width, y+photo_height), (x+photo_width, y+photo_height+mark_length)], fill=mark_color, width=line_width)
    
    # Save the sheet in requested format
    base_name = original_filename.rsplit('.', 1)[0]
    file_extension = output_format.lower() if output_format != 'JPEG' else 'jpg'
    sheet_filename = f"{base_name}_print_sheet_{sheet_type}_{actual_photos}copies_{uuid.uuid4().hex[:8]}.{file_extension}"
    sheet_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sheet_filename)
    
    # Save with appropriate format and quality
    if output_format.upper() == 'PDF':
        return create_pdf_sheet(sheet, sheet_filename, sheet_config, sheet_type)
    elif output_format.upper() == 'JPEG':
        # Convert to RGB for JPEG (no transparency)
        if sheet.mode in ('RGBA', 'LA', 'P'):
            rgb_sheet = Image.new('RGB', sheet.size, (255, 255, 255))
            rgb_sheet.paste(sheet, mask=sheet.split()[-1] if sheet.mode == 'RGBA' else None)
            sheet = rgb_sheet
        sheet.save(sheet_path, 'JPEG', quality=95, dpi=(300, 300), optimize=True)
    else:  # PNG
        sheet.save(sheet_path, 'PNG', quality=95, dpi=(300, 300), optimize=True)
    
    return sheet_filename

def create_pdf_sheet(sheet_image, sheet_filename, sheet_config, sheet_type):
    """Create PDF version of the print sheet"""
    sheet_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sheet_filename)
    
    # Convert PIL Image to bytes
    img_buffer = io.BytesIO()
    sheet_image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    # Create PDF
    if sheet_type == 'A4':
        page_size = A4
    elif sheet_type == 'LETTER':
        page_size = letter
    else:
        # For other sizes, use custom dimensions
        page_size = (sheet_config['width'] * 72 / 300, sheet_config['height'] * 72 / 300)  # Convert to points
    
    c = canvas.Canvas(sheet_path, pagesize=page_size)
    
    # Calculate image dimensions in points (72 points = 1 inch)
    img_width = sheet_config['width'] * 72 / 300
    img_height = sheet_config['height'] * 72 / 300
    
    # Save image temporarily to add to PDF
    temp_img_path = sheet_path.replace('.pdf', '_temp.png')
    sheet_image.save(temp_img_path, 'PNG')
    
    # Add image to PDF
    c.drawImage(temp_img_path, 0, 0, width=img_width, height=img_height)
    c.save()
    
    # Clean up temp image
    if os.path.exists(temp_img_path):
        os.remove(temp_img_path)
    
    return sheet_filename

@print_bp.route('/api/print-preview', methods=['POST'])
def print_preview():
    """Generate a preview of the print layout"""
    try:
        data = request.get_json()
        
        filename = data.get('filename')
        sheet_type = data.get('sheet_type', 'A4')
        num_photos = int(data.get('num_photos', 4))
        photo_size = data.get('photo_size', 'US')
        margin_size = data.get('margin_size', 'normal')
        
        # Calculate layout information
        sheet_config = SHEET_CONFIGS.get(sheet_type, SHEET_CONFIGS['A4'])
        photo_width, photo_height = PHOTO_SIZES.get(photo_size, PHOTO_SIZES['US'])
        
        margin_configs = {'small': 30, 'normal': 60, 'large': 90}
        margin = margin_configs.get(margin_size, 60)
        
        available_width = sheet_config['width'] - (2 * margin)
        available_height = sheet_config['height'] - (2 * margin)
        
        cols = min(num_photos, available_width // photo_width)
        rows = (num_photos + cols - 1) // cols
        
        if rows * photo_height > available_height:
            rows = available_height // photo_height
            cols = min(available_width // photo_width, num_photos)
        
        actual_photos = min(num_photos, rows * cols)
        
        return jsonify({
            'success': True,
            'preview': {
                'sheet_type': sheet_type,
                'sheet_name': sheet_config['name'],
                'photo_size': photo_size,
                'requested_photos': num_photos,
                'actual_photos': actual_photos,
                'layout': f"{cols} × {rows}",
                'photo_dimensions': f"{photo_width}×{photo_height}px",
                'sheet_dimensions': f"{sheet_config['width']}×{sheet_config['height']}px"
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': 'Failed to generate preview',
            'message': str(e)
        }), 500

@print_bp.route('/api/download-print-sheet', methods=['POST'])
def download_print_sheet():
    """Download print sheet in specified format"""
    try:
        data = request.get_json()
        
        # Validate input
        filename = data.get('filename')
        sheet_type = data.get('sheet_type', 'A4')
        num_photos = int(data.get('num_photos', 4))
        photo_size = data.get('photo_size', 'US')
        margin_size = data.get('margin_size', 'normal')
        add_cut_guides = data.get('add_cut_guides', True)
        output_format = data.get('format', 'PNG').upper()
        
        # Validate format
        if output_format not in ['PNG', 'JPEG', 'PDF']:
            return jsonify({'success': False, 'error': 'Invalid format'}), 400
        
        # Sanitize filename
        sanitized_filename = sanitize_filename(filename)
        if not sanitized_filename:
            return jsonify({'success': False, 'error': 'Invalid filename'}), 400
        
        # Check if source file exists
        source_path = os.path.join(current_app.config['PROCESSED_FOLDER'], sanitized_filename)
        if not os.path.exists(source_path):
            return jsonify({'success': False, 'error': 'Source file not found'}), 404
        
        # Generate print sheet in requested format
        sheet_filename = create_print_sheet(
            source_path, 
            sanitized_filename,
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
        
    except Exception as e:
        current_app.logger.error(f"Error downloading print sheet: {str(e)}")
        return jsonify({
            'success': False, 
            'error': 'Failed to download print sheet',
            'message': str(e)
        }), 500
