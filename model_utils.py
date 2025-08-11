"""
Optimized Model Utilities for Google Cloud Run
Designed for fast startup and minimal memory usage
"""

import os
import gc
import logging
import threading
import time
from typing import Optional, Tuple, Union
from concurrent.futures import ThreadPoolExecutor
import onnxruntime as ort
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)

class OptimizedModelManager:
    """
    Singleton model manager optimized for Google Cloud Run
    Preloads model during container startup for faster first requests
    """
    
    _instance = None
    _lock = threading.Lock()
    _executor = ThreadPoolExecutor(max_workers=2)  # Non-blocking inference
    
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
        self._input_name = None
        self._output_name = None
        self._model_ready = False
        self._input_size = (1024, 1024)
        self._model_name = "isnet-general-tiny"
        self._warmup_done = False
        self._initialized = True
        
        logger.info("OptimizedModelManager initialized")
    
    def preload_model(self) -> bool:
        """
        Preload the AI model during container startup
        Called from app.py before first request
        """
        try:
            logger.info("🚀 Preloading AI model for Google Cloud Run...")
            start_time = time.time()
            
            # Force garbage collection before loading
            gc.collect()
            
            # Create optimized ONNX session
            success = self._create_optimized_session()
            
            if success:
                load_time = time.time() - start_time
                logger.info(f"✅ Model preloaded successfully in {load_time:.2f}s")
                self._model_ready = True
                
                # Run warmup in background
                self._executor.submit(self._warmup_model)
                return True
            else:
                logger.error("❌ Failed to preload model")
                return False
                
        except Exception as e:
            logger.error(f"❌ Model preload failed: {e}")
            return False
    
    def _create_optimized_session(self) -> bool:
        """Create optimized ONNX Runtime session for Cloud Run"""
        try:
            # Session options optimized for Cloud Run
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 2  # Cloud Run has better CPU allocation
            sess_options.inter_op_num_threads = 1
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            sess_options.enable_mem_pattern = True  # Better memory management on Cloud Run
            sess_options.enable_cpu_mem_arena = True
            
            # CPU provider with Cloud Run optimizations
            provider_options = {
                'arena_extend_strategy': 'kSameAsRequested',
                'initial_chunk_size_bytes': 2 * 1024 * 1024,  # 2MB chunks
                'max_mem': 512 * 1024 * 1024,  # 512MB limit (Cloud Run has 2GB)
            }
            
            providers = [('CPUExecutionProvider', provider_options)]
            
            # Get model path
            model_path = self._get_model_path()
            if not model_path:
                raise RuntimeError("Model file not found")
            
            # Create session
            self._session = ort.InferenceSession(
                model_path,
                sess_options=sess_options,
                providers=providers
            )
            
            # Get input/output names
            self._input_name = self._session.get_inputs()[0].name
            self._output_name = self._session.get_outputs()[0].name
            
            logger.info(f"✅ ONNX session created: {self._input_name} -> {self._output_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create ONNX session: {e}")
            return False
    
    def _get_model_path(self) -> Optional[str]:
        """Get path to the AI model file"""
        # Try multiple potential model locations
        potential_paths = [
            # Local model file
            os.path.join(os.getcwd(), 'models', 'isnet-general-tiny.onnx'),
            os.path.join(os.path.dirname(__file__), 'models', 'isnet-general-tiny.onnx'),
            # rembg cache locations
            os.path.expanduser('~/.u2net/isnet-general-tiny.onnx'),
            os.path.expanduser('~/.cache/huggingface/transformers/isnet-general-tiny.onnx'),
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                logger.info(f"📂 Found model at: {path}")
                return path
        
        # Try to download via rembg
        try:
            logger.info("📥 Downloading model via rembg...")
            from rembg import new_session
            temp_session = new_session('isnet-general-use')
            
            # Extract model path from session
            if hasattr(temp_session, 'model_path'):
                return temp_session.model_path
            elif hasattr(temp_session, 'inner') and hasattr(temp_session.inner, 'model_path'):
                return temp_session.inner.model_path
            
            logger.warning("Could not extract model path from rembg session")
            return None
            
        except Exception as e:
            logger.error(f"Failed to download model: {e}")
            return None
    
    def _warmup_model(self):
        """
        Run a warmup inference to prepare the model
        This makes the first real request much faster
        """
        try:
            logger.info("🔥 Running model warmup...")
            start_time = time.time()
            
            # Create a dummy input image (small for faster warmup)
            dummy_image = Image.new('RGB', (512, 512), color='red')
            
            # Run warmup inference
            result = self._process_image_internal(dummy_image)
            
            if result is not None:
                warmup_time = time.time() - start_time
                logger.info(f"✅ Model warmup completed in {warmup_time:.2f}s")
                self._warmup_done = True
            else:
                logger.warning("⚠️ Model warmup failed")
                
        except Exception as e:
            logger.error(f"❌ Model warmup error: {e}")
        finally:
            # Clean up dummy image
            try:
                dummy_image.close()
            except:
                pass
            gc.collect()
    
    def is_ready(self) -> bool:
        """Check if model is ready for inference"""
        return self._model_ready and self._session is not None
    
    def is_warmed_up(self) -> bool:
        """Check if model warmup is complete"""
        return self._warmup_done
    
    def remove_background(self, input_path: str, output_path: str, non_blocking: bool = False) -> Union[bool, None]:
        """
        Remove background from image
        
        Args:
            input_path: Input image path
            output_path: Output image path  
            non_blocking: If True, run in background thread
            
        Returns:
            bool: Success status (or None if non_blocking)
        """
        if non_blocking:
            # Submit to thread pool for non-blocking execution
            future = self._executor.submit(self._remove_background_sync, input_path, output_path)
            return None  # Client should check result endpoint
        else:
            return self._remove_background_sync(input_path, output_path)
    
    def _remove_background_sync(self, input_path: str, output_path: str) -> bool:
        """Synchronous background removal"""
        try:
            if not self.is_ready():
                raise RuntimeError("Model not ready")
            
            # Validate input
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Load and process image
            image = self._load_and_optimize_image(input_path)
            if image is None:
                raise ValueError("Failed to load image")
            
            # Process with AI model
            result_image = self._process_image_internal(image)
            if result_image is None:
                raise RuntimeError("Background removal failed")
            
            # Save result
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result_image.save(output_path, 'PNG', optimize=True, compress_level=6)
            
            logger.info(f"✅ Background removed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Background removal failed: {e}")
            return False
        finally:
            # Cleanup
            try:
                if 'image' in locals() and image:
                    image.close()
                if 'result_image' in locals() and result_image:
                    result_image.close()
            except:
                pass
    
    def change_background_color(self, input_path: str, output_path: str, bg_color: Union[str, Tuple[int, int, int]]) -> bool:
        """Remove background and apply color in one optimized operation"""
        try:
            # Parse color if hex string
            if isinstance(bg_color, str):
                bg_color = self._parse_hex_color(bg_color)
            
            # Step 1: Remove background to memory (don't save intermediate file)
            image = self._load_and_optimize_image(input_path)
            if image is None:
                raise ValueError("Failed to load image")
            
            transparent_image = self._process_image_internal(image)
            if transparent_image is None:
                raise RuntimeError("Background removal failed")
            
            # Step 2: Apply background color directly
            result = self._apply_background_color_to_image(transparent_image, bg_color)
            if result is None:
                raise RuntimeError("Background color application failed")
            
            # Save final result
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            ext = os.path.splitext(output_path)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                result.save(output_path, 'JPEG', quality=95, optimize=True)
            else:
                result.save(output_path, 'PNG', optimize=True)
            
            logger.info(f"✅ Background color changed: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Background color change failed: {e}")
            return False
        finally:
            # Cleanup
            try:
                for img in ['image', 'transparent_image', 'result']:
                    if img in locals() and locals()[img]:
                        locals()[img].close()
            except:
                pass
    
    def _load_and_optimize_image(self, path: str) -> Optional[Image.Image]:
        """Load and optimize image for Cloud Run processing"""
        try:
            image = Image.open(path)
            
            # Optimize size for Cloud Run (has more memory than Railway)
            width, height = image.size
            max_dimension = 1920  # Higher limit for Cloud Run
            
            if max(width, height) > max_dimension:
                ratio = max_dimension / max(width, height)
                new_size = (int(width * ratio), int(height * ratio))
                logger.info(f"Resizing {width}x{height} -> {new_size[0]}x{new_size[1]}")
                resized = image.resize(new_size, Image.Resampling.LANCZOS)
                image.close()
                image = resized
            
            # Ensure RGB/RGBA format
            if image.mode not in ('RGB', 'RGBA'):
                rgb_image = image.convert('RGB')
                image.close()
                return rgb_image
            
            return image
            
        except Exception as e:
            logger.error(f"Error loading image {path}: {e}")
            return None
    
    def _process_image_internal(self, image: Image.Image) -> Optional[Image.Image]:
        """Internal image processing with the AI model"""
        try:
            if not self._session:
                raise RuntimeError("No active session")
            
            # Preprocess for model
            input_array = self._preprocess_for_model(image)
            
            # Run inference
            outputs = self._session.run([self._output_name], {self._input_name: input_array})
            
            # Postprocess result
            result_image = self._postprocess_output(outputs[0], image.size, image)
            
            return result_image
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return None
    
    def _preprocess_for_model(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for model input"""
        # Resize to model input size
        resized = image.resize(self._input_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy and normalize
        img_array = np.array(resized, dtype=np.float32) / 255.0
        
        # Convert to CHW format and add batch dimension
        if len(img_array.shape) == 3:
            img_array = img_array.transpose(2, 0, 1)  # HWC -> CHW
        
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
        return img_array
    
    def _postprocess_output(self, output: np.ndarray, original_size: Tuple[int, int], original_image: Image.Image) -> Image.Image:
        """Postprocess model output to create final image"""
        try:
            # Get mask from output
            mask = output.squeeze()
            if len(mask.shape) > 2:
                mask = mask[0]  # Take first channel
            
            # Normalize to [0, 255]
            mask = (mask * 255).astype(np.uint8)
            
            # Resize mask to original size
            mask_image = Image.fromarray(mask, mode='L')
            mask_resized = mask_image.resize(original_size, Image.Resampling.LANCZOS)
            
            # Apply mask to create transparent image
            if original_image.mode != 'RGBA':
                result = original_image.convert('RGBA')
            else:
                result = original_image.copy()
            
            # Apply mask to alpha channel
            mask_array = np.array(mask_resized)
            result_array = np.array(result)
            result_array[:, :, 3] = mask_array
            
            return Image.fromarray(result_array, 'RGBA')
                
        except Exception as e:
            logger.error(f"Error in postprocessing: {e}")
            raise
    
    def _apply_background_color_to_image(self, transparent_image: Image.Image, bg_color: Tuple[int, int, int]) -> Image.Image:
        """Apply background color to transparent image"""
        try:
            # Create background with specified color
            background = Image.new('RGBA', transparent_image.size, bg_color + (255,))
            
            # Composite images
            result = Image.alpha_composite(background, transparent_image)
            
            # Convert to RGB
            final_result = result.convert('RGB')
            
            # Cleanup intermediate images
            background.close()
            result.close()
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error applying background color: {e}")
            return None
    
    def _parse_hex_color(self, hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color string to RGB tuple"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters (RRGGBB)")
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except ValueError:
            raise ValueError("Invalid hex color format")
    
    def get_status(self) -> dict:
        """Get model status information"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            
            return {
                'model_ready': self._model_ready,
                'warmup_complete': self._warmup_done,
                'model_name': self._model_name,
                'memory_usage_mb': round(memory_mb, 2),
                'session_active': self._session is not None
            }
        except Exception as e:
            return {'error': str(e)}
    
    def clear_memory(self):
        """Clear model and free memory"""
        with self._lock:
            if self._session:
                try:
                    del self._session
                    logger.info("Model session cleared")
                except:
                    pass
                finally:
                    self._session = None
                    self._model_ready = False
                    self._warmup_done = False
            
            gc.collect()

# Global instance
model_manager = OptimizedModelManager()

# Public functions for backward compatibility
def load_model() -> bool:
    """Load and initialize the AI model (called during startup)"""
    return model_manager.preload_model()

def predict(input_path: str, output_path: str, operation: str = 'remove', **kwargs) -> bool:
    """
    Run prediction with the loaded model
    
    Args:
        input_path: Input image path
        output_path: Output image path  
        operation: 'remove' or 'change_color'
        **kwargs: Additional parameters (bg_color for change_color)
    """
    if operation == 'change_color':
        bg_color = kwargs.get('bg_color', 'white')
        return model_manager.change_background_color(input_path, output_path, bg_color)
    else:
        return model_manager.remove_background(input_path, output_path)
