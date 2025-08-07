"""
Background removal service using rembg and U²-Net
"""

import os
from rembg import new_session, remove
from PIL import Image
import logging

logger = logging.getLogger(__name__)

def remove_background(input_path: str, output_path: str, model_name: str = 'u2net'):
    """
    Remove background from image using AI models
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
        model_name (str): Model to use ('u2net', 'u2netp', 'silueta')
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create rembg session
        logger.info(f"Creating rembg session with model: {model_name}")
        session = new_session(model_name)
        
        # Open and process image
        with open(input_path, 'rb') as input_file:
            input_image = input_file.read()
        
        # Remove background
        logger.info(f"Processing image: {input_path}")
        output_image = remove(input_image, session=session)
        
        # Save result
        with open(output_path, 'wb') as output_file:
            output_file.write(output_image)
        
        logger.info(f"Background removed successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing background: {str(e)}")
        raise e

def remove_background_pil(input_path: str, output_path: str, model_name: str = 'u2net'):
    """
    Remove background using PIL for better control
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
        model_name (str): Model to use
    
    Returns:
        bool: True if successful
    """
    try:
        # Open image with PIL
        input_image = Image.open(input_path)
        
        # Convert to RGB if necessary
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        
        # Create session and remove background
        session = new_session(model_name)
        
        # Convert PIL image to bytes for rembg
        import io
        img_byte_arr = io.BytesIO()
        input_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Remove background
        output_bytes = remove(img_byte_arr, session=session)
        
        # Convert back to PIL and save
        output_image = Image.open(io.BytesIO(output_bytes))
        output_image.save(output_path, format='PNG')
        
        logger.info(f"Background removed with PIL: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error in PIL background removal: {str(e)}")
        raise e

def get_available_models():
    """Get list of available rembg models"""
    return ['u2net', 'u2netp', 'u2net_human_seg', 'silueta', 'isnet-general-use']
