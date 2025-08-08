"""
PixPort Flask Application Factory
"""

import os
import time
from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config
from .middleware import setup_middleware

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Initialize configuration with validation
    config = Config()
    app.config.from_object(config)
    
    # Initialize rate limiter with user-friendly limits
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[
            "500 per day",          # Daily limit - generous for normal usage
            "100 per hour",         # Hourly limit - prevents sustained abuse
            "20 per minute"         # Per-minute limit - allows bursts but prevents spam
        ],
        storage_uri=app.config.get('RATELIMIT_STORAGE_URL', 'memory://'),
        strategy='moving-window'  # More forgiving strategy
    )
    limiter.init_app(app)
    
    # Custom error handler for rate limits
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            'error': 'Rate limit exceeded',
            'message': 'You have made too many requests. Please wait a moment before trying again.',
            'retry_after': getattr(e, 'retry_after', None)
        }), 429
    
    # Setup custom middleware
    setup_middleware(app)
    
    # Add cache busting template context
    @app.context_processor
    def inject_cache_buster():
        """Inject cache busting functions into templates"""
        def get_file_version(filepath):
            """Get file modification time for cache busting"""
            try:
                static_path = os.path.join(app.static_folder, filepath)
                if os.path.exists(static_path):
                    return str(int(os.path.getmtime(static_path)))
                else:
                    # Fallback to current time if file doesn't exist
                    return str(int(time.time()))
            except (OSError, TypeError):
                # Fallback to current time on any error
                return str(int(time.time()))
        
        def versioned_url_for(endpoint, **values):
            """Generate URL with automatic cache busting"""
            if endpoint == 'static':
                filename = values.get('filename')
                if filename:
                    version = get_file_version(filename)
                    from flask import url_for
                    url = url_for(endpoint, **values)
                    return f"{url}?v={version}"
            from flask import url_for
            return url_for(endpoint, **values)
        
        return dict(
            get_file_version=get_file_version,
            versioned_url_for=versioned_url_for
        )
    
    # Register blueprints
    from .routes.main_routes import main_bp
    from .routes.process_routes import process_bp
    from .routes.static_routes import static_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(process_bp, url_prefix='/process')
    app.register_blueprint(static_bp, url_prefix='/static')
    
    # Ensure upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    
    return app
