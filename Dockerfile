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
COPY --chown=appuser:appuser preload_models.py ./

# Copy configuration files if they exist
COPY --chown=appuser:appuser gunicorn.conf.py* ./

# Switch to non-root user
USER appuser

# ===== MODEL PRELOADING OPTIMIZATION =====
# Note: Model preloading happens at runtime via app.py to avoid Docker build issues
# The optimized model_utils.py will handle fast loading on container startup

# Preload AI models during build (optional - will continue if fails)
RUN python preload_models.py || echo "Model preload failed, will load at runtime"

# Verify our optimization files are in place
RUN echo "📝 Verifying optimization setup..." && \
    python -c "import model_utils; print('✅ model_utils.py available')" && \
    python -c "from app import create_app; print('✅ Flask app structure valid')" && \
    echo "✅ All optimization components verified!"

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
