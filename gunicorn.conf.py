"""
Gunicorn configuration for PixPort with memory optimization
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', 8080)}"

# Worker processes
workers = 1  # Single worker to minimize memory usage
worker_class = "sync"
worker_connections = 10  # Lower concurrent connections per worker

# Worker timeout and recycling  
timeout = 300  # 5 minutes for AI processing
keepalive = 2
max_requests = 50  # Recycle worker after 50 requests to prevent memory leaks
max_requests_jitter = 5  # Add randomness to recycling

# Preload app for better memory sharing
preload_app = True

# Memory management
worker_tmp_dir = "/dev/shm" if os.path.exists("/dev/shm") else None  # Use RAM disk if available

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
