"""
Resize images to passport specifications
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageDraw
import logging

logger = logging.getLogger(__name__)

def resize_to_passport(input_path: str, output_path: str, dimensions: tuple):
    """
    Resize image to passport dimensions while maintaining aspect ratio
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save resized image
        dimensions (tuple): Target dimensions (width, height) in pixels
    
    Returns:
        bool: True if successful
    """
    try:
        # Validate input
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Open image
        image = Image.open(input_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        target_width, target_height = dimensions
        original_width, original_height = image.size
        
        # Calculate aspect ratios
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height
        
        # Determine the best fit strategy
        if original_ratio > target_ratio:
            # Image is wider than target - fit by height
            new_height = target_height
            new_width = int(target_height * original_ratio)
        else:
            # Image is taller than target - fit by width
            new_width = target_width
            new_height = int(target_width / original_ratio)
        
        # Resize image maintaining aspect ratio
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        
        # Create passport-sized canvas with white background
        passport_image = Image.new('RGB', (target_width, target_height), 'white')
        
        # Calculate position to center the resized image
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # Paste resized image onto passport canvas
        passport_image.paste(resized_image, (x_offset, y_offset))
        
        # Save result
        passport_image.save(output_path, 'JPEG', quality=95, dpi=(300, 300))
        
        logger.info(f"Image resized to passport dimensions {dimensions}: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error resizing to passport: {str(e)}")
        raise e

def crop_to_passport(input_path: str, output_path: str, dimensions: tuple):
    """
    Crop image to exact passport dimensions
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save cropped image
        dimensions (tuple): Target dimensions (width, height)
    
    Returns:
        bool: True if successful
    """
    try:
        # Open image
        image = Image.open(input_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        target_width, target_height = dimensions
        original_width, original_height = image.size
        
        # Calculate aspect ratios
        target_ratio = target_width / target_height
        original_ratio = original_width / original_height
        
        # Determine crop dimensions
        if original_ratio > target_ratio:
            # Image is wider - crop width
            crop_height = original_height
            crop_width = int(original_height * target_ratio)
        else:
            # Image is taller - crop height
            crop_width = original_width
            crop_height = int(original_width / target_ratio)
        
        # Calculate crop coordinates (center crop)
        left = (original_width - crop_width) // 2
        top = (original_height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height
        
        # Crop image
        cropped_image = image.crop((left, top, right, bottom))
        
        # Resize to exact passport dimensions
        passport_image = cropped_image.resize((target_width, target_height), Image.LANCZOS)
        
        # Save result
        passport_image.save(output_path, 'JPEG', quality=95, dpi=(300, 300))
        
        logger.info(f"Image cropped to passport dimensions {dimensions}: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error cropping to passport: {str(e)}")
        raise e

def create_passport_grid(input_path: str, output_path: str, dimensions: tuple, grid_size: tuple = (2, 2)):
    """
    Create a grid of passport photos for printing
    
    Args:
        input_path (str): Path to input passport photo
        output_path (str): Path to save grid image
        dimensions (tuple): Single photo dimensions (width, height)
        grid_size (tuple): Grid layout (cols, rows)
    
    Returns:
        bool: True if successful
    """
    try:
        # Open passport photo
        passport_photo = Image.open(input_path)
        
        # Convert to RGB if necessary
        if passport_photo.mode != 'RGB':
            passport_photo = passport_photo.convert('RGB')
        
        # Ensure photo is correct size
        if passport_photo.size != dimensions:
            passport_photo = passport_photo.resize(dimensions, Image.LANCZOS)
        
        cols, rows = grid_size
        photo_width, photo_height = dimensions
        
        # Calculate grid dimensions with margins
        margin = 20  # 20 pixels margin between photos
        total_width = cols * photo_width + (cols + 1) * margin
        total_height = rows * photo_height + (rows + 1) * margin
        
        # Create grid canvas
        grid_image = Image.new('RGB', (total_width, total_height), 'white')
        
        # Place photos in grid
        for row in range(rows):
            for col in range(cols):
                x = margin + col * (photo_width + margin)
                y = margin + row * (photo_height + margin)
                grid_image.paste(passport_photo, (x, y))
        
        # Save grid
        grid_image.save(output_path, 'JPEG', quality=95, dpi=(300, 300))
        
        logger.info(f"Passport grid created ({grid_size}): {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error creating passport grid: {str(e)}")
        raise e

def add_passport_guidelines(input_path: str, output_path: str):
    """
    Add guidelines to help with passport photo composition
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save image with guidelines
    
    Returns:
        bool: True if successful
    """
    try:
        # Open image
        image = Image.open(input_path).convert('RGB')
        width, height = image.size
        
        # Create a copy for drawing
        guided_image = image.copy()
        draw = ImageDraw.Draw(guided_image)
        
        # Calculate guideline positions (based on passport photo standards)
        # Head should occupy 70-80% of photo height
        head_top = int(height * 0.1)  # 10% from top
        head_bottom = int(height * 0.8)  # 80% from top
        
        # Eyes should be at about 60-70% from bottom
        eye_line = int(height * 0.35)  # 35% from top
        
        # Center vertical line
        center_x = width // 2
        
        # Draw guidelines (thin red lines)
        line_color = (255, 0, 0, 128)  # Semi-transparent red
        line_width = 2
        
        # Horizontal guidelines
        draw.line([(0, head_top), (width, head_top)], fill=line_color, width=line_width)
        draw.line([(0, head_bottom), (width, head_bottom)], fill=line_color, width=line_width)
        draw.line([(0, eye_line), (width, eye_line)], fill=line_color, width=line_width)
        
        # Vertical center line
        draw.line([(center_x, 0), (center_x, height)], fill=line_color, width=line_width)
        
        # Face oval guide (approximate)
        face_width = int(width * 0.6)
        face_height = int(height * 0.6)
        face_left = (width - face_width) // 2
        face_top = int(height * 0.15)
        face_right = face_left + face_width
        face_bottom = face_top + face_height
        
        draw.ellipse([(face_left, face_top), (face_right, face_bottom)], 
                    outline=line_color, width=line_width)
        
        # Save guided image
        guided_image.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"Passport guidelines added: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error adding guidelines: {str(e)}")
        raise e

def detect_face_and_resize(input_path: str, output_path: str, dimensions: tuple):
    """
    Detect face in image and resize appropriately for passport photo
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save processed image
        dimensions (tuple): Target passport dimensions
    
    Returns:
        bool: True if successful
    """
    try:
        # Read image with OpenCV
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not read image: {input_path}")
        
        # Load face cascade classifier
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        if len(faces) == 0:
            logger.warning("No face detected, using standard resize")
            return resize_to_passport(input_path, output_path, dimensions)
        
        # Use the largest face detected
        largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
        x, y, w, h = largest_face
        
        # Calculate optimal crop area for passport photo
        # Face should be 70-80% of photo height
        target_width, target_height = dimensions
        target_face_height = int(target_height * 0.75)
        scale_factor = target_face_height / h
        
        # Calculate crop dimensions
        crop_width = int(target_width / scale_factor)
        crop_height = int(target_height / scale_factor)
        
        # Center crop around face
        face_center_x = x + w // 2
        face_center_y = y + h // 2
        
        crop_x1 = max(0, face_center_x - crop_width // 2)
        crop_y1 = max(0, face_center_y - int(crop_height * 0.3))  # Face should be in upper portion
        crop_x2 = min(img.shape[1], crop_x1 + crop_width)
        crop_y2 = min(img.shape[0], crop_y1 + crop_height)
        
        # Adjust if crop goes outside image bounds
        if crop_x2 - crop_x1 < crop_width:
            crop_x1 = max(0, crop_x2 - crop_width)
        if crop_y2 - crop_y1 < crop_height:
            crop_y1 = max(0, crop_y2 - crop_height)
        
        # Crop image
        cropped_img = img[crop_y1:crop_y2, crop_x1:crop_x2]
        
        # Convert back to PIL and resize
        cropped_pil = Image.fromarray(cv2.cvtColor(cropped_img, cv2.COLOR_BGR2RGB))
        passport_image = cropped_pil.resize(dimensions, Image.LANCZOS)
        
        # Save result
        passport_image.save(output_path, 'JPEG', quality=95, dpi=(300, 300))
        
        logger.info(f"Face-detected passport photo created: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in face detection resize: {str(e)}")
        # Fallback to standard resize
        return resize_to_passport(input_path, output_path, dimensions)
