"""
PixPort Flask Application Factory
"""

import os
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config
from .middleware import setup_middleware

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    limiter.init_app(app)
    
    # Setup custom middleware
    setup_middleware(app)
    
    # Register blueprints
    from .routes.main_routes import main_bp
    from .routes.process_routes import process_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(process_bp, url_prefix='/process')
    
    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    
    return app
