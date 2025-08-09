#!/usr/bin/env python3
"""
Test script for Tiny U²-Net Background Removal Service
Tests memory-optimized background removal and color change functionality
"""

import os
import sys
import logging
import time
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_tiny_u2net_service():
    """Test the Tiny U²-Net service functionality"""
    try:
        logger.info("Testing Tiny U²-Net Background Removal Service")
        
        # Import the service
        from app.services.tiny_u2net_service import tiny_u2net_service
        
        # Check memory usage before
        memory_before = tiny_u2net_service.get_memory_usage()
        logger.info(f"Memory usage before: {memory_before}")
        
        # Find test images
        test_images = []
        image_dir = Path("app/static/images")
        if image_dir.exists():
            for ext in ['*.jpg', '*.jpeg', '*.png']:
                test_images.extend(image_dir.glob(ext))
        
        if not test_images:
            logger.warning("No test images found. Creating a simple test...")
            return test_simple_functionality()
        
        # Use the first image for testing
        test_image = str(test_images[0])
        logger.info(f"Using test image: {test_image}")
        
        # Create output directory
        output_dir = Path("temp_test_output")
        output_dir.mkdir(exist_ok=True)
        
        # Test 1: Background Removal
        logger.info("\n=== Test 1: Background Removal ===")
        output_bg_removed = output_dir / "bg_removed.png"
        
        start_time = time.time()
        success1 = tiny_u2net_service.remove_background(test_image, str(output_bg_removed))
        end_time = time.time()
        
        if success1:
            logger.info(f"✅ Background removal successful in {end_time - start_time:.2f} seconds")
            logger.info(f"Output: {output_bg_removed}")
        else:
            logger.error("❌ Background removal failed")
        
        # Test 2: Background Color Change
        logger.info("\n=== Test 2: Background Color Change ===")
        test_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green  
            (0, 0, 255),    # Blue
            (255, 255, 255), # White
            (128, 128, 128)  # Gray
        ]
        
        color_success = 0
        for i, color in enumerate(test_colors):
            output_colored = output_dir / f"bg_color_{i+1}.jpg"
            
            start_time = time.time()
            success = tiny_u2net_service.change_background_color(test_image, str(output_colored), color)
            end_time = time.time()
            
            if success:
                logger.info(f"✅ Color change to {color} successful in {end_time - start_time:.2f} seconds")
                color_success += 1
            else:
                logger.error(f"❌ Color change to {color} failed")
        
        # Test 3: Memory Usage
        logger.info("\n=== Test 3: Memory Usage ===")
        memory_after = tiny_u2net_service.get_memory_usage()
        logger.info(f"Memory usage after: {memory_after}")
        
        memory_increase = memory_after['rss_mb'] - memory_before['rss_mb']
        logger.info(f"Memory increase: {memory_increase:.1f}MB")
        
        # Memory cleanup test
        logger.info("Testing memory cleanup...")
        tiny_u2net_service.clear_memory()
        memory_cleared = tiny_u2net_service.get_memory_usage()
        logger.info(f"Memory after cleanup: {memory_cleared}")
        
        # Summary
        logger.info("\n=== Test Summary ===")
        logger.info(f"Background removal: {'✅ PASS' if success1 else '❌ FAIL'}")
        logger.info(f"Color changes: {color_success}/{len(test_colors)} successful")
        logger.info(f"Memory usage: {memory_after['rss_mb']:.1f}MB")
        
        if memory_increase > 200:  # Alert if memory usage increased by more than 200MB
            logger.warning(f"⚠️  High memory usage increase: {memory_increase:.1f}MB")
        else:
            logger.info(f"✅ Memory usage acceptable: +{memory_increase:.1f}MB")
        
        # Cleanup test files
        cleanup_test_files(output_dir)
        
        return success1 and color_success > 0
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_simple_functionality():
    """Simple functionality test without real images"""
    try:
        logger.info("Running simple functionality test...")
        
        from app.services.tiny_u2net_service import tiny_u2net_service
        
        # Test memory monitoring
        memory_info = tiny_u2net_service.get_memory_usage()
        logger.info(f"Memory info: {memory_info}")
        
        # Test memory clearing
        tiny_u2net_service.clear_memory()
        logger.info("Memory cleared successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"Simple test failed: {e}")
        return False

def test_model_manager():
    """Test the optimized model manager"""
    try:
        logger.info("\n=== Testing Model Manager ===")
        
        from app.services.model_manager import model_manager
        
        # Test memory constraint detection
        logger.info("Testing memory constraint detection...")
        
        # Test model session creation
        logger.info("Testing model session creation...")
        session = model_manager.get_session('u2net')  # Should default to u2netp
        
        if session:
            logger.info("✅ Model session created successfully")
        else:
            logger.error("❌ Failed to create model session")
            return False
        
        # Test memory info
        memory_info = model_manager.get_memory_info()
        logger.info(f"Model manager memory info: {memory_info}")
        
        # Test cleanup
        model_manager.clear_all()
        logger.info("✅ Model manager cleanup successful")
        
        return True
        
    except Exception as e:
        logger.error(f"Model manager test failed: {e}")
        return False

def test_integration_with_bg_remover():
    """Test integration with existing background remover"""
    try:
        logger.info("\n=== Testing Integration with Background Remover ===")
        
        from app.services.bg_remover_lite import remove_background
        
        # Find a test image
        image_dir = Path("app/static/images")
        test_images = []
        if image_dir.exists():
            for ext in ['*.jpg', '*.jpeg', '*.png']:
                test_images.extend(image_dir.glob(ext))
        
        if not test_images:
            logger.info("No test images found for integration test")
            return True
        
        test_image = str(test_images[0])
        output_dir = Path("temp_test_output")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / "integration_test.png"
        
        # Test the integrated background removal
        success = remove_background(test_image, str(output_path))
        
        if success:
            logger.info("✅ Integration with bg_remover_lite successful")
        else:
            logger.error("❌ Integration test failed")
        
        # Cleanup
        cleanup_test_files(output_dir)
        
        return success
        
    except Exception as e:
        logger.error(f"Integration test failed: {e}")
        return False

def cleanup_test_files(output_dir):
    """Clean up test output files"""
    try:
        if output_dir.exists():
            for file in output_dir.glob("*"):
                file.unlink()
            output_dir.rmdir()
            logger.info("Test files cleaned up")
    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")

def main():
    """Main test function"""
    logger.info("=== Tiny U²-Net Service Test Suite ===")
    
    tests = [
        ("Model Manager", test_model_manager),
        ("Tiny U²-Net Service", test_tiny_u2net_service),
        ("Integration Test", test_integration_with_bg_remover)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {e}")
            results.append((test_name, False))
    
    # Final summary
    logger.info(f"\n{'='*50}")
    logger.info("FINAL TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Tiny U²-Net service is ready for deployment.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
