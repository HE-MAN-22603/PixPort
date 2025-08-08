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
    Remove background from image using AI models with proper memory management
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output image
        model_name (str): Model to use ('u2net', 'u2netp', 'silueta')
    
    Returns:
        bool: True if successful, False otherwise
    """
    session = None
    input_image = None
    output_image = None
    
    try:
        # Validate input file exists
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create rembg session
        logger.info(f"Creating rembg session with model: {model_name}")
        session = new_session(model_name)
        
        # Open and process image with size limit check
        file_size = os.path.getsize(input_path)
        if file_size > 20 * 1024 * 1024:  # 20MB limit for processing
            raise ValueError(f"Input file too large: {file_size} bytes. Maximum 20MB allowed.")
        
        with open(input_path, 'rb') as input_file:
            input_image = input_file.read()
        
        # Remove background
        logger.info(f"Processing image: {input_path} ({file_size} bytes)")
        output_image = remove(input_image, session=session)
        
        # Save result
        with open(output_path, 'wb') as output_file:
            output_file.write(output_image)
        
        logger.info(f"Background removed successfully: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error removing background: {str(e)}")
        raise e
    finally:
        # Explicit cleanup to free memory
        if session is not None:
            try:
                # Clear session if possible
                if hasattr(session, 'clear'):
                    session.clear()
                elif hasattr(session, 'close'):
                    session.close()
                del session
            except Exception as cleanup_error:
                logger.warning(f"Error during session cleanup: {cleanup_error}")
        
        # Clear image data from memory
        if input_image is not None:
            del input_image
        if output_image is not None:
            del output_image
        
        # Force garbage collection
        import gc
        gc.collect()

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
        
        # Create session and remove background
        session = new_session(model_name)
        
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
        # Explicit cleanup to free memory
        if session is not None:
            try:
                if hasattr(session, 'clear'):
                    session.clear()
                elif hasattr(session, 'close'):
                    session.close()
                del session
            except Exception as cleanup_error:
                logger.warning(f"Error during session cleanup: {cleanup_error}")
        
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
