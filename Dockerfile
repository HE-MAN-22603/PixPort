# Use Python 3.11.9 slim image for minimal size and security
FROM python:3.11.9-slim

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8080

# Install system dependencies required for OpenCV and image processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libglib2.0-dev \
    pkg-config \
    libfontconfig1 \
    libxss1 \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create directories for uploads and processed files
RUN mkdir -p /tmp/uploads /tmp/processed && \
    chmod 755 /tmp/uploads /tmp/processed

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set proper permissions
RUN chown -R appuser:appuser /app /tmp/uploads /tmp/processed

# Switch to non-root user
USER appuser

# Expose port 8080 (Cloud Run default)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/ || exit 1

# Run with Gunicorn using optimized configuration for Cloud Run
CMD gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 --preload --max-requests 1000 --max-requests-jitter 50 app:app
