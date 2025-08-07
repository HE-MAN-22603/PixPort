# 🎯 PixPort - AI Passport Photo Maker

PixPort is a cutting-edge web application designed to help you create professional-quality passport photos with ease and accuracy. By leveraging AI technology, PixPort ensures compliance with international standards while providing tools for background removal, resizing, and photo enhancement.

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
├── 📄 Root Files
│   ├── .gitignore                  # Git ignore rules
│   ├── app.py                      # Flask entry point
│   ├── README.md                   # Project documentation
│   ├── requirements.txt            # Python dependencies
│   └── download_models.py          # AI model download script
│
├── 📦 app/                         # Main application package
│   ├── __init__.py                # Flask app factory
│   ├── config.py                  # Configuration settings
│   ├── middleware.py              # Custom middleware
│   │
│   ├── 🗺️ routes/                   # URL routing
│   │   ├── __init__.py
│   │   ├── main_routes.py         # Main page routes
│   │   └── process_routes.py      # Image processing routes
│   │
│   ├── ⚙️ services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── bg_changer.py          # Background color/image change
│   │   ├── bg_remover_lite.py     # Background removal (rembg + U²-Net)
│   │   ├── enhancer.py            # Image enhancement functions
│   │   ├── photo_resizer.py       # Resize to passport specs
│   │   └── utils.py               # Helper functions
│   │
│   ├── 🎨 static/                   # Static assets
│   │   ├── css/                    # Stylesheets
│   │   ├── js/                     # JavaScript files
│   │   ├── uploads/                # User uploaded images
│   │   └── processed/              # Final output images
│   │
│   └── 🎨 templates/                # HTML templates
│       ├── layout.html             # Base template
│       ├── index.html              # Home page
│       ├── preview.html            # Image preview page
│       └── result.html             # Result/download page
```

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

## 📊 Performance

- **Processing Time**: 2-5 seconds per image
- **Memory Usage**: ~500MB with models loaded
- **Concurrent Users**: 50+ (with proper scaling)
- **File Size Limit**: 16MB per upload

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

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
