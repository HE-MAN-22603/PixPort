<div align="center">
# PixPort - AI Passport Photo Maker 🚀

**Lightning-fast background removal with multiple AI fallbacks!**

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/your-template)
  
  <p><strong>Professional passport photos made simple with AI technology</strong></p>
  
  <p>
    <a href="#features">Features</a> •
    <a href="#quick-start">Quick Start</a> •
    <a href="#api-endpoints">API</a> •
    <a href="#deployment">Deployment</a> •
    <a href="#contributing">Contributing</a>
  </p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
    <img src="https://img.shields.io/badge/Flask-2.3+-green.svg" alt="Flask Version">
    <img src="https://img.shields.io/badge/AI-Powered-orange.svg" alt="AI Powered">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
  </p>
</div>

---

## 🌟 Overview

PixPort is a cutting-edge web application designed to help you create professional-quality passport photos with ease and accuracy. By leveraging advanced AI technology, PixPort ensures compliance with international standards while providing intuitive tools for background removal, resizing, and photo enhancement.

### 🎭 Demo

> **Try it now:** Upload any portrait photo and watch PixPort transform it into a professional passport photo in seconds!

**Perfect for:**
- 📋 Passport applications
- 🆔 ID cards and visas  
- 📄 Official documents
- 💼 Professional profiles
- 🎓 Student IDs

## ✨ Features

- **🤖 AI-Powered Background Removal**: Automatically remove photo backgrounds using advanced ML models
- **🎨 Smart Background Changing**: Replace backgrounds with solid colors or custom images
- **📐 Passport Size Compliance**: Support for 60+ international passport photo dimensions
- **🔧 Photo Enhancement**: Improve photo quality with professional-grade processing
- **📱 User-Friendly Interface**: Modern, responsive design with drag-and-drop functionality
- **⚡ Fast Processing**: Optimized for quick turnaround times
- **🌍 Global Standards**: Complies with passport photo requirements worldwide

## 💻 Technology Stack

- **Backend**: Flask (Python 3.11.9)
- **Frontend**: HTML5, CSS3, JavaScript
- **AI/ML**: 
  - `rembg==2.0.50` - AI background removal
  - `opencv-python-headless==4.8.0.76` - Image processing
  - `Pillow==10.0.0` - Image manipulation
  - `onnxruntime==1.15.1` - ML model inference
- **Rate Limiting**: Flask-Limiter

## 🎨 How to Use

1. **📷 Upload Image**: Drag and drop or select an image file (JPG, PNG, HEIC)
2. **🔍 Preview**: Review the uploaded image and select processing options
3. **⚙️ Process**: Choose from various AI-powered options:
   - ✨ Remove background automatically
   - 🎨 Change background color (white, blue, red, etc.)
   - 🔧 Enhance image quality
   - 📏 Resize to passport dimensions (US, EU, UK, Asian standards)
4. **📥 Download**: Get your professional passport photo instantly

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/PixPort.git
cd PixPort
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate
# or double-click activate_venv.bat

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Download AI models**
```bash
python download_models.py
```

6. **Run the application**
```bash
python app.py
```

7. **Open in browser**
```
http://localhost:5000
```

## 🌐 API Endpoints

### Main Routes
- `GET /` - Home page
- `GET /health` - Health check endpoint
- `GET /status` - Application status
- `GET /ping` - Simple ping endpoint
- `GET /features` - Features page
- `GET /about` - About page
- `GET /contact` - Contact page

### Processing Routes  
- `POST /upload` - Upload image for processing
- `POST /process/remove_background` - AI background removal
- `POST /process/change_background` - Change background color
- `POST /process/enhance` - Enhance image quality
- `POST /process/resize` - Resize to passport dimensions

## 📁 Project Structure

