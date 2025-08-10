"""
Model Warmer Service for Google Cloud Run
Ensures models are pre-loaded and ready for immediate use
"""

import os
import logging
import threading
import time
from typing import Optional, Dict, Any
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)

class ModelWarmer:
    """Singleton class to manage model warming and caching"""
    
    _instance = None
    _lock = threading.Lock()
    _models_cache = {}
    _warming_status = {}
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self._warm_models_async()
    
    def _warm_models_async(self):
        """Start model warming in background thread"""
        def warm_worker():
            try:
                logger.info("🔥 Starting model warming process...")
                
                # Create a small test image
                test_image = self._create_test_image()
                
                # Warm ISNet model (most memory efficient)
                self._warm_isnet_model(test_image)
                
                # Warm backup models if available
                self._warm_backup_models(test_image)
                
                logger.info("✅ Model warming completed successfully")
                
            except Exception as e:
                logger.error(f"❌ Model warming failed: {e}")
        
        # Don't block startup - warm in background
        warming_thread = threading.Thread(target=warm_worker, daemon=True)
        warming_thread.start()
    
    def _create_test_image(self) -> Image.Image:
        """Create a small test image for model warming"""
        # Create 100x100 RGB test image
        test_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        return Image.fromarray(test_array)
    
    def _warm_isnet_model(self, test_image: Image.Image):
        """Warm the ISNet model (primary choice for Cloud Run)"""
        try:
            self._warming_status['isnet'] = 'warming'
            logger.info("   🔥 Warming ISNet model...")
            
            from rembg import new_session, remove
            
            # Create session and cache it
            session = new_session('isnet-general-use')
            self._models_cache['isnet'] = session
            
            # Test the model with dummy image
            remove(test_image, session=session)
            
            self._warming_status['isnet'] = 'ready'
            logger.info("   ✅ ISNet model ready (isnet-general-use)")
            
        except Exception as e:
            logger.warning(f"   ⚠️ ISNet warming failed: {e}")
            self._warming_status['isnet'] = 'failed'
    
    def _warm_backup_models(self, test_image: Image.Image):
        """Warm backup models if primary fails"""
        backup_models = ['u2netp', 'u2net']
        
        for model_name in backup_models:
            try:
                self._warming_status[model_name] = 'warming'
                logger.info(f"   🔥 Warming backup model: {model_name}...")
                
                from rembg import new_session, remove
                
                session = new_session(model_name)
                self._models_cache[model_name] = session
                
                # Quick test
                remove(test_image, session=session)
                
                self._warming_status[model_name] = 'ready'
                logger.info(f"   ✅ Backup model ready: {model_name}")
                
                # Only warm one backup to save memory
                break
                
            except Exception as e:
                logger.warning(f"   ⚠️ {model_name} warming failed: {e}")
                self._warming_status[model_name] = 'failed'
    
    def get_model(self, model_name: str = 'isnet') -> Optional[Any]:
        """Get warmed model or create new session"""
        try:
            # Return cached model if available
            if model_name in self._models_cache:
                logger.info(f"📦 Using cached {model_name} model")
                return self._models_cache[model_name]
            
            # Create new session if not cached
            logger.info(f"🆕 Creating new {model_name} session")
            from rembg import new_session
            
            model_map = {
                'isnet': 'isnet-general-use',
                'u2netp': 'u2netp',
                'u2net': 'u2net'
            }
            
            actual_model = model_map.get(model_name, model_name)
            session = new_session(actual_model)
            
            # Cache for future use
            self._models_cache[model_name] = session
            return session
            
        except Exception as e:
            logger.error(f"❌ Failed to get model {model_name}: {e}")
            return None
    
    def get_status(self) -> Dict[str, str]:
        """Get current warming status"""
        return self._warming_status.copy()
    
    def is_ready(self, model_name: str = 'isnet') -> bool:
        """Check if specific model is ready"""
        return self._warming_status.get(model_name) == 'ready'

# Global instance
model_warmer = ModelWarmer()

def get_warmed_model(model_name: str = 'isnet'):
    """Get a pre-warmed model instance"""
    return model_warmer.get_model(model_name)

def get_warming_status():
    """Get current model warming status"""
    return model_warmer.get_status()
