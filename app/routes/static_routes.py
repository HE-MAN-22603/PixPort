"""
Static file serving routes for Railway deployment
"""

import os
from flask import Blueprint, send_file, current_app, abort

static_bp = Blueprint('static_files', __name__)

@static_bp.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files from temp directory"""
    try:
        upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(upload_path):
            return send_file(upload_path)
        else:
            abort(404)
    except Exception:
        abort(404)

@static_bp.route('/processed/<filename>')
def serve_processed(filename):
    """Serve processed files from temp directory"""
    try:
        processed_path = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        if os.path.exists(processed_path):
            return send_file(processed_path)
        else:
            abort(404)
    except Exception:
        abort(404)
