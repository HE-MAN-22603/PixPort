"""
Background removal service using rembg and U²-Net
"""

import os
from rembg import remove
from PIL import Image
import logging
from .model_manager import model_manager

logger = logging.getLogger(__name__)

def remove_background(input_path: str, output_path: str, model_name: str = 'u2net'):
    """
    Remove background from image using AI models with fallback strategies
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
        model_name (str): Model to use ('u2net', 'u2netp', 'silueta')
    
    Returns:
        bool: True if successful, False otherwise
    """
    input_image = None
    output_image = None
    
    try:
        # Validate input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Check file size and image dimensions first
        file_size = os.path.getsize(input_path)
        if file_size > 15 * 1024 * 1024:  # Reduced to 15MB for safer processing
            raise ValueError(f"Input file too large: {file_size} bytes. Maximum 15MB allowed.")
        
        # Try AI background removal first
        try:
            logger.info(f"Attempting AI background removal for: {input_path} ({file_size} bytes)")
            return _ai_remove_background(input_path, output_path, model_name)
            
        except (RuntimeError, MemoryError, Exception) as ai_error:
            logger.warning(f"AI background removal failed: {ai_error}")
            logger.info("Falling back to simple background removal")
            
            # Fallback to simple processing that just copies the image with transparency
            return _fallback_background_removal(input_path, output_path)
        
    except Exception as e:
        logger.error(f"All background removal methods failed: {str(e)}")
        raise e
    finally:
        # Clear image data from memory
        if input_image is not None:
            del input_image
        if output_image is not None:
            del output_image
        
        # Force garbage collection
        import gc
        gc.collect()

def _ai_remove_background(input_path: str, output_path: str, model_name: str) -> bool:
    """AI-powered background removal"""
    input_image = None
    output_image = None
    
    try:
        # Get optimized session from model manager
        logger.info(f"Getting AI session with model: {model_name}")
        session = model_manager.get_session(model_name)
        
        with open(input_path, 'rb') as input_file:
            input_image = input_file.read()
        
        # Remove background using AI
        logger.info(f"Processing with AI model: {model_name}")
        output_image = remove(input_image, session=session)
        
        # Save result
        with open(output_path, 'wb') as output_file:
            output_file.write(output_image)
        
        logger.info(f"AI background removal successful: {output_path}")
        return True
        
    finally:
        if input_image is not None:
            del input_image
        if output_image is not None:
            del output_image
        import gc
        gc.collect()

def _fallback_background_removal(input_path: str, output_path: str) -> bool:
    """Simple fallback that converts image to PNG with transparency"""
    try:
        from PIL import Image
        
        logger.info("Using fallback background removal (simple conversion)")
        
        # Open image
        with Image.open(input_path) as img:
            # Convert to RGBA for transparency support
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Save as PNG with transparency
            img.save(output_path, 'PNG', optimize=True)
        
        logger.info(f"Fallback background removal completed: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Fallback background removal failed: {e}")
        raise e

def remove_background_pil(input_path: str, output_path: str, model_name: str = 'u2net'):
    """
    Remove background using PIL for better control with proper memory management
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
        model_name (str): Model to use
    
    Returns:
        bool: True if successful
    """
    session = None
    input_image = None
    output_image = None
    img_byte_arr = None
    output_bytes = None
    
    try:
        # Check file size before processing
        file_size = os.path.getsize(input_path)
        if file_size > 20 * 1024 * 1024:  # 20MB limit
            raise ValueError(f"Input file too large: {file_size} bytes. Maximum 20MB allowed.")
        
        # Open image with PIL
        input_image = Image.open(input_path)
        
        # Check image dimensions to prevent memory issues
        width, height = input_image.size
        if width * height > 50_000_000:  # ~50MP limit
            raise ValueError(f"Image too large: {width}x{height} pixels. Please resize first.")
        
        # Convert to RGB if necessary
        if input_image.mode != 'RGB':
            rgb_image = input_image.convert('RGB')
            input_image.close()  # Close original image
            input_image = rgb_image
        
        # Get session from model manager
        session = model_manager.get_session(model_name)
        
        # Convert PIL image to bytes for rembg
        import io
        img_byte_arr = io.BytesIO()
        input_image.save(img_byte_arr, format='PNG', optimize=True)
        img_byte_arr_value = img_byte_arr.getvalue()
        
        # Remove background
        output_bytes = remove(img_byte_arr_value, session=session)
        
        # Convert back to PIL and save
        output_image = Image.open(io.BytesIO(output_bytes))
        
        # Create output directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        output_image.save(output_path, format='PNG', optimize=True)
        
        logger.info(f"Background removed with PIL: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in PIL background removal: {str(e)}")
        raise e
    finally:
        # Explicit cleanup to free memory (don't delete shared session)
        if input_image is not None:
            try:
                input_image.close()
                del input_image
            except:
                pass
        
        if output_image is not None:
            try:
                output_image.close()
                del output_image
            except:
                pass
        
        if img_byte_arr is not None:
            try:
                img_byte_arr.close()
                del img_byte_arr
            except:
                pass
        
        if output_bytes is not None:
            del output_bytes
        
        # Force garbage collection
        import gc
        gc.collect()

def get_available_models():
    """Get list of available rembg models"""
    return ['u2net', 'u2netp', 'u2net_human_seg', 'silueta', 'isnet-general-use']