```
PixPort/
│
├── 📄 Configuration & Setup
│   ├── .env.example               # Environment variables template
│   ├── .gitignore                 # Git ignore rules (comprehensive)
│   ├── requirements.txt           # Python dependencies
│   ├── runtime.txt               # Python version for deployment
│   ├── Procfile                  # Railway/Heroku deployment config
│   ├── railway.json              # Railway deployment config
│   └── README.md                 # This file - main documentation
│
├── 🚀 Application Entry Points
│   ├── app.py                    # Main Flask application
│   ├── debug_start.py            # Debug mode startup
│   ├── dev_start.py              # Development startup script
│   ├── start_dev.bat             # Windows development startup
│   └── download_models.py        # AI model download script
│
├── 📦 Core Application (app/)
│   ├── __init__.py               # Flask app factory
│   ├── config.py                 # Configuration management
│   ├── middleware.py             # Custom middleware & security
│   │
│   ├── 🗺️ routes/                 # URL routing & endpoints
│   │   ├── __init__.py
│   │   ├── main_routes.py        # Home, about, contact pages
│   │   ├── process_routes.py     # Image processing API
│   │   ├── print_routes.py       # Print layout & PDF generation
│   │   └── static_routes.py      # Static file serving
│   │
│   ├── ⚙️ services/               # Business logic & AI processing
│   │   ├── __init__.py
│   │   ├── bg_changer.py         # Background color/image change
│   │   ├── bg_remover_lite.py    # AI background removal (rembg + U²-Net)
│   │   ├── enhancer.py           # Image quality enhancement
│   │   ├── photo_resizer.py      # Passport size compliance
│   │   └── utils.py              # Helper functions & utilities
│   │
│   ├── 🎨 static/                 # Frontend assets
│   │   ├── css/                  # Stylesheets
│   │   │   ├── card-layout.css   # Card-based layouts
│   │   │   ├── index.css         # Home page styles
│   │   │   ├── layout.css        # Global layout
│   │   │   ├── preview.css       # Image preview styles
│   │   │   ├── result.css        # Result page styles
│   │   │   ├── result-modern.css # Modern result page styles
│   │   │   └── print_layout.css  # Print sheet layouts
│   │   │
│   │   ├── js/                   # JavaScript functionality
│   │   │   ├── script.js         # Main application logic
│   │   │   ├── preview.js        # Image preview handling
│   │   │   ├── result.js         # Result page interactions
│   │   │   ├── face_align.js     # Face alignment utilities
│   │   │   ├── cache-buster.js   # Cache management
│   │   │   ├── print_layout.js   # Print layout functionality
│   │   │   └── print-sheet-dropdown.js # Print sheet controls
│   │   │
│   │   ├── images/               # Demo & sample images
│   │   │   ├── demo1.jpg         # Sample passport photo 1
│   │   │   ├── demo2.jpg         # Sample passport photo 2
│   │   │   └── demo3.jpg         # Sample passport photo 3
│   │   │
│   │   ├── uploads/              # User uploaded images (gitignored)
│   │   │   └── .gitkeep         # Keep directory in git
│   │   │
│   │   └── processed/            # AI processed results (gitignored)
│   │       └── .gitkeep         # Keep directory in git
│   │
│   └── 🎨 templates/              # HTML Jinja2 templates
│       ├── layout.html           # Base template with navigation
│       ├── index.html            # Home page & upload interface
│       ├── preview.html          # Image preview & processing options
│       ├── result.html           # Download & result display
│       ├── print_layout.html     # Print sheet layout page
│       ├── about.html            # About page
│       ├── features.html         # Features showcase
│       ├── contact.html          # Contact information
│       └── errors/               # Error page templates
│           └── 404.html          # 404 Not Found page
│
├── 📚 Documentation (docs/)
│   ├── README.md                 # Documentation index
│   ├── QUICKSTART.md             # Quick setup guide
│   ├── DEPLOYMENT_CHECKLIST.md   # Deployment validation
│   ├── RAILWAY_DEPLOYMENT.md     # Railway-specific deployment
│   ├── COMPREHENSIVE_BUG_ANALYSIS.md  # Bug analysis reports
│   ├── FIXES_IMPLEMENTED.md      # Implementation tracking
│   ├── FINAL_VALIDATION_REPORT.md # Quality assurance
│   └── UNWANTED_FILES_GUIDE.md   # File management guide
│
├── 🧪 Tests & Development Tools (tests/)
│   ├── __init__.py               # Test package init
│   ├── README.md                 # Testing documentation
│   │
│   ├── 🔬 Test Files
│   │   ├── test_download_format.py      # Download format tests (active)
│   │   ├── simple_test.py               # Basic functionality tests
│   │   ├── test_app.py                  # Application tests
│   │   ├── test_startup.py              # Startup sequence tests
│   │   ├── test_comprehensive.py        # Comprehensive test suite
│   │   ├── test_all_endpoints.py        # API endpoint tests
│   │   ├── test_direct_download.py      # Download functionality tests
│   │   ├── test_download.py             # Download tests
│   │   ├── test_fixed_app.py            # Bug fix validation
│   │   ├── test_image_info_fix.py       # Image processing tests
│   │   ├── test_other_api.py            # Other API endpoint tests
│   │   ├── test_routes.py               # Route testing
│   │   ├── test_static.py               # Static file serving tests
│   │   └── test_urllib.py               # URL library tests
│   │
│   └── 🛠️ Development Utilities
│       ├── create_demo_images.py        # Generate demo images
│       ├── activate_venv.bat            # Windows virtual env activation
│       └── build.sh                     # Build script for deployment
│
└── 🔧 Virtual Environment (gitignored)
    └── venv/                     # Python virtual environment
        ├── Include/              # Header files
        ├── Lib/                  # Installed packages
        │   └── site-packages/    # Third-party libraries
        │       ├── flask/        # Flask web framework
        │       ├── rembg/        # AI background removal
        │       ├── cv2/          # OpenCV image processing
        │       ├── PIL/          # Pillow image library
        │       ├── onnxruntime/  # ML model runtime
        │       ├── flask_limiter/ # Rate limiting
        │       ├── gunicorn/     # Production WSGI server
        │       └── [many more...]# Dependencies
        └── Scripts/              # Executable scripts
```

