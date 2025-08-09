"""
Optimized AI model manager for memory-constrained environments
"""

import os
import gc
import threading
from typing import Optional
from rembg import new_session
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """Singleton model manager to optimize memory usage"""
    
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
        self._current_model = None
        self._lock = threading.Lock()
        self._initialized = True
        logger.info("ModelManager initialized")
    
    def get_session(self, model_name: str = 'u2net'):
        """Get or create a rembg session with memory optimization"""
        with self._lock:
            # Force smaller model for Railway's memory constraints
            original_model = model_name
            if os.environ.get('RAILWAY_ENVIRONMENT_NAME') or self._is_memory_constrained():
                # Always use the smallest model in production or memory-constrained environments
                model_name = 'u2netp'  # Tiny U²-Net - smallest available model (~4.7MB)
                logger.info(f"Memory-constrained mode: using {model_name} instead of {original_model}")
            elif model_name == 'u2net':
                # Default to u2netp for better memory usage
                model_name = 'u2netp'
                logger.info(f"Defaulting to memory-efficient u2netp instead of {original_model}")
            
            # Reuse session if same model
            if self._session is not None and self._current_model == model_name:
                logger.debug(f"Reusing existing session for {model_name}")
                return self._session
            
            # Clear old session if exists
            if self._session is not None:
                logger.info(f"Switching from {self._current_model} to {model_name}")
                self._clear_session()
            
            # Create new session with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    logger.info(f"Creating session for {model_name} (attempt {attempt + 1}/{max_retries})")
                    
                    # Force garbage collection before loading
                    import gc
                    gc.collect()
                    
                    # Create session
                    self._session = new_session(model_name)
                    self._current_model = model_name
                    logger.info(f"Session created successfully for {model_name}")
                    return self._session
                    
                except Exception as e:
                    logger.error(f"Attempt {attempt + 1} failed for {model_name}: {e}")
                    
                    # Clear any partial state
                    self._clear_session()
                    
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(2)  # Wait before retry
                    else:
                        # Final fallback - raise error for calling code to handle
                        logger.error(f"All attempts failed for {model_name}")
                        raise RuntimeError(f"Failed to load AI model after {max_retries} attempts: {str(e)}")
    
    def _clear_session(self):
        """Clear current session and free memory"""
        if self._session is not None:
            try:
                # Try to clear session resources
                if hasattr(self._session, 'clear'):
                    self._session.clear()
                elif hasattr(self._session, 'close'):
                    self._session.close()
                del self._session
                logger.info(f"Cleared session for {self._current_model}")
            except Exception as e:
                logger.warning(f"Error clearing session: {e}")
            finally:
                self._session = None
                self._current_model = None
                # Force garbage collection
                gc.collect()
    
    def _is_memory_constrained(self) -> bool:
        """Check if system is memory constrained"""
        try:
            import psutil
            # Get total system memory in MB
            total_memory_mb = psutil.virtual_memory().total / 1024 / 1024
            
            # Consider memory constrained if less than 1GB total system memory
            # or if we're using more than 70% of available memory
            available_memory_mb = psutil.virtual_memory().available / 1024 / 1024
            memory_usage_percent = psutil.virtual_memory().percent
            
            is_constrained = (
                total_memory_mb < 1024 or  # Less than 1GB total
                available_memory_mb < 256 or  # Less than 256MB available
                memory_usage_percent > 70  # Using more than 70% of memory
            )
            
            if is_constrained:
                logger.info(f"Memory constrained detected: {total_memory_mb:.1f}MB total, {available_memory_mb:.1f}MB available, {memory_usage_percent:.1f}% used")
            
            return is_constrained
            
        except Exception as e:
            logger.warning(f"Could not check memory constraints: {e}")
            # Default to constrained mode for safety
            return True
    
    def clear_all(self):
        """Clear all loaded models and free memory"""
        with self._lock:
            self._clear_session()
            logger.info("All models cleared")
    
    def get_memory_info(self):
        """Get memory usage information"""
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent(),
            'current_model': self._current_model
        }

# Global model manager instance
model_manager = ModelManager()
