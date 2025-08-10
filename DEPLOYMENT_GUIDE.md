# 🚀 PixPort Deployment Guide

Complete deployment guide for both the full PixPort application and the ultra-lightweight ISNet Tiny background removal service.

## 📋 Pre-Deployment Checklist

### ✅ Files Ready for Deployment

**Core Application Files:**
- [x] `app.py` - Main Flask application
- [x] `wsgi.py` - WSGI entry point
- [x] `gunicorn.conf.py` - Production server config
- [x] `requirements.txt` - Updated dependencies
- [x] `.gitignore` - Clean project structure

**ISNet Tiny Service Files:**
- [x] `app_isnet_tiny.py` - Lightweight Flask app
- [x] `app/services/isnet_tiny_service.py` - Core service
- [x] `app/api/bg_removal_api.py` - API endpoints
- [x] `requirements-isnet-tiny.txt` - Minimal dependencies
- [x] `Dockerfile.isnet-tiny` - Container config
- [x] `test_isnet_tiny.py` - Test suite
- [x] `README-isnet-tiny.md` - Service documentation

**Deployment Configuration:**
- [x] `railway.toml` - Railway deployment config
- [x] `Procfile` - Alternative deployment method

## 🎯 Deployment Options

### Option 1: Full PixPort Application (Default)
**Memory Usage:** ~350MB peak  
**Features:** Complete passport photo processing + background removal  
**Models:** Multiple model fallbacks (u2net, u2netp, isnet-general-use)

### Option 2: ISNet Tiny Service (Memory Optimized)
**Memory Usage:** ~235MB peak  
**Features:** Background removal + color change only  
**Models:** Single isnet-general-tiny ONNX model

---

## 🚄 Railway Deployment

### Quick Start (Default - Full App)

1. **Install Railway CLI:**
```bash
npm install -g @railway/cli
# or
curl -fsSL https://railway.app/install.sh | sh
```

2. **Login and Deploy:**
```bash
railway login
railway link  # Link to existing project or create new
railway up
```

### ISNet Tiny Service Deployment

To deploy the ultra-lightweight service instead:

1. **Update railway.toml:**
```bash
# Edit railway.toml and change the startCommand to:
startCommand = "python app_isnet_tiny.py"
```

2. **Deploy:**
```bash
railway up
```

### Environment-Specific Deployment

**For ISNet Tiny service with separate environment:**

1. **Create ISNet environment:**
```bash
railway environments:create isnet-tiny
railway environment:use isnet-tiny
```

2. **Set environment variables:**
```bash
railway variables:set FLASK_APP=app_isnet_tiny.py
railway variables:set REMBG_MODEL=isnet-general-tiny
railway variables:set MAX_CONTENT_LENGTH=8388608
```

3. **Deploy:**
```bash
railway up
```

### Memory Optimization for Railway

**Environment variables for better memory management:**
```bash
railway variables:set MALLOC_ARENA_MAX=2
railway variables:set MALLOC_MMAP_THRESHOLD_=131072
railway variables:set MALLOC_TRIM_THRESHOLD_=131072
railway variables:set PYTHONUNBUFFERED=1
railway variables:set PYTHONDONTWRITEBYTECODE=1
```

---

## 🐳 Docker Deployment

### ISNet Tiny Service

1. **Build the container:**
```bash
docker build -f Dockerfile.isnet-tiny -t pixport-isnet-tiny .
```

2. **Run locally:**
```bash
docker run -p 8080:8080 pixport-isnet-tiny
```

3. **Deploy to any container platform:**
```bash
# Example: Deploy to Railway using Docker
railway deploy --dockerfile Dockerfile.isnet-tiny
```

### Full PixPort App

1. **Build with default Dockerfile:**
```bash
docker build -t pixport-full .
```

2. **Run with memory limits:**
```bash
docker run -p 5000:5000 --memory=512m pixport-full
```

---

## 🔧 Configuration Guide

### Main App Configuration (`app.py`)

**Environment Variables:**
- `PORT` - Server port (default: 5000)
- `FLASK_ENV` - Environment (production/development)
- `UPLOAD_FOLDER` - Upload directory
- `PROCESSED_FOLDER` - Output directory
- `REMBG_MODEL` - Background removal model
- `MAX_CONTENT_LENGTH` - Max file size

### ISNet Tiny Service Configuration

**Environment Variables:**
- `PORT` - Server port (default: 5000)
- `FLASK_APP` - App file (app_isnet_tiny.py)
- `UPLOAD_FOLDER` - Upload directory (/tmp/uploads)
- `PROCESSED_FOLDER` - Output directory (/tmp/processed)
- `SECRET_KEY` - Flask secret key

