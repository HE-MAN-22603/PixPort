# PixPort - Quick Start Guide

## 🚀 Getting Started

### 1. Virtual Environment Setup ✅ COMPLETED
Your virtual environment has been created and all dependencies are installed!

### 2. AI Models ✅ DOWNLOADED
AI models for background removal have been downloaded and are ready to use.

### 3. Application Test ✅ PASSED
All core functionality has been tested and is working correctly.

## 🏃‍♂️ How to Run PixPort

### Option 1: Using the Activation Script
```bash
# Double-click on activate_venv.bat
# Then run: python app.py
```

### Option 2: Command Line
```bash
# Activate virtual environment
venv\Scripts\activate

# Start the Flask server
python app.py
```

### Option 3: Development Mode
```bash
# Activate virtual environment
venv\Scripts\activate

# Set environment variables
set FLASK_ENV=development
set FLASK_DEBUG=1

# Start the server
python app.py
```

## 🌐 Access the Application

Once running, open your browser and go to:
- **http://localhost:5000** - Main application
- **http://localhost:5000/health** - Health check
- **http://localhost:5000/status** - System status

## 📁 Project Structure

```
PixPort/
├── 📄 app.py                  # Flask entry point
├── 📄 requirements.txt        # Dependencies ✅ INSTALLED
├── 📄 download_models.py      # AI models ✅ DOWNLOADED
├── 📁 venv/                   # Virtual environment ✅ CREATED
├── 📁 app/
│   ├── __init__.py           # Flask factory
│   ├── config.py             # Configuration
│   ├── middleware.py         # Middleware
│   ├── routes/               # URL routes
│   ├── services/             # AI processing
│   ├── static/               # CSS, JS, uploads
│   └── templates/            # HTML templates
└── 📄 activate_venv.bat       # Quick activation
```

## ✨ Available Features

### API Endpoints
- `POST /process/upload` - Upload image files
- `POST /process/remove_background` - AI background removal
- `POST /process/change_background` - Change background color
- `POST /process/enhance` - Image enhancement
- `POST /process/resize` - Resize to passport dimensions

### AI Capabilities
- 🤖 **Background Removal** - Using rembg with U²-Net models
- 🎨 **Background Changing** - Solid colors and gradients
- 🔧 **Photo Enhancement** - Brightness, contrast, sharpness
- 📐 **Passport Sizing** - Multiple country standards
- 🖼️ **Face Detection** - Smart cropping and positioning

### Supported Formats
- **Input**: JPG, PNG, HEIC, WebP (up to 16MB)
- **Output**: High-quality JPEG with 300 DPI
- **Countries**: US, EU, UK, India, China, Canada, Australia, Japan

## 🔧 Next Steps

To complete the frontend, you still need to create:

1. **CSS Files** (in `app/static/css/`):
   - `layout.css` - Base layout styles
   - `index.css` - Home page styles
   - `preview.css` - Preview page styles
   - `result.css` - Result page styles

2. **JavaScript Files** (in `app/static/js/`):
   - `script.js` - General functionality
   - `preview.js` - Preview interactions
   - `result.js` - Result page logic
   - `face_align.js` - Face alignment

3. **HTML Templates** (in `app/templates/`):
   - `preview.html` - Image preview page
   - `result.html` - Download/result page

## 🆘 Troubleshooting

### If the server won't start:
1. Make sure virtual environment is activated
2. Check that all dependencies are installed: `pip list`
3. Run the test script: `python simple_test.py`

### If AI processing fails:
1. Verify models are downloaded: `python download_models.py`
2. Check upload/processed directories exist
3. Ensure input images are valid format and size

## 📞 Support

The application includes comprehensive error handling and logging.
Check the console output for detailed error messages.

---

**🎉 Congratulations! PixPort is ready to create amazing passport photos!**