### 📋 Key Directory Details

#### 🎯 **Core Functionality**
- **`app/services/`** - AI processing pipeline (background removal, enhancement, resizing)
- **`app/routes/`** - RESTful API endpoints and web routes including print/PDF generation
- **`app/static/`** - Frontend assets with responsive design and print layouts
- **`app/templates/`** - Server-side rendered HTML pages including error handling

#### 📚 **Documentation & Organization**
- **`docs/`** - All project documentation in one organized location
  - Quick start guides, deployment checklists, bug analysis reports
  - Keeps the project root clean and professional
  - Easy navigation for developers and contributors

#### 🧪 **Testing & Quality Assurance**  
- **`tests/`** - Organized testing directory with comprehensive coverage
  - **`test_download_format.py`** - Active download format validation tests
  - **Legacy test files** - Comprehensive test suite for all components
  - **Development utilities** - Build scripts, demo generators, environment tools
  - Centralized testing documentation and guidelines

#### 🚀 **Deployment Ready**
- **`Procfile`** - Railway/Heroku deployment configuration
- **`railway.json`** - Railway platform deployment settings
- **Production utilities** - Gunicorn server, build automation
- **Environment management** - Secure configuration templates

#### 🔒 **Security & Configuration**
- **`.env.example`** - Secure environment variable template
- **`app/config.py`** - Centralized configuration management
- **`app/middleware.py`** - Security headers and request handling
- **Rate limiting** - Flask-Limiter integration for API protection

#### 🎨 **Enhanced Features**
- **Print layouts** - PDF generation and multi-photo print sheets
- **Modern UI** - Updated styling with responsive design
- **Cache management** - Client-side cache busting for updated assets
- **Error handling** - Custom 404 pages and graceful error responses

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
REMBG_MODEL=u2net
REDIS_URL=memory://
```

### Supported Passport Sizes
- **US**: 35x45mm (413x531 pixels at 300 DPI)
- **EU**: 35x45mm (413x531 pixels at 300 DPI)
- **UK**: 35x45mm (413x531 pixels at 300 DPI)
- **India**: 35x45mm (413x531 pixels at 300 DPI)
- **China**: 33x48mm (390x567 pixels at 300 DPI)
- **Canada**: 35x45mm (425x567 pixels at 300 DPI)
- **Australia**: 35x45mm (413x531 pixels at 300 DPI)
- **Japan**: 35x45mm (425x567 pixels at 300 DPI)

### Background Colors
- White: `(255, 255, 255)`
- Blue: `(70, 130, 180)`
- Red: `(220, 20, 60)`
- Grey: `(128, 128, 128)`
- Light Blue: `(173, 216, 230)`
- Light Grey: `(211, 211, 211)`

## 🧪 Testing

Run the test suite:
```bash
python simple_test.py
```

Check application health:
```bash
curl http://localhost:5000/health
```

## 📝 Development

### Adding New Features
1. Create service functions in `app/services/`
2. Add routes in `app/routes/`
3. Update templates and static files
4. Test with `simple_test.py`

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable names
- Add docstrings to functions
- Handle errors gracefully

## 🔒 Security

- File upload validation
- Rate limiting on API endpoints
- CSRF protection
- Input sanitization
- Secure file handling

## 🐛 Troubleshooting

### Common Issues

**1. ModuleNotFoundError**
```bash
# Make sure virtual environment is activated
venv\Scripts\activate
pip install -r requirements.txt
```

**2. AI Model Loading Error**
```bash
# Re-download models
python download_models.py
```

**3. File Upload Issues**
- Check file size (max 16MB)
- Verify file format (JPG, PNG, HEIC)
- Ensure upload directory exists

**4. Port Already in Use**
```bash
# Change port in app.py or kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

