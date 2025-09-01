import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes - use uvicorn-worker instead of deprecated uvicorn.workers
workers = int(os.getenv("WORKERS", min(multiprocessing.cpu_count() * 2 + 1, 8)))
worker_class = "uvicorn_worker.UvicornWorker"  # Updated package
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

# Timeouts
timeout = 30
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "fastapi-app"

# Server mechanics
preload_app = True
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = os.getenv("USER", "appuser")
group = os.getenv("GROUP", "appuser")
tmp_upload_dir = None

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance
max_requests_jitter = 100    # Add jitter to prevent thundering herd

# Monitoring
statsd_host = os.getenv("STATSD_HOST")
statsd_prefix = "fastapi"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (if terminating SSL at the application level)
# keyfile = os.getenv("SSL_KEYFILE")
# certfile = os.getenv("SSL_CERTFILE")

# Graceful shutdown
def on_starting(server):
    server.log.info("Starting FastAPI with Gunicorn")

def on_reload(server):
    server.log.info("Reloading FastAPI application")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")
