"""
Image enhancement functions
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging

logger = logging.getLogger(__name__)

def enhance_image(input_path: str, output_path: str):
    """
    Enhance image quality with multiple techniques
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save enhanced image
    
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
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply enhancements
        enhanced_image = image.copy()
        
        # 1. Adjust brightness (slight increase)
        brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
        enhanced_image = brightness_enhancer.enhance(1.1)
        
        # 2. Adjust contrast (moderate increase)
        contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
        enhanced_image = contrast_enhancer.enhance(1.2)
        
        # 3. Adjust color saturation (slight increase)
        color_enhancer = ImageEnhance.Color(enhanced_image)
        enhanced_image = color_enhancer.enhance(1.1)
        
        # 4. Adjust sharpness (moderate increase)
        sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
        enhanced_image = sharpness_enhancer.enhance(1.3)
        
        # 5. Apply unsharp mask for better detail
        enhanced_image = apply_unsharp_mask(enhanced_image)
        
        # Save enhanced image
        enhanced_image.save(output_path, 'JPEG', quality=95, optimize=True)
        
        logger.info(f"Image enhanced successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        raise e

def apply_unsharp_mask(image: Image.Image, radius: float = 2.0, percent: float = 150, threshold: int = 3):
    """
    Apply unsharp mask filter for better sharpness
    
    Args:
        image (PIL.Image): Input image
        radius (float): Blur radius
        percent (float): Sharpening strength
        threshold (int): Minimum difference threshold
    
    Returns:
        PIL.Image: Sharpened image
    """
    try:
        # Create blurred version
        blurred = image.filter(ImageFilter.GaussianBlur(radius=radius))
        
        # Convert to numpy arrays
        original = np.array(image, dtype=np.float32)
        blur = np.array(blurred, dtype=np.float32)
        
        # Calculate difference
        difference = original - blur
        
        # Apply threshold
        mask = np.abs(difference) >= threshold
        difference = difference * mask
        
        # Apply sharpening
        sharpened = original + (difference * percent / 100.0)
        
        # Clip values to valid range
        sharpened = np.clip(sharpened, 0, 255).astype(np.uint8)
        
        return Image.fromarray(sharpened)
        
    except Exception as e:
        logger.error(f"Error applying unsharp mask: {str(e)}")
        return image

def enhance_with_opencv(input_path: str, output_path: str):
    """
    Enhance image using OpenCV techniques
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save enhanced image
    
    Returns:
        bool: True if successful
    """
    try:
        # Read image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not read image: {input_path}")
        
        # Convert to different color spaces for processing
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        l_channel_clahe = clahe.apply(l_channel)
        
        # Merge channels back
        lab_enhanced = cv2.merge([l_channel_clahe, a_channel, b_channel])
        img_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2BGR)
        
        # Apply bilateral filter for noise reduction while preserving edges
        img_enhanced = cv2.bilateralFilter(img_enhanced, 9, 75, 75)
        
        # Apply gamma correction for better brightness
        gamma = 1.2
        lookup_table = np.array([((i / 255.0) ** (1.0 / gamma)) * 255
                               for i in np.arange(0, 256)]).astype("uint8")
        img_enhanced = cv2.LUT(img_enhanced, lookup_table)
        
        # Save result
        cv2.imwrite(output_path, img_enhanced, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        logger.info(f"Image enhanced with OpenCV: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error enhancing with OpenCV: {str(e)}")
        raise e

def denoise_image(input_path: str, output_path: str):
    """
    Remove noise from image
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save denoised image
    
    Returns:
        bool: True if successful
    """
    try:
        # Read image
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not read image: {input_path}")
        
        # Apply different denoising techniques based on image characteristics
        
        # Non-local Means Denoising for color images
        denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        
        # Save result
        cv2.imwrite(output_path, denoised, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        logger.info(f"Image denoised: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error denoising image: {str(e)}")
        raise e

def adjust_lighting(input_path: str, output_path: str, brightness: float = 1.0, contrast: float = 1.0):
    """
    Adjust image lighting (brightness and contrast)
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save adjusted image
        brightness (float): Brightness factor (1.0 = no change)
        contrast (float): Contrast factor (1.0 = no change)
    
    Returns:
        bool: True if successful
    """
    try:
        # Open image with PIL
        image = Image.open(input_path)
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Adjust brightness
        if brightness != 1.0:
            brightness_enhancer = ImageEnhance.Brightness(image)
            image = brightness_enhancer.enhance(brightness)
        
        # Adjust contrast
        if contrast != 1.0:
            contrast_enhancer = ImageEnhance.Contrast(image)
            image = contrast_enhancer.enhance(contrast)
        
        # Save result
        image.save(output_path, 'JPEG', quality=95)
        
        logger.info(f"Lighting adjusted (brightness: {brightness}, contrast: {contrast}): {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error adjusting lighting: {str(e)}")
        raise e

def auto_enhance(input_path: str, output_path: str):
    """
    Automatically enhance image based on analysis
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save enhanced image
    
    Returns:
        bool: True if successful
    """
    try:
        # Read image for analysis
        img = cv2.imread(input_path)
        if img is None:
            raise ValueError(f"Could not read image: {input_path}")
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Calculate image statistics
        mean_brightness = np.mean(gray)
        std_brightness = np.std(gray)
        
        # Determine enhancement parameters based on analysis
        if mean_brightness < 100:  # Dark image
            brightness_factor = 1.3
            contrast_factor = 1.2
        elif mean_brightness > 180:  # Bright image
            brightness_factor = 0.9
            contrast_factor = 1.1
        else:  # Normal brightness
            brightness_factor = 1.1
            contrast_factor = 1.15
        
        # Adjust contrast based on standard deviation
        if std_brightness < 30:  # Low contrast
            contrast_factor *= 1.3
        elif std_brightness > 80:  # High contrast
            contrast_factor *= 0.9
        
        # Apply automatic enhancement
        adjust_lighting(input_path, output_path, brightness_factor, contrast_factor)
        
        logger.info(f"Auto-enhanced image (brightness: {brightness_factor:.2f}, contrast: {contrast_factor:.2f}): {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in auto enhancement: {str(e)}")
        raise e
