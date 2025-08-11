# ==========================================
# 🚀 OPTIMIZED DOCKERFILE FOR RAILWAY DEPLOYMENT
# Multi-stage build optimized for 512MB memory limit
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

# Set environment variables for Railway deployment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080
ENV PYTHONPATH=/app
ENV RAILWAY_ENVIRONMENT_NAME=production

# Fix pymatting/numba cache issues in containerized environment
ENV NUMBA_DISABLE_JIT=1
ENV NUMBA_CACHE_DIR=/tmp/.numba_cache
ENV NUMBA_DISABLE_PERFORMANCE_WARNINGS=1

# Install minimal runtime dependencies (ultra-compatible)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Test if ONNX Runtime needs additional libraries and install if needed
RUN python -c "import onnxruntime" || \
    (echo "ONNX Runtime needs additional libraries, installing..." && \
     apt-get update && apt-get install -y --no-install-recommends libgomp1 && \
     rm -rf /var/lib/apt/lists/*)

# Set work directory first
WORKDIR /app

# Create necessary directories including numba cache
RUN mkdir -p /tmp/uploads /tmp/processed /app/logs /tmp/.numba_cache

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set proper permissions for directories including numba cache
RUN chown -R appuser:appuser /tmp/uploads /tmp/processed /tmp/.numba_cache /app

# Copy application code
COPY --chown=appuser:appuser app/ ./app/

# Copy essential Python files
COPY --chown=appuser:appuser wsgi.py ./
COPY --chown=appuser:appuser main.py ./
# model_utils.py removed - using simplified Railway-optimized services
# download_models.py available but not needed in container
COPY --chown=appuser:appuser requirements.txt ./

# Copy configuration files
COPY --chown=appuser:appuser gunicorn.conf.py ./

# Switch to non-root user
USER appuser

# ===== MODEL PRELOADING OPTIMIZATION =====
# Note: Model preloading happens at runtime via app.py to avoid Docker build issues
# The optimized model_utils.py will handle fast loading on container startup

# Skip model preloading for Railway to save memory during build
# Models will be downloaded at runtime for Railway deployment

# Verify Flask app structure
RUN echo "📝 Verifying app structure..." && \
    python -c "from app import create_app; print('✅ Flask app structure valid')" && \
    python -c "from app.services.isnet_tiny_service import ISNetTinyService; print('✅ Railway services available')" && \
    echo "✅ Railway optimization components verified!"

# Expose port
EXPOSE 8080

# Health check for Railway
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:$PORT/health || exit 1

# ===== RAILWAY OPTIMIZED STARTUP COMMAND =====
# Use Gunicorn with Railway optimizations (512MB memory limit)
CMD gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --threads 2 \
    --timeout 60 \
    --keep-alive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info \
    wsgi:app