**Memory Limits:**
- Max file size: 8MB
- Max image dimension: 1024px
- Model memory limit: 150MB
- Total target: <235MB

---

## 📊 Performance Comparison

| Metric | Full PixPort | ISNet Tiny |
|--------|--------------|------------|
| **Memory (Peak)** | ~350MB | ~235MB |
| **Memory (Idle)** | ~180MB | ~120MB |
| **Docker Size** | ~800MB | ~600MB |
| **Startup Time** | ~30s | ~15s |
| **Processing Speed** | Fast | Very Fast |
| **Model Flexibility** | High | Fixed |
| **Features** | Complete | BG Only |

---

## 🧪 Testing Deployments

### Local Testing

**Full App:**
```bash
python app.py
curl http://localhost:5000/health
```

**ISNet Tiny:**
```bash
python app_isnet_tiny.py
curl http://localhost:5000/api/bg/health
```

### Production Testing

**Health Checks:**
```bash
# Full app
curl https://your-app.railway.app/health

# ISNet Tiny
curl https://your-app.railway.app/api/bg/health
```

**Memory Monitoring:**
```bash
# ISNet Tiny memory status
curl https://your-app.railway.app/api/bg/status
```

**API Testing:**
```bash
# Background removal
curl -X POST -F "file=@test.jpg" \
  https://your-app.railway.app/api/bg/remove \
  -o result.png

# Color change
curl -X POST -F "file=@test.jpg" -F "color=#00FF00" \
  https://your-app.railway.app/api/bg/change_color \
  -o green_bg.jpg
```

---

## 🚨 Troubleshooting

### Common Issues

**Memory Limit Exceeded (Railway):**
```bash
# Check current memory usage
curl https://your-app.railway.app/api/bg/status

# Switch to ISNet Tiny service
# Edit railway.toml startCommand and redeploy
```

**Model Download Issues:**
```bash
# Check Railway logs
railway logs

# Models download on first request - be patient
# Pre-download in Dockerfile for faster startups
```

**Build Failures:**
```bash
# Clear Railway cache
railway build --clear-cache

# Check requirements.txt formatting
pip install -r requirements.txt  # Test locally first
```

### Railway-Specific Issues

**Cold Starts:**
- Enable health checks to keep service warm
- Use Railway's always-on feature for production

**Storage Issues:**
- Railway uses ephemeral storage
- Files in /tmp are cleared on restart
- Don't rely on persistent file storage

**Memory Monitoring:**
```bash
# View Railway metrics
railway metrics

# Check service logs
railway logs --tail
```

---

## 📈 Scaling Guidelines

### When to Use Each Deployment

**Use Full PixPort App when:**
- Need complete passport photo processing
- Require multiple background removal models
- Have >512MB memory available
- Need maximum flexibility

**Use ISNet Tiny Service when:**
- Only need background removal
- Memory is limited (≤512MB)
- Want fastest possible deployment
- Need predictable resource usage

### Resource Planning

**Railway Hobby Plan (512MB):**
- ✅ ISNet Tiny Service (235MB peak)
- ⚠️  Full PixPort App (350MB peak) - tight but possible
- ❌ Multiple instances

**Railway Pro Plan (8GB):**
- ✅ Multiple ISNet Tiny instances
- ✅ Full PixPort App with headroom  
- ✅ Multiple deployment environments

---

## 🔐 Security Considerations

### Environment Variables
- Never commit API keys or secrets
- Use Railway's environment variable system
- Rotate secrets regularly

### File Uploads
- Validate file types and sizes
- Scan uploads for malware if needed
- Clean up temporary files

### Rate Limiting
- Implement rate limiting for production
- Use Flask-Limiter or Railway's built-in limits
- Monitor API usage patterns

---

## 📚 Additional Resources

- [Railway Documentation](https://docs.railway.app/)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [ONNX Runtime Documentation](https://onnxruntime.ai/)
- [ISNet Paper](https://arxiv.org/abs/2112.13465)

---

## ✅ Ready to Deploy!

Your PixPort application is now ready for deployment with two optimized options:

1. **Quick Railway Deploy (ISNet Tiny):**
   ```bash
   # Edit railway.toml to use app_isnet_tiny.py
   railway up
   ```

2. **Full App Deploy:**
   ```bash
   railway up  # Uses default configuration
   ```

Both deployments include comprehensive monitoring, error handling, and are optimized for Railway's 512MB memory limit.

**Happy deploying! 🎉**
