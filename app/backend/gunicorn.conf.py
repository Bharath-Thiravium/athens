# gunicorn.conf.py
import os

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8001")
workers = int(os.getenv("GUNICORN_WORKERS", "4"))
worker_class = os.getenv("GUNICORN_WORKER_CLASS", "sync")
worker_connections = int(os.getenv("GUNICORN_WORKER_CONNECTIONS", "1000"))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "100"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))
preload_app = os.getenv("GUNICORN_PRELOAD_APP", "True").lower() in ("1", "true", "yes", "on")
