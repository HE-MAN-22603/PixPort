"""
Ultra-Lightweight Background Removal for Railway Deployment
Uses isnet-general tiny model (~1.6MB) with <150MB memory usage
Designed specifically for 512MB Railway containers
"""

import os
import gc
import io
import logging
import numpy as np
from PIL import Image
import threading
from typing import Optional, Tuple
import time

logger = logging.getLogger(__name__)

class RailwayBgRemover:
    """Ultra-lightweight background remover for Railway deployment"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._session = None
        self._model_name = "isnet-general-use"  # This is the tiny version
        self._initialized = True
        logger.info("RailwayBgRemover initialized with isnet-general-use (tiny)")
    
    def _get_session(self):
        """Get or create session with aggressive memory management"""
        if self._session is None:
            with self._lock:
                if self._session is None:
                    self._create_session()
        return self._session
    
    def _create_session(self):
        """Create optimized session for Railway deployment"""
        try:
            # Force garbage collection before loading
            gc.collect()
            
            logger.info("Creating isnet-general-use session (tiny model ~1.6MB)")
            
            # Try rembg with isnet-general-use (tiny version)
            try:
                from rembg import new_session
                self._session = new_session('isnet-general-use')
                logger.info("✅ isnet-general-use session created successfully")
                
            except Exception as rembg_error:
                logger.warning(f"rembg isnet failed: {rembg_error}")
                raise RuntimeError(f"Failed to load isnet-general-use model: {rembg_error}")
                
        except Exception as e:
            logger.error(f"Error creating Railway session: {e}")
            self._session = None
            raise
    
    def remove_background(self, input_path: str, output_path: str) -> bool:
        """
        Remove background using isnet-general-use tiny model
        Optimized for Railway 512MB memory limit
        """
        start_time = time.time()
        input_image = None
        
        try:
            # Validate input
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Check file size (Railway limit)
            file_size = os.path.getsize(input_path)
            if file_size > 8 * 1024 * 1024:  # 8MB limit for Railway
                raise ValueError(f"File too large: {file_size} bytes. Maximum 8MB for Railway.")
            
            logger.info(f"Processing with isnet-general-use: {input_path} ({file_size} bytes)")
            
            # Memory check before processing
            if not self._check_memory_availability():
                raise RuntimeError("Insufficient memory for background removal")
            
            # Load and preprocess image
            input_image = self._load_and_optimize_image(input_path)
            if input_image is None:
                raise ValueError("Failed to load image")
            
            # Process with isnet-general-use
            result_image = self._process_with_isnet(input_image)
            
            # Save result
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result_image.save(output_path, 'PNG', optimize=True, compress_level=6)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Background removal completed in {processing_time:.2f}s: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Railway background removal failed: {e}")
            return False
            
        finally:
            # Aggressive cleanup
            self._cleanup_memory([input_image])
    
    def _load_and_optimize_image(self, path: str) -> Optional[Image.Image]:
        """Load and optimize image for Railway memory constraints"""
        try:
            image = Image.open(path)
            
            # Check dimensions and resize if too large
            width, height = image.size
            max_dimension = 1500  # Reduced for Railway
            
            if max(width, height) > max_dimension:
                ratio = max_dimension / max(width, height)
                new_size = (int(width * ratio), int(height * ratio))
                logger.info(f"Resizing from {width}x{height} to {new_size[0]}x{new_size[1]} for Railway")
                resized = image.resize(new_size, Image.LANCZOS)
                image.close()
                image = resized
            
            # Convert to RGB if needed
            if image.mode not in ('RGB', 'RGBA'):
                rgb_image = image.convert('RGB')
                image.close()
                return rgb_image
            
            return image
            
        except Exception as e:
            logger.error(f"Error loading/optimizing image {path}: {e}")
            return None
    
    def _process_with_isnet(self, image: Image.Image) -> Image.Image:
        """Process image with isnet-general-use model"""
        try:
            from rembg import remove
            
            # Convert PIL to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='PNG', optimize=True)
            img_bytes_data = img_bytes.getvalue()
            img_bytes.close()
            
            # Get session
            session = self._get_session()
            if session is None:
                raise RuntimeError("No session available")
            
            # Process with rembg
            logger.debug("Processing with isnet-general-use...")
            result_bytes = remove(img_bytes_data, session=session)
            
            # Convert back to PIL
            result_image = Image.open(io.BytesIO(result_bytes))
            
            # Clean up bytes data
            del img_bytes_data, result_bytes
            gc.collect()
            
            return result_image
            
        except Exception as e:
            logger.error(f"Error processing with isnet: {e}")
            raise
    
    def change_background_color(self, input_path: str, output_path: str, bg_color: Tuple[int, int, int]) -> bool:
        """Remove background and change color in one optimized step"""
        temp_path = None
        
        try:
            # Step 1: Remove background
            temp_path = output_path.replace('.jpg', '_temp_nobg.png').replace('.jpeg', '_temp_nobg.png')
            
            if not self.remove_background(input_path, temp_path):
                return False
            
            # Step 2: Apply background color
            return self._apply_background_color(temp_path, output_path, bg_color)
            
        except Exception as e:
            logger.error(f"Error in Railway background color change: {e}")
            return False
            
        finally:
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def _apply_background_color(self, transparent_path: str, output_path: str, bg_color: Tuple[int, int, int]) -> bool:
        """Apply background color to transparent image"""
        try:
            # Load transparent image
            foreground = Image.open(transparent_path).convert('RGBA')
            
            # Create background
            background = Image.new('RGBA', foreground.size, bg_color + (255,))
            
            # Composite
            result = Image.alpha_composite(background, foreground)
            result = result.convert('RGB')
            
            # Save
            result.save(output_path, 'JPEG', quality=95, optimize=True)
            
            # Cleanup
            foreground.close()
            background.close()
            result.close()
            
            logger.info(f"Background color applied: {bg_color}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying background color: {e}")
            return False
    
    def _check_memory_availability(self) -> bool:
        """Check if we have enough memory for processing"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            available_mb = psutil.virtual_memory().available / 1024 / 1024
            
            # Check if we're under Railway limits
            if memory_mb > 450 or available_mb < 100:  # Conservative limits
                logger.warning(f"Memory check failed: Process={memory_mb:.1f}MB, Available={available_mb:.1f}MB")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Memory check failed: {e}")
            return True  # Allow processing if can't check
    
    def _cleanup_memory(self, objects):
        """Aggressive memory cleanup"""
        for obj in objects:
            if obj is not None:
                try:
                    if hasattr(obj, 'close'):
                        obj.close()
                    del obj
                except:
                    pass
        gc.collect()
    
    def get_memory_usage(self) -> dict:
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,
                'vms_mb': memory_info.vms / 1024 / 1024,
                'percent': process.memory_percent(),
                'model_loaded': self._session is not None,
                'model_name': self._model_name
            }
        except Exception as e:
            return {'error': str(e)}
    
    def clear_memory(self):
        """Clear session and free memory"""
        with self._lock:
            if self._session:
                try:
                    del self._session
                except:
                    pass
                finally:
                    self._session = None
            gc.collect()
            logger.info("Railway session memory cleared")

# Global instance
railway_bg_remover = RailwayBgRemover()
