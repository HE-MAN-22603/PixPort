"""
PixPort Configuration Settings
"""

import os
from dotenv import load_dotenv
import tempfile

load_dotenv()

class Config:
    """Flask configuration class"""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pixport-secret-key-railway-2024'
    
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
    
    # Background colors (RGB)
    BACKGROUND_COLORS = {
        'white': (255, 255, 255),
        'blue': (70, 130, 180),
        'red': (220, 20, 60),
        'grey': (128, 128, 128),
        'light_blue': (230, 243, 255),  # Very light blue for passports
        'light_gray': (245, 245, 245),  # Very light gray
        'light_grey': (211, 211, 211),  # Keep for backward compatibility
        'cream': (249, 246, 240)        # Cream color
    }
