#!/usr/bin/env python3
# Gunicorn configuration for Lamina Dashboard

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5001"
backlog = 2048

# Worker processes
workers = 1  # Use single worker for WebSocket support
worker_class = "eventlet"  # Required for SocketIO WebSocket support
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "lamina-dashboard"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (disabled for internal cluster communication)
keyfile = None
certfile = None

# Application
module = "lamina_dashboard.app:app"

# Preload app for better performance
preload_app = True

# Enable graceful shutdown
graceful_timeout = 30