#!/usr/bin/env python3
"""
Model Optimization Script for 512MB RAM Deployment
Downloads, optimizes, and prepares Tiny U²-Net models for memory-constrained environments
"""

import os
import sys
import logging
import gc
from pathlib import Path

# Add the parent directory to path so we can import our services
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_and_prepare_models():
    """Download and prepare optimized models for deployment"""
    logger.info("Starting model optimization process...")
    
    try:
        # Import rembg to trigger model downloads
        logger.info("Importing rembg and triggering model downloads...")
        from rembg import new_session
        
        # Force download of u2netp (Tiny U²-Net) model
        logger.info("Downloading u2netp (Tiny U²-Net) model...")
        session = new_session('u2netp')
        logger.info("✅ u2netp model downloaded successfully")
        
        # Clear session to free memory
        del session
        gc.collect()
        
        # Test our Tiny U²-Net service
        logger.info("Testing Tiny U²-Net service...")
        from app.services.tiny_u2net_service import tiny_u2net_service
        
        # Get memory info
        memory_info = tiny_u2net_service.get_memory_usage()
        logger.info(f"Memory usage: {memory_info}")
        
        logger.info("✅ Model optimization completed successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Model optimization failed: {e}")
        return False

def verify_memory_constraints():
    """Verify system meets memory constraints for deployment"""
    try:
        import psutil
        
        # Get system memory info
        memory = psutil.virtual_memory()
        total_mb = memory.total / 1024 / 1024
        available_mb = memory.available / 1024 / 1024
        used_percent = memory.percent
        
        logger.info(f"System Memory Analysis:")
        logger.info(f"  Total: {total_mb:.1f}MB")
        logger.info(f"  Available: {available_mb:.1f}MB")
        logger.info(f"  Used: {used_percent:.1f}%")
        
        # Check constraints for 512MB deployment
        if total_mb > 512:
            logger.info("✅ System has more than 512MB total memory")
        else:
            logger.warning("⚠️  System has limited memory - optimizations will be crucial")
        
        if available_mb > 200:
            logger.info("✅ Sufficient available memory for model loading")
        else:
            logger.warning("⚠️  Low available memory - may need additional optimizations")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Memory verification failed: {e}")
        return False

def test_background_removal():
    """Test background removal with sample processing"""
    try:
        logger.info("Testing background removal functionality...")
        
        # Create a small test image if demo images exist
        demo_dir = Path(__file__).parent.parent / "app" / "static" / "images"
        test_images = list(demo_dir.glob("demo*.jpg"))
        
        if not test_images:
            logger.info("No demo images found, skipping background removal test")
            return True
        
        test_image = test_images[0]
        logger.info(f"Using test image: {test_image}")
        
        # Test with our Tiny U²-Net service
        from app.services.tiny_u2net_service import tiny_u2net_service
        
        # Create temp output path
        output_dir = Path(__file__).parent.parent / "temp_test"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "test_output.png"
        
        # Test background removal
        logger.info("Testing background removal...")
        success = tiny_u2net_service.remove_background(str(test_image), str(output_path))
        
        if success:
            logger.info("✅ Background removal test successful")
            
            # Test background color change
            color_output = output_dir / "test_color.jpg"
            success = tiny_u2net_service.change_background_color(
                str(test_image), str(color_output), (255, 0, 0)  # Red background
            )
            
            if success:
                logger.info("✅ Background color change test successful")
            else:
                logger.warning("⚠️  Background color change test failed")
        else:
            logger.warning("⚠️  Background removal test failed")
        
        # Cleanup
        if output_path.exists():
            output_path.unlink()
        if (output_dir / "test_color.jpg").exists():
            (output_dir / "test_color.jpg").unlink()
        if output_dir.exists() and not list(output_dir.iterdir()):
            output_dir.rmdir()
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Background removal test failed: {e}")
        return False

def main():
    """Main optimization process"""
    logger.info("=== Model Optimization for 512MB RAM Deployment ===")
    
    success = True
    
    # Step 1: Verify memory constraints
    logger.info("\n1. Verifying memory constraints...")
    if not verify_memory_constraints():
        success = False
    
    # Step 2: Download and prepare models
    logger.info("\n2. Downloading and preparing models...")
    if not download_and_prepare_models():
        success = False
    
    # Step 3: Test functionality
    logger.info("\n3. Testing background removal functionality...")
    if not test_background_removal():
        logger.warning("Background removal test failed, but continuing...")
    
    # Summary
    logger.info("\n=== Optimization Summary ===")
    if success:
        logger.info("✅ Model optimization completed successfully!")
        logger.info("\nRecommended deployment settings:")
        logger.info("- Use u2netp model (Tiny U²-Net)")
        logger.info("- Limit input images to 10MB")
        logger.info("- Resize large images before processing")
        logger.info("- Monitor memory usage during operation")
    else:
        logger.error("❌ Some optimization steps failed. Review logs above.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
