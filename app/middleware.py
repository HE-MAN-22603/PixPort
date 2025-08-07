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
        """Execute after each request"""
        # Add CORS headers for API endpoints
        if request.endpoint and 'process' in request.endpoint:
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        
        # Add processing time header
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            response.headers.add('X-Response-Time', f"{duration:.3f}s")
        
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