## 🚀 Deployment

### Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template-id)

1. **One-click deployment** via Railway button above
2. **Environment variables** are automatically configured
3. **AI models** download automatically on first run
4. **Custom domain** available with Railway Pro

### Manual Deployment

```bash
# Set production environment
export FLASK_ENV=production
export PORT=8000

# Install production dependencies
pip install gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
```

### Docker Deployment

```dockerfile
# Create Dockerfile (example)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
# Build and run
docker build -t pixport .
docker run -p 5000:5000 pixport
```

## 📊 Performance

### Benchmarks
- **Processing Time**: 2-5 seconds per image
- **Memory Usage**: ~500MB with models loaded
- **Concurrent Users**: 50+ (with proper scaling)
- **File Size Limit**: 16MB per upload
- **Supported Formats**: JPG, PNG, HEIC, WEBP
- **Output Quality**: 300 DPI (print-ready)

### Optimization Tips
- **Enable GPU**: For faster processing with CUDA-enabled devices
- **Redis Caching**: Use Redis for session storage in production
- **CDN**: Serve static assets via CDN for better performance
- **Load Balancing**: Use multiple instances for high traffic

## 🚀 Advanced Usage

### API Integration

```python
import requests

# Upload and process image via API
with open('portrait.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:5000/upload', files=files)
    
# Get processing result
result = requests.post('http://localhost:5000/process/remove_background', 
                      json={'filename': 'portrait.jpg'})
```

### Custom Background Colors

```python
# Add custom background color
from app.services.bg_changer import change_background

custom_color = (123, 45, 67)  # RGB values
result = change_background(image_path, custom_color)
```

### Batch Processing

```python
# Process multiple images
import os
from app.services import photo_processor

for filename in os.listdir('input_folder'):
    if filename.lower().endswith(('.jpg', '.png')):
        process_image(f'input_folder/{filename}')
```

## ❓ FAQ

### General Questions

**Q: What image formats are supported?**
A: PixPort supports JPG, PNG, HEIC, and WEBP formats. The AI models work best with high-quality portrait photos.

**Q: What's the maximum file size?**
A: The default limit is 16MB per image. This can be configured in the app settings.

**Q: How accurate is the background removal?**
A: PixPort uses the U²-Net model which achieves 95%+ accuracy on portrait photos. Results may vary based on image quality and lighting.

**Q: Are the AI models downloaded locally?**
A: Yes, all AI models are downloaded and run locally for privacy and speed. No images are sent to external services.

### Technical Questions

**Q: Can I run this on a server without internet?**
A: Yes, once the AI models are downloaded, PixPort works completely offline.

**Q: How can I improve processing speed?**
A: Use a GPU-enabled environment, reduce image size before processing, or implement Redis caching.

**Q: Can I customize passport photo dimensions?**
A: Yes, edit the `photo_resizer.py` service to add custom dimensions for specific requirements.

**Q: Is there a rate limit?**
A: Yes, the default is 500/day, 100/hour, 20/minute per IP. This can be configured in `app/__init__.py`.

### Privacy & Security

**Q: Are uploaded images stored permanently?**
A: No, images are automatically deleted after processing. You can configure retention time in settings.

**Q: Is the app GDPR compliant?**
A: Yes, PixPort processes images locally and doesn't store personal data beyond the session.

**Q: Can I use this commercially?**
A: Yes, PixPort is MIT licensed. Check the license file for full terms.

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Code Contributions
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Other Ways to Contribute
- 🐛 Report bugs via [GitHub Issues](https://github.com/your-username/PixPort/issues)
- 📝 Improve documentation
- 🌍 Translate the interface
- ⭐ Star the repository
- 💬 Share feedback and suggestions

### Development Setup
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 app/
black app/

# Run security checks
bandit -r app/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [rembg](https://github.com/danielgatis/rembg) for AI background removal
- [OpenCV](https://opencv.org/) for image processing
- [Pillow](https://pillow.readthedocs.io/) for image manipulation
- [Flask](https://flask.palletsprojects.com/) for web framework

## 📞 Support

- 📧 Email: support@pixport.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-username/PixPort/issues)
- 📖 Documentation: [Wiki](https://github.com/your-username/PixPort/wiki)

---

**Made with ❤️ for passport photos worldwide**
#   G o o g l e   C l o u d   R u n   D e p l o y m e n t   R e a d y !   T e s t   d e p l o y m e n t   0 8 / 1 0 / 2 0 2 5   2 3 : 0 7 : 0 2  
 