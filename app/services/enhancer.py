"""
Image enhancement functions
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import logging

logger = logging.getLogger(__name__)

def enhance_image(input_path: str, output_path: str, enhancement_params: dict = None):
    """
    Enhance image quality with multiple techniques and proper memory management
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save enhanced image
        enhancement_params (dict): Parameters for enhancement adjustments
    
    Returns:
        bool: True if successful
    """
    image = None
    enhanced_image = None
    temp_images = []
    
    try:
        # Validate input
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Check file size
        file_size = os.path.getsize(input_path)
        if file_size > 20 * 1024 * 1024:  # 20MB limit
            raise ValueError(f"Input file too large: {file_size} bytes. Maximum 20MB allowed.")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Open image with PIL
        image = Image.open(input_path)
        
        # Check image dimensions
        width, height = image.size
        if width * height > 50_000_000:  # ~50MP limit
            raise ValueError(f"Image too large: {width}x{height} pixels. Please resize first.")
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            rgb_image = image.convert('RGB')
            image.close()
            image = rgb_image
        
        # Apply enhancements
        enhanced_image = image.copy()
        
        # Get enhancement parameters or use defaults
        params = enhancement_params or {}
        
        # Calculate enhancement factors from slider values (-50 to +50 or 0 to 100)
        brightness_factor = 1.0 + (params.get('brightness', 0) / 100.0)  # -50 to +50 -> 0.5 to 1.5
        contrast_factor = 1.0 + (params.get('contrast', 0) / 100.0)      # -50 to +50 -> 0.5 to 1.5
        saturation_factor = 1.0 + (params.get('saturation', 0) / 100.0)  # -50 to +50 -> 0.5 to 1.5
        sharpness_factor = 1.0 + (params.get('sharpness', 0) / 100.0)    # 0 to 100 -> 1.0 to 2.0
        
        # Apply default enhancements if no parameters provided
        if not params or all(v == 0 for v in params.values()):
            brightness_factor = 1.1
            contrast_factor = 1.2
            saturation_factor = 1.1
            sharpness_factor = 1.3
        
        # 1. Adjust brightness
        if brightness_factor != 1.0:
            brightness_enhancer = ImageEnhance.Brightness(enhanced_image)
            temp_image = brightness_enhancer.enhance(max(0.1, min(2.0, brightness_factor)))
            enhanced_image.close()
            enhanced_image = temp_image
        
        # 2. Adjust contrast
        if contrast_factor != 1.0:
            contrast_enhancer = ImageEnhance.Contrast(enhanced_image)
            temp_image = contrast_enhancer.enhance(max(0.1, min(2.0, contrast_factor)))
            enhanced_image.close()
            enhanced_image = temp_image
        
        # 3. Adjust color saturation
        if saturation_factor != 1.0:
            color_enhancer = ImageEnhance.Color(enhanced_image)
            temp_image = color_enhancer.enhance(max(0.1, min(2.0, saturation_factor)))
            enhanced_image.close()
            enhanced_image = temp_image
        
        # 4. Adjust sharpness
        if sharpness_factor != 1.0:
            sharpness_enhancer = ImageEnhance.Sharpness(enhanced_image)
            temp_image = sharpness_enhancer.enhance(max(0.1, min(3.0, sharpness_factor)))
            enhanced_image.close()
            enhanced_image = temp_image
        
        # 5. Apply hue adjustment if specified
        hue_shift = params.get('hue', 0)
        if hue_shift != 0:
            temp_image = apply_hue_shift(enhanced_image, hue_shift)
            if temp_image != enhanced_image:
                enhanced_image.close()
                enhanced_image = temp_image
        
        # 6. Apply noise reduction if specified
        noise_reduction = params.get('noise', 0)
        if noise_reduction > 0:
            temp_image = apply_noise_reduction(enhanced_image, noise_reduction)
            if temp_image != enhanced_image:
                enhanced_image.close()
                enhanced_image = temp_image
        
        # 7. Apply blur if specified
        blur_amount = params.get('blur', 0)
        if blur_amount > 0:
            temp_image = enhanced_image.filter(ImageFilter.GaussianBlur(radius=blur_amount / 10.0))
            enhanced_image.close()
            enhanced_image = temp_image
        
        # 8. Apply unsharp mask for better detail
        temp_image = apply_unsharp_mask(enhanced_image)
        if temp_image != enhanced_image:
            enhanced_image.close()
            enhanced_image = temp_image
        
        # Save enhanced image
        enhanced_image.save(output_path, 'JPEG', quality=95, optimize=True)
        
        logger.info(f"Image enhanced successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error enhancing image: {str(e)}")
        raise e
    finally:
        # Cleanup all image objects
        if image is not None:
            try:
                image.close()
                del image
            except:
                pass
        
        if enhanced_image is not None:
            try:
                enhanced_image.close()
                del enhanced_image
            except:
                pass
        
        # Cleanup any temp images
        for temp_img in temp_images:
            try:
                temp_img.close()
                del temp_img
            except:
                pass
        
        # Force garbage collection
        import gc
        gc.collect()

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

def apply_hue_shift(image: Image.Image, hue_shift: float):
    """
    Apply hue shift to image
    
    Args:
        image (PIL.Image): Input image
        hue_shift (float): Hue shift in degrees (-180 to 180)
    
    Returns:
        PIL.Image: Hue-shifted image
    """
    try:
        # Convert to HSV
        hsv_image = image.convert('HSV')
        h, s, v = hsv_image.split()
        
        # Convert hue channel to numpy array
        h_array = np.array(h, dtype=np.float32)
        
        # Apply hue shift (normalize to 0-360 range)
        h_array = (h_array / 255.0 * 360.0 + hue_shift) % 360.0
        
        # Convert back to 0-255 range
        h_array = (h_array / 360.0 * 255.0).astype(np.uint8)
        
        # Create new HSV image
        h_shifted = Image.fromarray(h_array, mode='L')
        hsv_shifted = Image.merge('HSV', (h_shifted, s, v))
        
        # Convert back to RGB
        return hsv_shifted.convert('RGB')
        
    except Exception as e:
        logger.error(f"Error applying hue shift: {str(e)}")
        return image

def apply_noise_reduction(image: Image.Image, noise_level: float):
    """
    Apply noise reduction to image
    
    Args:
        image (PIL.Image): Input image
        noise_level (float): Noise reduction level (0-100)
    
    Returns:
        PIL.Image: Noise-reduced image
    """
    try:
        # Convert PIL to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Apply bilateral filter for noise reduction
        # Adjust filter strength based on noise level
        filter_strength = int(noise_level / 10.0)  # 0-10 range
        filtered = cv2.bilateralFilter(cv_image, 9, filter_strength * 10, filter_strength * 10)
        
        # Convert back to PIL format
        filtered_rgb = cv2.cvtColor(filtered, cv2.COLOR_BGR2RGB)
        return Image.fromarray(filtered_rgb)
        
    except Exception as e:
        logger.error(f"Error applying noise reduction: {str(e)}")
        return image
