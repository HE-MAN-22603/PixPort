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

def railway_background_change(input_path: str, output_path: str, bg_color: tuple) -> bool:
    """
    Remove background and change color using Railway-optimized isnet-general-use in one step
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output
        bg_color (tuple): RGB color tuple
    
    Returns:
        bool: True if successful
    """
    try:
        logger.info(f"Using Railway-optimized isnet for background change to {bg_color}")
        
        # Import the Railway background remover service
        from .railway_bg_remover import railway_bg_remover
        
        # Use the integrated background removal and color change
        return railway_bg_remover.change_background_color(input_path, output_path, bg_color)
        
    except Exception as e:
        logger.error(f"Error in Railway background change: {e}")
        return False

def tiny_u2net_background_change(input_path: str, output_path: str, bg_color: tuple) -> bool:
    """
    Remove background and change color using Tiny U²-Net in one optimized step
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output
        bg_color (tuple): RGB color tuple
    
    Returns:
        bool: True if successful
    """
    try:
        logger.info(f"Using Tiny U²-Net for background change to {bg_color}")
        
        # Import the Tiny U²-Net service
        from .tiny_u2net_service import tiny_u2net_service
        
        # Use the integrated background removal and color change
        return tiny_u2net_service.change_background_color(input_path, output_path, bg_color)
        
    except Exception as e:
        logger.error(f"Error in Tiny U²-Net background change: {e}")
        return False

def smart_background_change(input_path: str, output_path: str, bg_color: tuple):
    """
    Intelligently change background color - works on both original images and transparent background images
    Priority: Railway-optimized -> Tiny U²-Net -> OpenCV methods
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output
        bg_color (tuple): RGB color tuple
    
    Returns:
        bool: True if successful
    """
    try:
        is_railway = os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None
        
        # Priority 1: Railway-optimized background change (isnet-general-use)
        if is_railway:
            if railway_background_change(input_path, output_path, bg_color):
                logger.info("✅ Railway-optimized background change succeeded")
                return True
        
        # Priority 2: Tiny U²-Net (for local or Railway fallback)
        if tiny_u2net_background_change(input_path, output_path, bg_color):
            logger.info("✅ Tiny U²-Net background change succeeded")
            return True
        
        logger.warning("Tiny U²-Net failed, falling back to smart method")
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Open image with PIL
        image = Image.open(input_path)
        
        # Check if image has transparency (alpha channel)
        has_transparency = image.mode in ('RGBA', 'LA') or 'transparency' in image.info
        
        if has_transparency and image.mode == 'RGBA':
            # Image already has transparent background, just change it
            logger.info("Image has transparent background, applying new background color")
            
            # Create background with specified color
            background = Image.new('RGBA', image.size, bg_color + (255,))
            
            # Composite the images
            result = Image.alpha_composite(background, image)
            
        else:
            # Image doesn't have transparent background, need to remove it first
            logger.info("Image has solid background, removing and applying new color")
            
            # Convert image to numpy array for OpenCV processing
            img = cv2.imread(input_path)
            if img is None:
                raise ValueError(f"Could not read image: {input_path}")
            
            # Convert to HSV for better background detection
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Try to detect background automatically
            # Check corners to estimate background color
            h, w = img.shape[:2]
            corner_pixels = [
                hsv[0, 0],           # top-left
                hsv[0, w-1],         # top-right
                hsv[h-1, 0],         # bottom-left
                hsv[h-1, w-1],       # bottom-right
            ]
            
            # Use the most common corner color as background reference
            avg_corner = np.mean(corner_pixels, axis=0).astype(np.uint8)
            
            # Create more flexible background mask
            # Expand the range based on the detected background color
            tolerance = 30
            lower_bg = np.array([
                max(0, int(avg_corner[0]) - tolerance),
                max(0, int(avg_corner[1]) - tolerance//2),
                max(0, int(avg_corner[2]) - tolerance)
            ], dtype=np.uint8)
            upper_bg = np.array([
                min(179, int(avg_corner[0]) + tolerance),
                min(255, int(avg_corner[1]) + tolerance//2),
                min(255, int(avg_corner[2]) + tolerance)
            ], dtype=np.uint8)
            
            # Create mask for background removal
            mask = cv2.inRange(hsv, lower_bg, upper_bg)
            
            # Apply some morphological operations to clean up the mask
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            # Invert mask (we want to keep the foreground)
            mask_inv = cv2.bitwise_not(mask)
            
            # Create new background with specified color
            bg_bgr = (bg_color[2], bg_color[1], bg_color[0])  # RGB to BGR
            background = np.full_like(img, bg_bgr, dtype=np.uint8)
            
            # Apply masks
            foreground = cv2.bitwise_and(img, img, mask=mask_inv)
            background = cv2.bitwise_and(background, background, mask=mask)
            
            # Combine foreground and background
            result_cv = cv2.add(foreground, background)
            
            # Convert back to PIL for consistency
            result_rgb = cv2.cvtColor(result_cv, cv2.COLOR_BGR2RGB)
            result = Image.fromarray(result_rgb)
        
        # Convert to RGB for final output (remove alpha if present)
        if result.mode != 'RGB':
            result = result.convert('RGB')
        
        # Save result
        result.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"Smart background change completed: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in smart background change: {str(e)}")
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
