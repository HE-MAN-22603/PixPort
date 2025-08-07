"""
Utility functions for PixPort services
"""

import os
import uuid
import mimetypes
from PIL import Image, ExifTags
from werkzeug.utils import secure_filename
import logging

logger = logging.getLogger(__name__)

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """
    Check if file extension is allowed
    
    Args:
        filename (str): Name of the file
        allowed_extensions (set): Set of allowed file extensions
    
    Returns:
        bool: True if file is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def save_uploaded_file(file, filename: str, upload_folder: str) -> str:
    """
    Save uploaded file to the upload folder
    
    Args:
        file: Flask file object
        filename (str): Filename to save as
        upload_folder (str): Directory to save file
    
    Returns:
        str: Full path to saved file
    """
    try:
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Auto-rotate image based on EXIF data
        filepath = auto_rotate_image(filepath)
        
        logger.info(f"File saved: {filepath}")
        return filepath
        
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        raise e

def auto_rotate_image(filepath: str) -> str:
    """
    Auto-rotate image based on EXIF orientation data
    
    Args:
        filepath (str): Path to image file
    
    Returns:
        str: Path to corrected image (same as input)
    """
    try:
        with Image.open(filepath) as img:
            # Check for EXIF orientation data
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif is not None:
                    for tag, value in exif.items():
                        if tag in ExifTags.TAGS:
                            if ExifTags.TAGS[tag] == 'Orientation':
                                if value == 2:
                                    img = img.transpose(Image.FLIP_LEFT_RIGHT)
                                elif value == 3:
                                    img = img.rotate(180, expand=True)
                                elif value == 4:
                                    img = img.transpose(Image.FLIP_TOP_BOTTOM)
                                elif value == 5:
                                    img = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(90, expand=True)
                                elif value == 6:
                                    img = img.rotate(270, expand=True)
                                elif value == 7:
                                    img = img.transpose(Image.FLIP_LEFT_RIGHT).rotate(270, expand=True)
                                elif value == 8:
                                    img = img.rotate(90, expand=True)
                                
                                # Save corrected image
                                img.save(filepath, quality=95, optimize=True)
                                logger.info(f"Image auto-rotated: {filepath}")
                                break
        
        return filepath
        
    except Exception as e:
        logger.error(f"Error auto-rotating image: {str(e)}")
        return filepath

def generate_unique_filename(original_filename: str) -> str:
    """
    Generate a unique filename while preserving the extension
    
    Args:
        original_filename (str): Original filename
    
    Returns:
        str: Unique filename
    """
    name, ext = os.path.splitext(secure_filename(original_filename))
    unique_id = str(uuid.uuid4())[:8]
    return f"{unique_id}_{name}{ext}"

def get_image_info(filepath: str) -> dict:
    """
    Get basic information about an image file
    
    Args:
        filepath (str): Path to image file
    
    Returns:
        dict: Image information
    """
    try:
        with Image.open(filepath) as img:
            info = {
                'filename': os.path.basename(filepath),
                'format': img.format,
                'mode': img.mode,
                'size': img.size,
                'width': img.size[0],
                'height': img.size[1],
                'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info
            }
            
            # Get file size
            info['file_size'] = os.path.getsize(filepath)
            
            # Get MIME type
            info['mime_type'] = mimetypes.guess_type(filepath)[0]
            
            return info
            
    except Exception as e:
        logger.error(f"Error getting image info: {str(e)}")
        return {}

def validate_image_file(filepath: str) -> tuple:
    """
    Validate if file is a valid image
    
    Args:
        filepath (str): Path to image file
    
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    try:
        if not os.path.exists(filepath):
            return False, "File does not exist"
        
        # Check file size (max 16MB)
        file_size = os.path.getsize(filepath)
        if file_size > 16 * 1024 * 1024:
            return False, "File too large (max 16MB)"
        
        # Try to open with PIL
        with Image.open(filepath) as img:
            # Verify the image
            img.verify()
            
            # Check minimum dimensions (passport photos need reasonable size)
            if img.size[0] < 100 or img.size[1] < 100:
                return False, "Image too small (minimum 100x100 pixels)"
            
            # Check maximum dimensions
            if img.size[0] > 5000 or img.size[1] > 5000:
                return False, "Image too large (maximum 5000x5000 pixels)"
        
        return True, "Valid image"
        
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"

def clean_old_files(directory: str, max_age_hours: int = 24):
    """
    Clean up old files from a directory
    
    Args:
        directory (str): Directory to clean
        max_age_hours (int): Maximum age of files in hours
    """
    try:
        import time
        
        if not os.path.exists(directory):
            return
        
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(directory):
            filepath = os.path.join(directory, filename)
            
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getctime(filepath)
                
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                        logger.info(f"Deleted old file: {filepath}")
                    except Exception as e:
                        logger.error(f"Error deleting file {filepath}: {str(e)}")
    
    except Exception as e:
        logger.error(f"Error cleaning old files: {str(e)}")

def convert_heic_to_jpg(input_path: str, output_path: str) -> bool:
    """
    Convert HEIC file to JPG (requires pillow-heif)
    
    Args:
        input_path (str): Path to HEIC file
        output_path (str): Path to save JPG file
    
    Returns:
        bool: True if successful
    """
    try:
        # This would require pillow-heif package
        # For now, we'll use PIL's basic support
        
        with Image.open(input_path) as img:
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Save as JPEG
            img.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"HEIC converted to JPG: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error converting HEIC: {str(e)}")
        return False

def create_thumbnail(input_path: str, output_path: str, size: tuple = (150, 150)) -> bool:
    """
    Create thumbnail of image
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save thumbnail
        size (tuple): Thumbnail dimensions
    
    Returns:
        bool: True if successful
    """
    try:
        with Image.open(input_path) as img:
            # Create thumbnail
            img.thumbnail(size, Image.LANCZOS)
            
            # Save thumbnail
            img.save(output_path, 'JPEG', quality=85)
        
        logger.info(f"Thumbnail created: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating thumbnail: {str(e)}")
        return False

def get_dominant_colors(image_path: str, num_colors: int = 5) -> list:
    """
    Get dominant colors from an image
    
    Args:
        image_path (str): Path to image
        num_colors (int): Number of dominant colors to return
    
    Returns:
        list: List of RGB tuples
    """
    try:
        from collections import Counter
        
        with Image.open(image_path) as img:
            # Resize for faster processing
            img = img.resize((100, 100))
            
            # Convert to RGB
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Get all pixels
            pixels = list(img.getdata())
            
            # Count color frequencies
            color_counts = Counter(pixels)
            
            # Get most common colors
            dominant_colors = color_counts.most_common(num_colors)
            
            return [color[0] for color in dominant_colors]
    
    except Exception as e:
        logger.error(f"Error getting dominant colors: {str(e)}")
        return []
