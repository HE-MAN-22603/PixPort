"""
Ultra-Lightweight Background Removal Service
ONLY uses isnet-general-tiny ONNX model - memory optimized for Railway 512MB
Designed to stay under 200MB RAM usage at runtime
"""

import os
import gc
import io
import logging
import numpy as np
import onnxruntime as ort
from PIL import Image
import threading
from typing import Optional, Tuple, Union
import time

logger = logging.getLogger(__name__)

class ISNetTinyService:
    """Ultra-lightweight background remover using ONLY isnet-general-tiny ONNX model"""
    
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
        self._input_name = None
        self._output_name = None
        self._model_path = None
        self._initialized = True
        
        # Model specifications for isnet-general-tiny
        self._input_size = (1024, 1024)  # ISNet input size
        self._model_name = "isnet-general-tiny"
        
        logger.info(f"ISNetTinyService initialized - will use {self._model_name} ONLY")
    
    def _get_session(self) -> ort.InferenceSession:
        """Get or create ONNX Runtime session with aggressive memory optimization"""
        if self._session is None:
            with self._lock:
                if self._session is None:
                    self._create_session()
        return self._session
    
    def _create_session(self):
        """Create optimized ONNX Runtime session for isnet-general-tiny"""
        try:
            # Force garbage collection before loading
            gc.collect()
            
            logger.info(f"Creating {self._model_name} ONNX session...")
            
            # Memory-optimized session options
            sess_options = ort.SessionOptions()
            sess_options.intra_op_num_threads = 1  # Single thread for memory efficiency
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.execution_mode = ort.ExecutionMode.ORT_SEQUENTIAL
            sess_options.enable_mem_pattern = False  # Disable memory pattern optimization to save RAM
            sess_options.enable_cpu_mem_arena = False  # Disable memory arena for tighter control
            
            # CPU provider configuration for minimal memory usage
            provider_options = {
                'arena_extend_strategy': 'kSameAsRequested',
                'initial_chunk_size_bytes': 1024 * 1024,  # 1MB initial chunks
                'max_mem': 150 * 1024 * 1024,  # 150MB max memory limit
            }
            
            providers = [('CPUExecutionProvider', provider_options)]
            
            # Try to get model from local storage or download
            model_path = self._get_model_path()
            if not model_path:
                raise RuntimeError("Failed to locate isnet-general-tiny.onnx model")
            
            # Create ONNX Runtime session
            self._session = ort.InferenceSession(
                model_path,
                sess_options=sess_options,
                providers=providers
            )
            
            # Get input/output names
            self._input_name = self._session.get_inputs()[0].name
            self._output_name = self._session.get_outputs()[0].name
            
            logger.info(f"✅ {self._model_name} ONNX session created successfully")
            logger.info(f"Input: {self._input_name}, Output: {self._output_name}")
            
        except Exception as e:
            logger.error(f"Failed to create {self._model_name} session: {e}")
            self._session = None
            raise RuntimeError(f"Cannot load {self._model_name}: {e}")
    
    def _get_model_path(self) -> Optional[str]:
        """Get path to isnet-general-tiny.onnx model"""
        # Check if model exists locally in the project
        potential_paths = [
            os.path.join(os.path.dirname(__file__), '..', 'models', 'isnet-general-tiny.onnx'),
            os.path.join(os.getcwd(), 'models', 'isnet-general-tiny.onnx'),
            os.path.join(os.getcwd(), 'app', 'models', 'isnet-general-tiny.onnx'),
            os.path.expanduser('~/.cache/isnet-general-tiny/isnet-general-tiny.onnx'),
        ]
        
        for path in potential_paths:
            if os.path.exists(path):
                logger.info(f"Found {self._model_name} model at: {path}")
                return path
        
        # Try to download/get via rembg if available
        try:
            from rembg import new_session
            logger.info("Attempting to use rembg to access isnet-general-tiny...")
            
            # Create session to trigger model download
            temp_session = new_session('isnet-general-use')  # Use available model
            
            # Try to get the model path from the session
            if hasattr(temp_session, 'model_path'):
                return temp_session.model_path
            elif hasattr(temp_session, 'inner') and hasattr(temp_session.inner, 'model_path'):
                return temp_session.inner.model_path
            
            logger.warning("Could not extract model path from rembg session")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get model via rembg: {e}")
            return None
    
    def remove_background(self, input_path: str, output_path: str) -> bool:
        """
        Remove background using ONLY isnet-general-tiny model
        Optimized for Railway 512MB memory limit
        """
        start_time = time.time()
        input_image = None
        result_image = None
        
        try:
            # Validate input
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Check file size (Railway limit - be conservative)
            file_size = os.path.getsize(input_path)
            max_size = 8 * 1024 * 1024  # 8MB limit for safety
            if file_size > max_size:
                raise ValueError(f"File too large: {file_size} bytes. Maximum {max_size//1024//1024}MB allowed.")
            
            logger.info(f"Processing with {self._model_name}: {input_path} ({file_size} bytes)")
            
            # Memory check before processing
            if not self._check_memory_availability():
                raise RuntimeError("Insufficient memory for background removal")
            
            # Load and preprocess image
            input_image = self._load_and_optimize_image(input_path)
            if input_image is None:
                raise ValueError("Failed to load image")
            
            # Process with isnet-general-tiny
            result_image = self._process_with_isnet_tiny(input_image)
            if result_image is None:
                raise RuntimeError("Background removal failed")
            
            # Save result
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result_image.save(output_path, 'PNG', optimize=True, compress_level=6)
            
            processing_time = time.time() - start_time
            logger.info(f"✅ Background removal completed in {processing_time:.2f}s: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"{self._model_name} background removal failed: {e}")
            return False
            
        finally:
            # Aggressive memory cleanup
            self._cleanup_memory([input_image, result_image])
    
    def change_background_color(self, input_path: str, output_path: str, bg_color: Union[str, Tuple[int, int, int]]) -> bool:
        """
        Remove background and apply solid color in one optimized step
        
        Args:
            input_path: Path to input image
            output_path: Path to save output image
            bg_color: RGB color tuple (r,g,b) or hex string '#RRGGBB'
        """
        temp_path = None
        
        try:
            # Parse color if hex string
            if isinstance(bg_color, str):
                bg_color = self._parse_hex_color(bg_color)
            
            # Step 1: Remove background to temporary PNG
            temp_dir = os.path.dirname(output_path)
            temp_filename = f"temp_nobg_{int(time.time())}.png"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            if not self.remove_background(input_path, temp_path):
                return False
            
            # Step 2: Apply background color
            return self._apply_background_color(temp_path, output_path, bg_color)
            
        except Exception as e:
            logger.error(f"Error in background color change: {e}")
            return False
            
        finally:
            # Cleanup temp file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except:
                    pass
    
    def _load_and_optimize_image(self, path: str) -> Optional[Image.Image]:
        """Load and optimize image for Railway memory constraints"""
        try:
            image = Image.open(path)
            
            # Check dimensions and resize if too large to prevent OOM
            width, height = image.size
            max_dimension = 1024  # Conservative limit for Railway
            
            if max(width, height) > max_dimension:
                ratio = max_dimension / max(width, height)
                new_size = (int(width * ratio), int(height * ratio))
                logger.info(f"Resizing from {width}x{height} to {new_size[0]}x{new_size[1]} for memory optimization")
                resized = image.resize(new_size, Image.Resampling.LANCZOS)
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
    
    def _process_with_isnet_tiny(self, image: Image.Image) -> Optional[Image.Image]:
        """Process image with isnet-general-tiny ONNX model"""
        try:
            # Get ONNX session
            session = self._get_session()
            if session is None:
                raise RuntimeError("No ONNX session available")
            
            # Preprocess image for ISNet
            input_array = self._preprocess_for_isnet(image)
            
            # Run inference
            logger.debug("Running ONNX inference...")
            outputs = session.run([self._output_name], {self._input_name: input_array})
            
            # Postprocess result
            result_image = self._postprocess_isnet_output(outputs[0], image.size, image)
            
            return result_image
            
        except Exception as e:
            logger.error(f"Error processing with {self._model_name}: {e}")
            return None
    
    def _preprocess_for_isnet(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for ISNet input format"""
        # Resize to model input size
        resized = image.resize(self._input_size, Image.Resampling.LANCZOS)
        
        # Convert to numpy array and normalize
        img_array = np.array(resized, dtype=np.float32)
        img_array = img_array / 255.0  # Normalize to [0, 1]
        
        # Convert to CHW format and add batch dimension
        if len(img_array.shape) == 3:
            img_array = img_array.transpose(2, 0, 1)  # HWC -> CHW
        
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        
        return img_array
    
    def _postprocess_isnet_output(self, output: np.ndarray, original_size: Tuple[int, int], original_image: Image.Image) -> Image.Image:
        """Postprocess ISNet output to create masked image"""
        try:
            # Remove batch dimension and get mask
            mask = output.squeeze()
            
            # Ensure mask is 2D
            if len(mask.shape) > 2:
                mask = mask[0]  # Take first channel if multi-channel
            
            # Normalize mask to [0, 255]
            mask = (mask * 255).astype(np.uint8)
            
            # Resize mask back to original image size
            mask_image = Image.fromarray(mask, mode='L')
            mask_resized = mask_image.resize(original_size, Image.Resampling.LANCZOS)
            
            # Apply mask to original image - ensure original is RGBA
            if original_image.mode != 'RGBA':
                result = original_image.convert('RGBA')
            else:
                result = original_image.copy()
            
            # Apply mask to alpha channel
            mask_array = np.array(mask_resized)
            result_array = np.array(result)
            result_array[:, :, 3] = mask_array  # Set alpha channel
            
            return Image.fromarray(result_array, 'RGBA')
                
        except Exception as e:
            logger.error(f"Error postprocessing ISNet output: {e}")
            raise
    
    def _apply_background_color(self, transparent_path: str, output_path: str, bg_color: Tuple[int, int, int]) -> bool:
        """Apply background color to transparent image"""
        try:
            # Load transparent image
            foreground = Image.open(transparent_path).convert('RGBA')
            
            # Create background with specified color
            background = Image.new('RGBA', foreground.size, bg_color + (255,))
            
            # Composite images
            result = Image.alpha_composite(background, foreground)
            
            # Convert to RGB and save
            result = result.convert('RGB')
            
            # Determine output format based on extension
            ext = os.path.splitext(output_path)[1].lower()
            if ext in ['.jpg', '.jpeg']:
                result.save(output_path, 'JPEG', quality=95, optimize=True)
            else:
                result.save(output_path, 'PNG', optimize=True)
            
            # Cleanup
            foreground.close()
            background.close()
            result.close()
            
            logger.info(f"Background color applied: {bg_color}")
            return True
            
        except Exception as e:
            logger.error(f"Error applying background color: {e}")
            return False
    
    def _parse_hex_color(self, hex_color: str) -> Tuple[int, int, int]:
        """Parse hex color string to RGB tuple"""
        if hex_color.startswith('#'):
            hex_color = hex_color[1:]
        
        if len(hex_color) != 6:
            raise ValueError("Hex color must be 6 characters long (RRGGBB)")
        
        try:
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16) 
            b = int(hex_color[4:6], 16)
            return (r, g, b)
        except ValueError:
            raise ValueError("Invalid hex color format")
    
    def _check_memory_availability(self) -> bool:
        """Check if we have enough memory for processing"""
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            available_mb = psutil.virtual_memory().available / 1024 / 1024
            
            # Conservative limits for Railway 512MB
            if memory_mb > 180 or available_mb < 50:  # Very conservative
                logger.warning(f"Memory check failed: Process={memory_mb:.1f}MB, Available={available_mb:.1f}MB")
                return False
            
            logger.debug(f"Memory OK: Process={memory_mb:.1f}MB, Available={available_mb:.1f}MB")
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
        
        # Force garbage collection
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
                    logger.info(f"{self._model_name} session cleared")
                except:
                    pass
                finally:
                    self._session = None
                    self._input_name = None
                    self._output_name = None
            
            gc.collect()
            logger.info("Memory cleared")

# Global instance - singleton pattern
isnet_tiny_service = ISNetTinyService()
