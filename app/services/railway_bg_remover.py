"""
Railway-optimized background removal service
NO MODEL LOADING ON WORKER STARTUP to prevent OOM crashes
"""

import os
import gc
import logging

logger = logging.getLogger(__name__)

def remove_background_railway(input_path: str, output_path: str) -> bool:
    """
    Remove background using u2netp model - Railway ultra-optimized
    Creates and disposes session only when processing, NOT on startup
    """
    session = None
    input_data = None
    output_data = None
    
    try:
        # Validate input
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        # Check file size (8MB max for Railway)
        file_size = os.path.getsize(input_path)
        if file_size > 8 * 1024 * 1024:
            raise ValueError(f"File too large: {file_size} bytes. Max 8MB for Railway.")
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        logger.info(f"Railway: Processing {input_path} ({file_size} bytes)")
        
        # CRITICAL: Force garbage collection before loading model
        gc.collect()
        
        # Import and create session only when needed (not during worker startup)
        logger.info("Railway: Creating disposable u2netp session")
        from rembg import new_session, remove
        session = new_session('u2netp')
        
        # Read input
        with open(input_path, 'rb') as f:
            input_data = f.read()
        
        # Process
        logger.info("Railway: Removing background")
        output_data = remove(input_data, session=session)
        
        # Save output
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        logger.info(f"Railway: Background removal completed: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Railway background removal failed: {e}")
        return False
        
    finally:
        # CRITICAL: Aggressive cleanup for Railway memory constraints
        if session is not None:
            try:
                if hasattr(session, 'clear'):
                    session.clear()
                elif hasattr(session, 'close'):
                    session.close()
                del session
                logger.debug("Railway: Disposed u2netp session")
            except Exception as cleanup_error:
                logger.warning(f"Railway session cleanup error: {cleanup_error}")
        
        # Clean up data
        if input_data is not None:
            del input_data
        if output_data is not None:
            del output_data
        
        # Force double garbage collection
        gc.collect()
        gc.collect()
        
        logger.debug("Railway: Memory cleanup completed")


def is_railway_environment() -> bool:
    """Check if running in Railway environment"""
    return os.environ.get('RAILWAY_ENVIRONMENT_NAME') is not None
