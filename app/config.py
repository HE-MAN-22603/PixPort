"""
PixPort Configuration Settings
"""

import os
from dotenv import load_dotenv
import tempfile

load_dotenv()

class Config:
    """Flask configuration class"""
    
    # Basic Flask config - require SECRET_KEY in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    def __init__(self):
        # Validate critical configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate critical configuration settings"""
        # Require SECRET_KEY in production environments
        if not self.SECRET_KEY:
            if os.environ.get('RAILWAY_ENVIRONMENT_NAME') or os.environ.get('FLASK_ENV') == 'production':
                raise ValueError(
                    "SECRET_KEY environment variable is required in production. "
                    "Please set SECRET_KEY to a secure random string."
                )
            else:
                # Only use fallback in development
                self.SECRET_KEY = 'dev-secret-key-change-in-production-' + str(hash(os.getcwd()))
                import warnings
                warnings.warn(
                    "Using default SECRET_KEY in development. Set SECRET_KEY environment variable for production.",
                    UserWarning
                )
        
        # Validate SECRET_KEY strength
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        
        # Warn about weak keys
        weak_keys = ['dev-secret-key', 'change-me', 'secret', 'key', 'password']
        if any(weak in self.SECRET_KEY.lower() for weak in weak_keys):
            if os.environ.get('RAILWAY_ENVIRONMENT_NAME'):
                raise ValueError("SECRET_KEY appears to be a weak/default key. Please use a strong random key.")
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Use temp directories for Railway deployment
    if os.environ.get('RAILWAY_ENVIRONMENT_NAME'):
        # Railway deployment - use /tmp for file storage
        UPLOAD_FOLDER = '/tmp/pixport/uploads'
        PROCESSED_FOLDER = '/tmp/pixport/processed'
        # Ensure directories exist
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(PROCESSED_FOLDER, exist_ok=True)
    else:
        # Local development
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
        PROCESSED_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'processed')
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'heic', 'webp'}
    
    # AI Model settings
    REMBG_MODEL = os.environ.get('REMBG_MODEL') or 'u2net'
    
    # Rate limiting - Use Redis URL from Railway if available
    REDIS_URL = os.environ.get('REDIS_URL')
    if REDIS_URL:
        RATELIMIT_STORAGE_URL = REDIS_URL
    else:
        RATELIMIT_STORAGE_URL = 'memory://'
    
    # Passport photo standards (width, height in pixels at 300 DPI)
    PASSPORT_SIZES = {
        'US': (413, 531),        # 2x2 inches (35x45mm)
        'EU': (413, 531),        # 35x45mm
        'UK': (413, 531),        # 35x45mm
        'CANADA': (413, 531),    # 35x45mm
        'GERMANY': (413, 531),   # 35x45mm
        'FRANCE': (413, 531),    # 35x45mm
        'AUSTRALIA': (413, 531), # 35x45mm
        'JAPAN': (413, 531),     # 35x45mm
        'INDIA': (413, 413),     # 35x35mm (square)
        'CHINA': (390, 567),     # 33x48mm
        # Legacy aliases
        'India': (413, 413),     # Keep for compatibility
        'Canada': (413, 531),    # Keep for compatibility
        'Australia': (413, 531), # Keep for compatibility
        'Japan': (413, 531),     # Keep for compatibility
    }
    
    # Background colors (RGB) - 5 Standard Colors
    BACKGROUND_COLORS = {
        'white': (255, 255, 255),        # Classic white
        'light_blue': (173, 216, 230),   # Light blue for official photos
        'light_gray': (211, 211, 211),   # Light gray
        'red': (255, 99, 99),            # Light red
        'cream': (255, 253, 240)         # Cream/ivory
    }
