# PixPort Tests & Development Utilities

This directory contains test files and development utilities for the PixPort application.

## Test Files

### Current/Active Tests
- **`test_download_format.py`** - Tests for download format functionality (PNG, JPEG, PDF, WEBP)

### Legacy Test Files (Moved from Root)
- `test_all_endpoints.py` - Comprehensive endpoint testing
- `test_app.py` - Basic application tests
- `test_comprehensive.py` - Comprehensive application testing
- `test_direct_download.py` - Direct download functionality tests
- `test_download.py` - Download functionality tests
- `test_fixed_app.py` - Tests for fixed application issues
- `test_image_info_fix.py` - Image information fix tests
- `test_other_api.py` - Other API endpoint tests
- `test_routes.py` - Route testing
- `test_startup.py` - Application startup tests
- `test_static.py` - Static file serving tests
- `test_urllib.py` - URL library tests
- `simple_test.py` - Simple test cases

## Development Utilities
- **`create_demo_images.py`** - Script to create demo images for testing
- **`activate_venv.bat`** - Windows batch script to activate virtual environment
- **`build.sh`** - Build script for development

## Usage Examples

### Running the Main Download Format Test
```bash
python tests/test_download_format.py
```

**Requirements:**
- Server must be running on localhost:5000
- Update the `test_filename` variable with an actual processed image filename

### Running Tests

1. **Start your PixPort server:**
   ```bash
   python app.py
   ```

2. **Run specific tests:**
   ```bash
   # Test download formats
   python tests/test_download_format.py
   ```

3. **Install test dependencies:**
   ```bash
   pip install requests pytest
   ```

## Test Categories

- **Unit Tests**: Test individual components
- **Integration Tests**: Test API endpoints  
- **Functional Tests**: Test complete workflows
- **Load Tests**: Test performance under load

## Adding New Tests

When adding new test files:

1. Use descriptive names: `test_<feature_name>.py`
2. Include proper documentation
3. Add error handling and cleanup
4. Update this README if needed

## Test Data

Test files may generate temporary data in:
- `sample_*.png`, `sample_*.jpg`, etc. (cleaned up automatically)
- Test results are logged to console

## Notes

- Tests are excluded from git via `.gitignore`
- Keep test files focused and independent
- Use the existing API endpoints for testing
