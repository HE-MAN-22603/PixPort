# 🎨 PixPort ISNet Tiny - Ultra-Lightweight Background Removal

An ultra-lightweight background removal service optimized for Railway's 512MB memory limit. Uses **ONLY** the `isnet-general-tiny` ONNX model for maximum efficiency.

## 🚀 Features

- **Memory Optimized**: Runs in <200MB RAM (well under Railway's 512MB limit)
- **Single Model**: Uses only `isnet-general-tiny` ONNX model - no fallbacks, no bloat
- **Two Operations**: Background removal (transparent) and background color change
- **Railway Ready**: Containerized deployment with health checks
- **Fast Processing**: ONNX Runtime with CPU optimizations
- **Auto-Resizing**: Images auto-resized to 1024px max for memory safety
- **Real-time Monitoring**: Memory usage and health endpoints

## 📊 Memory Usage Breakdown

```
- Base Python runtime: ~50MB
- Flask + dependencies: ~20MB  
- ONNX Runtime (CPU): ~40MB
- ISNet model: ~40MB
- PIL/Pillow: ~15MB
- NumPy: ~20MB
- Working memory: ~50MB
Total: ~235MB (54% of Railway limit)
```

## 🛠️ Quick Start

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements-isnet-tiny.txt
```

2. **Run the service:**
```bash
python app_isnet_tiny.py
```

3. **Access the service:**
- API Documentation: http://localhost:5000/
- Health Check: http://localhost:5000/api/bg/health
- Status: http://localhost:5000/api/bg/status

### Railway Deployment

1. **Deploy to Railway:**
```bash
# Using Railway CLI
railway login
railway init
railway up
```

2. **Or use the Dockerfile:**
```bash
# Build the image
docker build -f Dockerfile.isnet-tiny -t pixport-isnet-tiny .

# Run locally
docker run -p 8080:8080 pixport-isnet-tiny
```

## 🔧 API Endpoints

### Remove Background
```bash
curl -X POST -F "file=@image.jpg" \
  https://your-app.railway.app/api/bg/remove \
  -o result.png
```

### Change Background Color
```bash
# Hex color
curl -X POST -F "file=@image.jpg" -F "color=#00FF00" \
  https://your-app.railway.app/api/bg/change_color \
  -o green_bg.jpg

# RGB color  
curl -X POST -F "file=@image.jpg" -F "color=255,0,0" \
  https://your-app.railway.app/api/bg/change_color \
  -o red_bg.jpg
```

### Health & Status
```bash
# Health check
curl https://your-app.railway.app/api/bg/health

# Service status
curl https://your-app.railway.app/api/bg/status

# Clear cache (if needed)
curl -X POST https://your-app.railway.app/api/bg/clear_cache
```

## 📝 API Response Examples

### Background Removal Success
```http
POST /api/bg/remove
Content-Type: multipart/form-data

HTTP/1.1 200 OK
Content-Type: image/png
Content-Disposition: attachment; filename="nobg_image.png"

[PNG data with transparent background]
```

### Status Response
```json
{
  "status": "ready",
  "model": "isnet-general-tiny",
  "memory": {
    "rss_mb": 185.2,
    "model_loaded": true
  },
  "max_file_size_mb": 8,
  "max_dimension": 1024,
  "allowed_extensions": ["png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp"]
}
```

### Health Check Response
```json
{
  "status": "healthy",
  "memory_mb": 185.2,
  "model_loaded": true
}
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Server port |
| `UPLOAD_FOLDER` | `/tmp/uploads` | Upload directory |
| `PROCESSED_FOLDER` | `/tmp/processed` | Output directory |
| `SECRET_KEY` | `isnet-tiny-railway-key` | Flask secret key |
| `FLASK_ENV` | `production` | Flask environment |

### Service Limits

| Limit | Value | Reason |
|-------|-------|--------|
| Max file size | 8MB | Railway memory constraints |
| Max image dimension | 1024px | Memory optimization |
| Processing timeout | 60s | Railway request timeout |
| Model memory limit | 150MB | Conservative ONNX limit |

## 🧪 Testing

### Run Tests
```bash
# Test the service directly
python test_isnet_tiny.py
```

### Manual Testing
```bash
# 1. Start the service
python app_isnet_tiny.py

# 2. Test with curl
curl -X POST -F "file=@test_image.jpg" \
  http://localhost:5000/api/bg/remove \
  -o test_output.png

# 3. Check the result
file test_output.png
```

## 📦 File Structure

```
PixPort/
├── app_isnet_tiny.py              # Standalone Flask app
├── requirements-isnet-tiny.txt    # Minimal dependencies
├── Dockerfile.isnet-tiny          # Railway deployment
├── test_isnet_tiny.py            # Test suite
├── README-isnet-tiny.md          # This file
└── app/
    ├── services/
    │   └── isnet_tiny_service.py  # Core service
    └── api/
        └── bg_removal_api.py      # Flask API
```

## 🔍 Technical Details

### Model Information
- **Model**: `isnet-general-tiny` from rembg
- **Format**: ONNX (CPU optimized)
- **Size**: ~40MB
- **Input**: 1024x1024 RGB images
- **Output**: Binary mask for background removal

### ONNX Optimization
```python
# Memory-optimized session options
sess_options.intra_op_num_threads = 1
sess_options.graph_optimization_level = ORT_ENABLE_ALL
sess_options.enable_mem_pattern = False
sess_options.enable_cpu_mem_arena = False
```

### Image Processing Pipeline
1. **Load & Validate**: Check file size and format
2. **Resize**: Auto-resize to max 1024px if needed
3. **Preprocess**: Convert to ONNX input format (CHW, normalized)
4. **Inference**: Run ISNet model to get mask
5. **Postprocess**: Apply mask to create transparent PNG
6. **Cleanup**: Aggressive memory cleanup after processing

## 🚨 Troubleshooting

### Common Issues

**1. Out of Memory Errors**
```bash
# Check memory usage
curl localhost:5000/api/bg/status

# Clear cache if needed
curl -X POST localhost:5000/api/bg/clear_cache
```

**2. Model Download Issues**
```bash
# The model downloads automatically on first use
# Check logs for download progress
docker logs <container_id>
```

**3. Large Image Processing**
- Images >1024px are automatically resized
- Files >8MB are rejected
- Use smaller images for better performance

### Railway-Specific Issues

**Memory Limit Exceeded:**
- Monitor `/api/bg/health` endpoint
- Consider reducing max file size
- Use Railway's monitoring dashboard

**Cold Starts:**
- First request may take longer (model loading)
- Health check endpoint prevents cold starts
- Model is pre-cached in Docker image

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Test with `python test_isnet_tiny.py`
4. Ensure memory usage stays under 200MB
5. Submit a pull request

## 📄 License

MIT License - feel free to use this for your Railway deployments!

## 🔗 Related

- [ISNet Paper](https://arxiv.org/abs/2112.13465)
- [rembg Library](https://github.com/danielgatis/rembg)
- [Railway Deployment Docs](https://docs.railway.app/)
- [ONNX Runtime](https://onnxruntime.ai/)

---

**Note**: This service is specifically optimized for Railway's 512MB memory limit. For higher-capacity deployments, consider the full PixPort service with multiple model fallbacks.
