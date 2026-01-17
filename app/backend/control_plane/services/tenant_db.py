import os
import re
from django.conf import settings
from django.db import connections
from django.contrib.auth import get_user_model

from control_plane.models import TenantDatabaseConfig


def _sanitize_key(value: str) -> str:
    return re.sub(r'[^A-Z0-9]+', '_', value.upper()).strip('_')


def _env_key(prefix: str, connection_key: str) -> str:
    sanitized = _sanitize_key(connection_key)
    return f"{prefix}_{sanitized}"


def _build_db_settings(connection_key: str) -> dict:
    engine = os.getenv(_env_key('TENANT_DB_ENGINE', connection_key), 'django.db.backends.postgresql')

    if engine == 'django.db.backends.sqlite3':
        name = os.getenv(_env_key('TENANT_DB_NAME', connection_key))
        if not name:
            raise ValueError('TENANT_DB_NAME is required for sqlite tenant DB')
        return {
            'ENGINE': engine,
            'NAME': name,
        }

    name = os.getenv(_env_key('TENANT_DB_NAME', connection_key))
    user = os.getenv(_env_key('TENANT_DB_USER', connection_key))
    password = os.getenv(_env_key('TENANT_DB_PASSWORD', connection_key))
    host = os.getenv(_env_key('TENANT_DB_HOST', connection_key), 'localhost')
    port = os.getenv(_env_key('TENANT_DB_PORT', connection_key), '5432')

    if not name or not user or not password:
        raise ValueError('TENANT_DB_NAME, TENANT_DB_USER, and TENANT_DB_PASSWORD are required')

    return {
        'ENGINE': engine,
        'NAME': name,
        'USER': user,
        'PASSWORD': password,
        'HOST': host,
        'PORT': port,
    }


def get_tenant_db_alias(tenant_id) -> str:
    config = TenantDatabaseConfig.objects.select_related('tenant').get(tenant_id=tenant_id)
    connection_key = config.connection_key
    alias = f"tenant_{_sanitize_key(connection_key).lower()}"

    if alias not in settings.DATABASES:
        settings.DATABASES[alias] = _build_db_settings(connection_key)
        connections.databases[alias] = settings.DATABASES[alias]

    return alias


def tenant_user_exists(tenant_db_alias: str, email: str) -> bool:
    if not email:
        return False
    user_model = get_user_model()
    try:
        return user_model.objects.using(tenant_db_alias).filter(email__iexact=email).exists()
    except Exception:
        return False
