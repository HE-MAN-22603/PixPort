# Optimized Dockerfile for Google Cloud Run - Fast Cold Start
FROM python:3.11.9-slim

# Set environment variables for performance
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies in single layer
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set work directory
WORKDIR /app

# Copy and install requirements (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    pip cache purge

# Copy application code
COPY . .

# Pre-create directories and pre-download lightweight models
RUN mkdir -p /tmp/uploads /tmp/processed /tmp/models && \
    python -c "import torch; print('PyTorch ready')" 2>/dev/null || echo "PyTorch not available" && \
    python -c "import rembg; rembg.new_session('isnet-general-use')" 2>/dev/null || echo "Model will download on first use"

# Expose port
EXPOSE 8080

# Use optimized Gunicorn configuration
CMD gunicorn --config gunicorn.conf.py wsgi:app
