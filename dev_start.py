#!/usr/bin/env python3
"""
Development startup script for PixPort with hot reload
Bypasses AI model loading for faster development
"""

import os
import sys

# Set development environment variables
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = '1'

# Disable AI model preloading during development
os.environ['SKIP_AI_MODELS'] = '1'

# Add cache busting for development
os.environ['DEVELOPMENT_MODE'] = '1'

print("🔧 PixPort Development Server")
print("=" * 50)
print("🌍 Mode: Development (Hot Reload Enabled)")
print("🤖 AI Models: Skip preload (loaded on demand)")
print("🔄 Cache: Disabled for development")
print("🐛 Debug: Enabled")

try:
    from app import create_app
    
    app = create_app()
    
    # Ensure debug mode and reloader are enabled
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Disable static file caching
    app.config['TEMPLATES_AUTO_RELOAD'] = True   # Auto reload templates
    
    port = int(os.environ.get('PORT', 5000))
    
    print(f"\n🚀 Starting development server on port {port}")
    print(f"🔗 Local URL: http://127.0.0.1:{port}")
    print(f"🔗 Network URL: http://0.0.0.0:{port}")
    print("\n✅ Server ready! Changes will auto-reload.")
    print("=" * 50)
    
    # Enable auto-reload and debug mode
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True,
        use_reloader=True,
        use_debugger=True,
        threaded=True
    )
    
except Exception as e:
    print(f"❌ Failed to start development server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
