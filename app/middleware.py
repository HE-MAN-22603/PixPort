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
        
        # Add cache control for static files
        if request.endpoint == 'static':
            response.headers['Cache-Control'] = 'public, max-age=3600'  # 1 hour
        elif request.endpoint and ('serve_' in request.endpoint):
            response.headers['Cache-Control'] = 'public, max-age=7200'  # 2 hours for processed files
        
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
        return jsonify({
            'error': 'Internal server error',
            'message': 'Something went wrong processing your request'
        }), 500
