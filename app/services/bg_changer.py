"""
Background color/image change service using Pillow and OpenCV
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance
import logging

logger = logging.getLogger(__name__)

def change_background(input_path: str, output_path: str, bg_color: tuple):
    """
    Change image background to a solid color
    
    Args:
        input_path (str): Path to input image (should have transparent background)
        output_path (str): Path to save output image
        bg_color (tuple): RGB color tuple (r, g, b)
    
    Returns:
        bool: True if successful
    """
    try:
        # Validate input
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Open image with PIL
        image = Image.open(input_path)
        
        # Convert to RGBA if not already
        if image.mode != 'RGBA':
            image = image.convert('RGBA')
        
        # Create background with specified color
        background = Image.new('RGBA', image.size, bg_color + (255,))
        
        # Composite the images
        result = Image.alpha_composite(background, image)
        
        # Convert to RGB for final output
        result = result.convert('RGB')
        
        # Save result
        result.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"Background changed to {bg_color}: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error changing background: {str(e)}")
        raise e

def change_background_with_image(input_path: str, output_path: str, bg_image_path: str):
    """
    Change background to another image
    
    Args:
        input_path (str): Path to input image (with transparent background)
        output_path (str): Path to save output
        bg_image_path (str): Path to background image
    
    Returns:
        bool: True if successful
    """
    try:
        # Validate inputs
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if not os.path.exists(bg_image_path):
            raise FileNotFoundError(f"Background file not found: {bg_image_path}")
        
        # Open images
        foreground = Image.open(input_path).convert('RGBA')
        background = Image.open(bg_image_path).convert('RGB')
        
        # Resize background to match foreground
        background = background.resize(foreground.size, Image.LANCZOS)
        background = background.convert('RGBA')
        
        # Composite images
        result = Image.alpha_composite(background, foreground)
        result = result.convert('RGB')
        
        # Save result
        result.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"Background changed with image: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error changing background with image: {str(e)}")
        raise e

def remove_and_change_background(input_path: str, output_path: str, bg_color: tuple):
    """
    Remove background and add new color in one step using OpenCV
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output
        bg_color (tuple): RGB color tuple
    
    Returns:
        bool: True if successful
    """
    try:
        # Read image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not read image: {input_path}")
        
        # Convert BGR to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Create a simple background removal using color thresholding
        # This is a basic implementation - for better results, use the AI model first
        
        # Convert to HSV for better color separation
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # Define range for background color (assuming light background)
        lower_bg = np.array([0, 0, 200])
        upper_bg = np.array([180, 30, 255])
        
        # Create mask
        mask = cv2.inRange(hsv, lower_bg, upper_bg)
        mask_inv = cv2.bitwise_not(mask)
        
        # Create background with specified color
        bg_bgr = (bg_color[2], bg_color[1], bg_color[0])  # RGB to BGR
        background = np.full_like(img, bg_bgr, dtype=np.uint8)
        
        # Apply masks
        foreground = cv2.bitwise_and(img, img, mask=mask_inv)
        background = cv2.bitwise_and(background, background, mask=mask)
        
        # Combine foreground and background
        result = cv2.add(foreground, background)
        
        # Save result
        cv2.imwrite(output_path, result)
        
        logger.info(f"Background removed and changed: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in remove and change background: {str(e)}")
        raise e

def apply_gradient_background(input_path: str, output_path: str, color1: tuple, color2: tuple):
    """
    Apply gradient background
    
    Args:
        input_path (str): Path to input image (with transparent background)
        output_path (str): Path to save output
        color1 (tuple): Start color RGB
        color2 (tuple): End color RGB
    
    Returns:
        bool: True if successful
    """
    try:
        # Open foreground image
        foreground = Image.open(input_path).convert('RGBA')
        width, height = foreground.size
        
        # Create gradient background
        gradient = Image.new('RGB', (width, height))
        
        for y in range(height):
            # Calculate gradient ratio
            ratio = y / height
            
            # Interpolate colors
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            
            # Draw horizontal line
            for x in range(width):
                gradient.putpixel((x, y), (r, g, b))
        
        # Convert gradient to RGBA
        gradient = gradient.convert('RGBA')
        
        # Composite images
        result = Image.alpha_composite(gradient, foreground)
        result = result.convert('RGB')
        
        # Save result
        result.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"Gradient background applied: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error applying gradient background: {str(e)}")
        raise e
