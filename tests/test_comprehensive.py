#!/usr/bin/env python3
"""
Comprehensive test script to validate all PixPort functionality
"""

import os
import sys
from app import create_app

def test_configuration():
    """Test application configuration"""
    print('\n⚙️  CONFIGURATION TEST:')
    app = create_app()
    
    secret_key = app.config.get('SECRET_KEY', '')
    print(f'SECRET_KEY length: {len(secret_key)}')
    
    max_size = app.config.get('MAX_CONTENT_LENGTH', 0)
    print(f'Max file size: {max_size / (1024*1024):.1f}MB')
    
    extensions = app.config.get('ALLOWED_EXTENSIONS', set())
    print(f'Allowed extensions: {extensions}')
    
    rate_limit = app.config.get('RATELIMIT_STORAGE_URL', 'Not set')
    print(f'Rate limit storage: {rate_limit}')
    
    return app

def test_directories(app):
    """Test directory structure"""
    print('\n📁 DIRECTORY TEST:')
    
    upload_dir = app.config.get('UPLOAD_FOLDER')
    processed_dir = app.config.get('PROCESSED_FOLDER')
    
    print(f'Upload folder: {upload_dir}')
    print(f'Processed folder: {processed_dir}')
    print(f'Upload exists: {os.path.exists(upload_dir) if upload_dir else False}')
    print(f'Processed exists: {os.path.exists(processed_dir) if processed_dir else False}')

def test_passport_config(app):
    """Test passport configuration"""
    print('\n📏 PASSPORT SIZES TEST:')
    
    passport_sizes = app.config.get('PASSPORT_SIZES', {})
    print(f'Available countries: {len(passport_sizes)}')
    
    for i, (country, size) in enumerate(passport_sizes.items()):
        if i < 5:  # Show first 5
            print(f'  {country}: {size}')

def test_background_colors(app):
    """Test background colors configuration"""
    print('\n🎨 BACKGROUND COLORS TEST:')
    
    bg_colors = app.config.get('BACKGROUND_COLORS', {})
    print(f'Available colors: {len(bg_colors)}')
    
    for color, rgb in bg_colors.items():
        print(f'  {color}: {rgb}')

def test_imports():
    """Test service imports"""
    print('\n📦 SERVICE IMPORTS TEST:')
    
    try:
        from app.services.bg_remover_lite import remove_background
        print('✅ bg_remover_lite: remove_background')
    except Exception as e:
        print(f'❌ bg_remover_lite: {e}')

    try:
        from app.services.bg_changer import smart_background_change
        print('✅ bg_changer: smart_background_change')
    except Exception as e:
        print(f'❌ bg_changer: {e}')

    try:
        from app.services.enhancer import enhance_image
        print('✅ enhancer: enhance_image')
    except Exception as e:
        print(f'❌ enhancer: {e}')

    try:
        from app.services.photo_resizer import resize_to_passport
        print('✅ photo_resizer: resize_to_passport')
    except Exception as e:
        print(f'❌ photo_resizer: {e}')

    try:
        from app.services.utils import allowed_file, validate_image_file
        print('✅ utils: utility functions')
    except Exception as e:
        print(f'❌ utils: {e}')

def test_routes(app):
    """Test route functionality"""
    print('\n🎯 ROUTE HANDLER TEST:')
    
    # Test critical route endpoints
    critical_routes = [
        '/', '/features', '/about', '/contact',
        '/health', '/status', '/ping'
    ]
    
    missing_routes = []
    existing_routes = []
    
    with app.test_client() as client:
        for route in critical_routes:
            try:
                response = client.get(route)
                if response.status_code == 404:
                    missing_routes.append(route)
                else:
                    existing_routes.append(f'{route} -> {response.status_code}')
            except Exception as e:
                missing_routes.append(f'{route} (Error: {e})')
    
    for route in existing_routes:
        print(f'✅ {route}')
    
    for route in missing_routes:
        print(f'❌ {route}')
    
    return len(existing_routes), len(missing_routes)

def test_templates():
    """Test template files"""
    print('\n🎨 TEMPLATE FILES TEST:')
    
    templates_dir = 'app/templates'
    required_templates = [
        'layout.html', 'index.html', 'preview.html', 'result.html',
        'features.html', 'about.html', 'contact.html'
    ]
    
    existing_templates = []
    missing_templates = []
    
    for template in required_templates:
        template_path = os.path.join(templates_dir, template)
        if os.path.exists(template_path):
            size = os.path.getsize(template_path)
            existing_templates.append(f'✅ {template} ({size} bytes)')
        else:
            missing_templates.append(f'❌ {template} - MISSING!')
    
    for template in existing_templates:
        print(template)
    
    for template in missing_templates:
        print(template)
    
    return len(existing_templates), len(missing_templates)

def main():
    """Run all tests"""
    print('🔍 COMPREHENSIVE PIXPORT VALIDATION')
    print('=' * 50)
    
    # Test imports first
    test_imports()
    
    # Create app and test configuration
    app = test_configuration()
    
    # Test other components
    test_directories(app)
    test_passport_config(app)
    test_background_colors(app)
    
    # Test routes
    working_routes, broken_routes = test_routes(app)
    
    # Test templates
    existing_templates, missing_templates = test_templates()
    
    print('\n📊 FINAL SUMMARY:')
    print('=' * 50)
    print(f'✅ Working Routes: {working_routes}')
    print(f'❌ Broken Routes: {broken_routes}')
    print(f'✅ Existing Templates: {existing_templates}')
    print(f'❌ Missing Templates: {missing_templates}')
    
    if broken_routes == 0 and missing_templates == 0:
        print('\n🎉 ALL TESTS PASSED - APPLICATION IS READY!')
        return 0
    else:
        print(f'\n⚠️  ISSUES FOUND - {broken_routes + missing_templates} problems to fix')
        return 1

if __name__ == '__main__':
    sys.exit(main())
