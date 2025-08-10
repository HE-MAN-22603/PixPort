# PixPort - Google Cloud Run Deployment Guide

Complete guide for deploying your Flask application to Google Cloud Run with GitHub integration.

## 📋 Prerequisites

1. **Google Cloud Project**
   - Active Google Cloud Project with billing enabled
   - Project ID: `my-gcp-project-id` (replace with your actual project ID)

2. **Required Google Cloud APIs**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable artifactregistry.googleapis.com
   ```

3. **GitHub Repository**
   - Your code pushed to GitHub
   - Admin access to the repository

## 🚀 Setup Steps

### Step 1: Create Artifact Registry Repository

```bash
# Create repository for Docker images
gcloud artifacts repositories create my-artifact-repo \
    --repository-format=docker \
    --location=europe-west1 \
    --description="PixPort Flask application images"
```

### Step 2: Set Up Cloud Build Triggers (GitHub Integration)

#### Option A: Using Google Cloud Console (Recommended)

1. Go to [Cloud Build Triggers](https://console.cloud.google.com/cloud-build/triggers)
2. Click **"Create Trigger"**
3. Configure:
   - **Name**: `pixport-deploy-trigger`
   - **Event**: Push to a branch
   - **Source**: Connect your GitHub repository
   - **Branch pattern**: `^main$` or `^master$`
   - **Build Configuration**: Cloud Build configuration file
   - **Cloud Build configuration file location**: `cloudbuild.yaml`
4. Click **"Create"**

#### Option B: Using gcloud CLI

```bash
# Connect your GitHub repo (interactive setup)
gcloud builds repositories connect

# Create the trigger
gcloud builds triggers create github \
    --repo-name=your-repo-name \
    --repo-owner=your-github-username \
    --branch-pattern=^main$ \
    --build-config=cloudbuild.yaml \
    --description="Deploy PixPort to Cloud Run on main branch push"
```

### Step 3: Configure GitHub Secrets (for GitHub Actions - Optional)

If using GitHub Actions workflow, add these secrets to your repository:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add `GCP_SA_KEY` secret:

```bash
# Create service account
gcloud iam service-accounts create pixport-deploy \
    --description="Service account for PixPort Cloud Run deployment" \
    --display-name="PixPort Deploy SA"

# Grant necessary permissions
gcloud projects add-iam-policy-binding my-gcp-project-id \
    --member="serviceAccount:pixport-deploy@my-gcp-project-id.iam.gserviceaccount.com" \
    --role="roles/cloudbuild.builds.builder"

gcloud projects add-iam-policy-binding my-gcp-project-id \
    --member="serviceAccount:pixport-deploy@my-gcp-project-id.iam.gserviceaccount.com" \
    --role="roles/run.developer"

gcloud projects add-iam-policy-binding my-gcp-project-id \
    --member="serviceAccount:pixport-deploy@my-gcp-project-id.iam.gserviceaccount.com" \
    --role="roles/artifactregistry.writer"

# Create and download key
gcloud iam service-accounts keys create pixport-sa-key.json \
    --iam-account=pixport-deploy@my-gcp-project-id.iam.gserviceaccount.com

# Copy the content of pixport-sa-key.json to GitHub secret GCP_SA_KEY
```

### Step 4: Update Configuration Files

Replace placeholders in the following files:

#### cloudbuild.yaml
```yaml
# Replace these values:
PROJECT_ID: my-gcp-project-id → your-actual-project-id
REGION: europe-west1 → your-preferred-region
REPO_NAME: my-artifact-repo → your-artifact-registry-repo
SERVICE_NAME: my-flask-service → your-service-name
```

#### GitHub Actions workflow (.github/workflows/deploy-to-cloudrun.yml)
```yaml
# Replace these values:
PROJECT_ID: my-gcp-project-id → your-actual-project-id
REGION: europe-west1 → your-preferred-region
REPO_NAME: my-artifact-repo → your-artifact-registry-repo
SERVICE_NAME: my-flask-service → your-service-name
```

## 📦 Deployment Process

### Automatic Deployment (Recommended)

1. **Push to main branch**:
   ```bash
   git add .
   git commit -m "Deploy to Cloud Run"
   git push origin main
   ```

2. **Monitor deployment**:
   - Cloud Build: https://console.cloud.google.com/cloud-build/builds
   - Cloud Run: https://console.cloud.google.com/run

### Manual Deployment

```bash
# Build and deploy manually
gcloud builds submit --config cloudbuild.yaml

# Or use gcloud run deploy directly
gcloud run deploy my-flask-service \
    --source . \
    --region europe-west1 \
    --platform managed \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10
```

## ⚙️ Configuration Details

### Resource Allocation
- **Memory**: 2Gi (perfect for AI models)
- **CPU**: 1 vCPU
- **Max Instances**: 10 (suitable for free tier)
- **Concurrency**: 80 requests per instance
- **Timeout**: 300 seconds (5 minutes)

### Environment Variables
```
FLASK_ENV=production
UPLOAD_FOLDER=/tmp/uploads
PROCESSED_FOLDER=/tmp/processed
REMBG_MODEL=isnet-general-use
```

### Free Tier Limits
- **CPU-seconds**: 180,000 per month
- **Memory-seconds**: 360,000 per month
- **Requests**: 2 million per month
- **Bandwidth**: 1GB outbound per month

## 🔧 Troubleshooting

### Common Issues

1. **Build Timeout**
   ```bash
   # Increase timeout in cloudbuild.yaml
   timeout: '1800s'  # 30 minutes
   ```

2. **Memory Issues**
   ```bash
   # Increase memory allocation
   --memory 4Gi
   ```

3. **Cold Start Issues**
   ```bash
   # Add minimum instances (billable)
   --min-instances 1
   ```

4. **Permission Denied**
   ```bash
   # Check IAM permissions
   gcloud projects get-iam-policy my-gcp-project-id
   ```

### Monitoring

```bash
# View service details
gcloud run services describe my-flask-service --region=europe-west1

# View logs
gcloud logs read "resource.type=cloud_run_revision" --limit=50

# Check service URL
gcloud run services list --platform=managed
```

## 🌐 Post-Deployment

### Test Your Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe my-flask-service --region=europe-west1 --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/api/bg/health

# Test main page
curl $SERVICE_URL
```

### Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create \
    --service=my-flask-service \
    --domain=your-domain.com \
    --region=europe-west1
```

## 💰 Cost Optimization

1. **Use minimum resources**:
   - Start with 1 CPU, 2Gi memory
   - Adjust based on usage

2. **Set max instances**:
   ```bash
   --max-instances 10  # Prevent runaway scaling
   ```

3. **Monitor usage**:
   - Check Cloud Console billing dashboard
   - Set up billing alerts

4. **Free tier tips**:
   - Keep under 180k CPU-seconds/month
   - Monitor request count
   - Use efficient AI models

## 🔄 CI/CD Best Practices

1. **Environment-specific configs**
2. **Automated testing before deployment**
3. **Rollback strategies**
4. **Health checks and monitoring**
5. **Secrets management**

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [GitHub Integration Guide](https://cloud.google.com/build/docs/automating-builds/github/build-repos-from-github)

---

**🎉 Your PixPort Flask application is now ready for Google Cloud Run deployment!**

The setup provides automatic deployment from GitHub with optimized configuration for the free tier while maintaining high performance and scalability.
