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
            # Use a lighter model for Railway's memory constraints
            if os.environ.get('RAILWAY_ENVIRONMENT_NAME'):
                # Use smaller model in production to save memory
                if model_name == 'u2net':
                    model_name = 'u2netp'  # Smaller version
            
            # Reuse session if same model
            if self._session is not None and self._current_model == model_name:
                logger.debug(f"Reusing existing session for {model_name}")
                return self._session
            
            # Clear old session if exists
            if self._session is not None:
                logger.info(f"Switching from {self._current_model} to {model_name}")
                self._clear_session()
            
            # Create new session
            try:
                logger.info(f"Creating new session for model: {model_name}")
                self._session = new_session(model_name)
                self._current_model = model_name
                logger.info(f"Session created successfully for {model_name}")
                return self._session
            except Exception as e:
                logger.error(f"Failed to create session for {model_name}: {e}")
                # Fallback to smaller model
                if model_name != 'u2netp':
                    logger.info("Falling back to u2netp model")
                    return self.get_session('u2netp')
                raise e
    
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
