"""
SQLite CI settings for testing without PostgreSQL socket access.
Allows migrations and tests to run locally, generating DB-agnostic migrations.
"""
from backend.settings import *
import os

# Override database to SQLite in-memory
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': True,
    }
}

# Ensure SECRET_KEY has safe default
SECRET_KEY = os.environ.get('SECRET_KEY', 'test-secret-key-for-ci-only-do-not-use-in-production')

# Simplify logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {'handlers': ['console'], 'level': 'WARNING'},
}

# Speed up tests
PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable any PostgreSQL-specific features
DEBUG = True
