"""
Gunicorn configuration for PixPort - Optimized for Google Cloud Run
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"

# Worker processes - optimized for Cloud Run
workers = 2  # Increased for better concurrency
worker_class = "gthread"  # Thread-based for better I/O handling
threads = 4  # 4 threads per worker = 8 concurrent requests
worker_connections = 1000  # Higher for Cloud Run

# Timeouts optimized for AI processing
timeout = 300  # 5 minutes for AI model processing
keepalive = 5  # Keep connections alive longer
graceful_timeout = 30  # Graceful shutdown time

# Worker recycling for memory management
max_requests = 100  # Increased for better performance
max_requests_jitter = 10

# Preload app for faster cold starts
preload_app = True

# Performance optimizations
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else None

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"
capture_output = True

# Process naming
proc_name = "pixport"

def post_fork(server, worker):
    """Configure worker process after fork"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)
    
def pre_fork(server, worker):
    """Clean up before forking"""
    server.log.info("Pre-fork cleanup")
    
def when_ready(server):
    """Called when server is ready to accept connections"""
    server.log.info("Server is ready. Spawning workers")
    
def worker_int(worker):
    """Handle worker interrupt"""
    worker.log.info("Worker received INT or QUIT signal")
    
def pre_exec(server):
    """Called before exec"""
    server.log.info("Forked child, re-executing.")
