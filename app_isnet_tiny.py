"""
Standalone Flask App for Ultra-Lightweight Background Removal
Uses ONLY isnet-general-tiny model - optimized for Railway 512MB deployment
"""

import os
import logging
from flask import Flask, request, jsonify, render_template_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask app for Railway deployment"""
    app = Flask(__name__)
    
    # Configuration for Railway
    app.config.update(
        MAX_CONTENT_LENGTH=8 * 1024 * 1024,  # 8MB max file size
        SECRET_KEY=os.environ.get('SECRET_KEY', 'isnet-tiny-railway-key'),
        UPLOAD_FOLDER=os.environ.get('UPLOAD_FOLDER', '/tmp/uploads'),
        PROCESSED_FOLDER=os.environ.get('PROCESSED_FOLDER', '/tmp/processed'),
    )
    
    # Ensure directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    
    # Register API blueprint
    from app.api.bg_removal_api import bg_api
    app.register_blueprint(bg_api)
    
    # Simple landing page
    @app.route('/')
    def index():
        return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>PixPort ISNet Tiny - Background Removal</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .container { background: #f5f5f5; padding: 30px; border-radius: 10px; }
        .endpoint { background: white; margin: 10px 0; padding: 15px; border-radius: 5px; }
        .method { color: white; padding: 5px 10px; border-radius: 3px; font-weight: bold; }
        .post { background: #28a745; }
        .get { background: #007bff; }
        code { background: #f8f9fa; padding: 2px 6px; border-radius: 3px; }
        .memory-info { background: #e7f3ff; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .status { margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 PixPort ISNet Tiny</h1>
        <p><strong>Ultra-lightweight background removal service</strong></p>
        <p>Optimized for Railway 512MB deployment using <em>only</em> the isnet-general-tiny ONNX model.</p>
        
        <div class="status">
            <h3>📊 Service Status</h3>
            <div id="status">Loading...</div>
        </div>
        
        <h3>🚀 API Endpoints</h3>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/bg/remove</strong>
            <p>Remove background from image (returns PNG with transparent background)</p>
            <p><strong>Form Data:</strong> <code>file</code> - Image file to process</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/bg/change_color</strong>
            <p>Remove background and replace with solid color</p>
            <p><strong>Form Data:</strong> <code>file</code> - Image file, <code>color</code> - Hex color (#FF0000) or RGB (255,0,0)</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/bg/status</strong>
            <p>Get service status and configuration</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span> <strong>/api/bg/health</strong>
            <p>Health check endpoint</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <strong>/api/bg/clear_cache</strong>
            <p>Clear model cache (for debugging/recovery)</p>
        </div>
        
        <h3>📋 Usage Examples</h3>
        <pre><code># Remove background
curl -X POST -F "file=@image.jpg" {{host}}/api/bg/remove -o result.png

# Change background color
curl -X POST -F "file=@image.jpg" -F "color=#00FF00" {{host}}/api/bg/change_color -o green_bg.jpg

# Check status  
curl {{host}}/api/bg/status</code></pre>
        
        <div class="memory-info">
            <h4>💾 Memory Optimization</h4>
            <ul>
                <li>Maximum file size: 8MB</li>
                <li>Maximum image dimension: 1024px (auto-resized)</li>
                <li>Target memory usage: <200MB RAM</li>
                <li>Model: isnet-general-tiny ONNX (CPU-only)</li>
            </ul>
        </div>
        
        <p><small>Powered by ISNet Tiny • Railway Optimized • <a href="https://github.com/danielgatis/rembg">rembg</a> compatible</small></p>
    </div>
    
    <script>
    // Load status
    fetch('/api/bg/status')
        .then(response => response.json())
        .then(data => {
            const statusDiv = document.getElementById('status');
            if (data.status === 'ready') {
                statusDiv.innerHTML = `
                    <div style="color: green;">✅ Service Ready</div>
                    <div>Model: ${data.model}</div>
                    <div>Memory: ${data.memory.rss_mb ? data.memory.rss_mb.toFixed(1) + 'MB' : 'N/A'}</div>
                    <div>Model Loaded: ${data.memory.model_loaded ? 'Yes' : 'No'}</div>
                `;
            } else {
                statusDiv.innerHTML = '<div style="color: red;">❌ Service Error</div>';
            }
        })
        .catch(error => {
            document.getElementById('status').innerHTML = '<div style="color: orange;">⚠️ Status Check Failed</div>';
        });
    
    // Replace host placeholder
    document.querySelectorAll('code').forEach(code => {
        code.innerHTML = code.innerHTML.replace('{{host}}', window.location.origin);
    });
    </script>
</body>
</html>
        ''')
    
    # Error handlers
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'error': 'File too large. Maximum 8MB allowed for Railway deployment.'
        }), 413
    
    @app.errorhandler(500)
    def internal_server_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            'error': 'Internal server error. Check logs for details.'
        }), 500
    
    return app

# Create app instance
app = create_app()

if __name__ == '__main__':
    # Development server
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    )
