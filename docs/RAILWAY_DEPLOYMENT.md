# 🚀 PixPort Railway Deployment Guide

This guide will help you deploy PixPort to Railway successfully.

## 📋 Prerequisites

1. **Railway Account**: Create a free account at [railway.app](https://railway.app)
2. **GitHub Repository**: Push your PixPort code to GitHub
3. **Railway CLI** (optional): Install Railway CLI for local testing

## 🛠️ Deployment Steps

### 1. Prepare Your Repository

Ensure these files are in your repository:
- ✅ `Procfile` - Web process definition
- ✅ `railway.json` - Railway configuration
- ✅ `nixpacks.toml` - Build configuration
- ✅ `runtime.txt` - Python version
- ✅ `requirements.txt` - Python dependencies
- ✅ `.gitignore` - Git ignore rules

### 2. Deploy to Railway

#### Option A: GitHub Integration (Recommended)

1. **Connect Repository**:
   - Go to [railway.app](https://railway.app)
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your PixPort repository

2. **Configure Environment Variables**:
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add these variables:
     ```
     SECRET_KEY=your-super-secret-key-here
     FLASK_ENV=production
     REMBG_MODEL=u2net
     ```

3. **Deploy**:
   - Railway will automatically build and deploy
   - Wait for deployment to complete (3-5 minutes)

#### Option B: Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Deploy
railway up
```

### 3. Configure Domain (Optional)

1. Go to "Settings" tab in Railway dashboard
2. Click "Generate Domain" for a free `.railway.app` subdomain
3. Or connect your custom domain

## 🔧 Configuration Details

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | ✅ Yes | - | Flask secret key for sessions |
| `FLASK_ENV` | No | `production` | Flask environment |
| `REMBG_MODEL` | No | `u2net` | AI model for background removal |
| `REDIS_URL` | No | `memory://` | Redis URL for rate limiting |

### Resource Requirements

- **Memory**: 1GB minimum (AI models are memory intensive)
- **Disk**: 500MB minimum
- **CPU**: 1 vCPU minimum
- **Build Time**: 3-5 minutes (downloading AI models)

## 📊 Monitoring

### Health Checks

Railway automatically monitors these endpoints:
- `GET /health` - Application health status
- `GET /status` - Detailed system status
- `GET /ping` - Simple connectivity test

### Logs

View logs in Railway dashboard:
1. Go to your project
2. Click "Deployments" tab
3. Click on latest deployment
4. View real-time logs

## 🐛 Troubleshooting

### Common Issues

#### 1. Build Timeout
**Problem**: Build takes too long downloading AI models
**Solution**: Models are cached after first build

#### 2. Memory Issues
**Problem**: App crashes due to insufficient memory
**Solution**: Upgrade Railway plan for more memory

#### 3. File Upload Issues
**Problem**: Files not saving properly
**Solution**: Using `/tmp` directory for Railway (already configured)

#### 4. Static Files Not Loading
**Problem**: CSS/JS files not loading
**Solution**: Using custom static file serving (already configured)

### Debug Commands

```bash
# Check deployment status
railway status

# View logs
railway logs

# Connect to shell
railway shell

# Set environment variable
railway variables set SECRET_KEY=your-key-here
```

## 🚀 Performance Optimization

### Railway-Specific Optimizations

1. **Cold Starts**: Railway apps sleep after inactivity
   - Solution: Use a uptime monitoring service

2. **File Storage**: Railway doesn't persist files between deployments
   - Solution: Use cloud storage (S3, Cloudinary) for production

3. **Database**: Add PostgreSQL if needed
   ```bash
   railway add postgresql
   ```

## 📈 Scaling

### Upgrade Plans
- **Hobby Plan**: $5/month - More resources
- **Pro Plan**: $20/month - Custom domains, team collaboration

### Horizontal Scaling
- Railway supports multiple instances
- Configure in `railway.json`

## 🔒 Security

### Production Checklist
- ✅ Strong `SECRET_KEY` set
- ✅ `FLASK_ENV=production`
- ✅ Rate limiting enabled
- ✅ File upload validation
- ✅ HTTPS enabled (automatic on Railway)

## 📞 Support

### Resources
- **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- **Discord**: [Railway Discord Server](https://discord.gg/railway)
- **Status**: [status.railway.app](https://status.railway.app)

### PixPort Issues
- Check logs in Railway dashboard
- Verify environment variables
- Test health endpoints
- Monitor resource usage

---

**🎉 Congratulations!** Your PixPort app should now be running on Railway!

Visit your Railway-provided URL to test the deployment.
