# ==========================================
# 🚀 OPTIMIZED DOCKERFILE FOR GOOGLE CLOUD RUN
# Multi-stage build for faster deploys and smaller images
# ==========================================

# ===== STAGE 1: Build Stage =====
FROM python:3.11.9-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ===== STAGE 2: Production Stage =====
FROM python:3.11.9-slim as production

# Set environment variables for Cloud Run
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080
ENV PYTHONPATH=/app

# Install only runtime dependencies (smaller image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libgl1-mesa-glx \
    libgthread-2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set work directory
WORKDIR /app

# Create necessary directories with proper permissions
RUN mkdir -p /tmp/uploads /tmp/processed /app/logs && \
    chown -R appuser:appuser /tmp/uploads /tmp/processed /app

# Copy application code (exclude unnecessary files)
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser *.py .
COPY --chown=appuser:appuser requirements.txt .

# Copy configuration files if they exist
COPY --chown=appuser:appuser gunicorn.conf.py* ./

# Switch to non-root user
USER appuser

# ===== MODEL PRELOADING OPTIMIZATION =====
# Download and cache AI models during build (not at runtime)
# This eliminates the cold start delay
RUN python -c "
print('📦 Pre-downloading AI models for faster cold starts...')
try:
    # Import and trigger model download
    from rembg import new_session
    print('Downloading isnet-general-use model...')
    session = new_session('isnet-general-use')
    print('✅ Model downloaded and cached successfully!')
except Exception as e:
    print(f'⚠️ Model download failed: {e}')
    print('Models will be downloaded on first request.')
"

# Test model loading to ensure everything works
RUN python -c "
print('📝 Testing model loading...')
try:
    from model_utils import load_model
    success = load_model()
    if success:
        print('✅ Model preloading test successful!')
    else:
        print('⚠️ Model preloading test failed, but app will still work.')
except Exception as e:
    print(f'⚠️ Model test failed: {e}')
    print('App will use fallback loading.')
print('📝 Model testing complete.')
"

# Expose port
EXPOSE 8080

# Health check for Cloud Run
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# ===== OPTIMIZED STARTUP COMMAND =====
# Use Gunicorn with Cloud Run optimizations
CMD gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 4 \
    --timeout 300 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    wsgi:app
