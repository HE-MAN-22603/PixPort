"""
Custom middleware for PixPort
"""

from flask import request, jsonify
import time

def setup_middleware(app):
    """Setup custom middleware for the Flask app"""
    
    @app.before_request
    def before_request():
        """Execute before each request"""
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        """Execute after each request with security headers"""
        # Add comprehensive security headers
        response.headers.add('X-Content-Type-Options', 'nosniff')
        response.headers.add('X-Frame-Options', 'DENY')
        response.headers.add('X-XSS-Protection', '1; mode=block')
        response.headers.add('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.add('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        
        # Add Content Security Policy
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none'"
        )
        response.headers.add('Content-Security-Policy', csp_policy)
        
        # Add CORS headers for API endpoints only
        if request.endpoint and ('process' in request.endpoint or 'api' in request.endpoint):
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
            response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        
        # Add processing time header
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response.headers.add('X-Response-Time', f"{duration:.3f}s")
        
        # Comprehensive cache control with aggressive cache busting
        if request.endpoint == 'static' or '/static/' in request.path:
            # Static files (CSS, JS) - aggressive cache busting
            if any(ext in request.path for ext in ['.css', '.js']):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
                response.headers['ETag'] = f'"pixport-{int(time.time())}-{hash(str(request.path))}"'
            # Images and other assets - short cache with validation
            elif any(ext in request.path for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2']):
                response.headers['Cache-Control'] = 'public, max-age=300, must-revalidate'  # 5 minutes
                response.headers['ETag'] = f'"pixport-asset-{int(time.time())}"'
            else:
                response.headers['Cache-Control'] = 'no-cache, must-revalidate'
                response.headers['ETag'] = f'"pixport-{int(time.time())}"'
        elif request.endpoint and ('serve_' in request.endpoint):
            # Processed images - short cache
            response.headers['Cache-Control'] = 'private, max-age=300, must-revalidate'  # 5 minutes
        else:
            # HTML pages and API responses - no caching whatsoever
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            response.headers['Last-Modified'] = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime())
        
        return response
    
    @app.errorhandler(413)
    def file_too_large(error):
        """Handle file too large error"""
        return jsonify({
            'error': 'File too large',
            'message': 'Maximum file size is 16MB'
        }), 413
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handle bad request error"""
        return jsonify({
            'error': 'Bad request',
            'message': str(error.description)
        }), 400
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle internal server error"""
        import traceback
        # Log the actual error
        app.logger.error(f"500 error: {str(error)}")
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'error': 'Download failed',
            'message': 'An error occurred while preparing your download. Please try again.'
        }), 500
