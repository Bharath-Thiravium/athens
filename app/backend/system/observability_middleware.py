import logging
import os
import time
import uuid

from django.conf import settings
from django.db import connections
from django.http import JsonResponse

logger = logging.getLogger("request")


class RequestContextLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = getattr(settings, "REQUEST_LOGGING", True)
        self.log_db_connections = getattr(settings, "REQUEST_LOG_DB_CONNECTIONS", True)
        self.crash_guard = os.getenv("CRASH_GUARD_ENABLED", "True").lower() in ("1", "true", "yes", "on")
        self.request_id_header = os.getenv("REQUEST_ID_HEADER", "HTTP_X_REQUEST_ID")
        self.response_header = os.getenv("REQUEST_ID_RESPONSE_HEADER", "X-Request-ID")

    def __call__(self, request):
        request_id = request.META.get(self.request_id_header) or uuid.uuid4().hex
        request.request_id = request_id

        start = time.monotonic()
        response = None
        error = None

        try:
            response = self.get_response(request)
            return response
        except Exception as exc:  # noqa: BLE001
            error = exc
            if self.crash_guard and not settings.DEBUG:
                response = JsonResponse(
                    {"detail": "Internal server error", "request_id": request_id},
                    status=500,
                )
                return response
            raise
        finally:
            if response is not None:
                response[self.response_header] = request_id

            if self.enabled:
                self._log_request(request, response, error, start, request_id)

    def _log_request(self, request, response, error, start, request_id):
        duration_ms = (time.monotonic() - start) * 1000
        user_id = "anon"
        if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
            user_id = str(request.user.id)

        status_before = self._extract_status_before(request)
        status_after = self._extract_status_after(response)
        http_status = response.status_code if response is not None else "exception"
        pid = os.getpid()
        db_connections = self._count_db_connections() if self.log_db_connections else "disabled"

        logger.info(
            "request_id=%s user_id=%s endpoint=%s status_before=%s status_after=%s http_status=%s pid=%s db_connections=%s duration_ms=%.1f error=%s",
            request_id,
            user_id,
            request.path,
            status_before,
            status_after,
            http_status,
            pid,
            db_connections,
            duration_ms,
            "yes" if error else "no",
        )

    def _extract_status_before(self, request):
        status_before = getattr(request, "status_before", None)
        if status_before:
            return status_before

        header_status = request.META.get("HTTP_X_STATUS_BEFORE")
        if header_status:
            return header_status

        data = getattr(request, "data", None)
        if isinstance(data, dict):
            return data.get("status_before") or data.get("previous_status")

        return None

    def _extract_status_after(self, response):
        if response is None:
            return None

        data = getattr(response, "data", None)
        if isinstance(data, dict):
            return data.get("status_after") or data.get("status") or data.get("new_status")

        return None

    def _count_db_connections(self):
        try:
            connection = connections["default"]
            if connection.vendor != "postgresql":
                return "n/a"
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database()"
                )
                result = cursor.fetchone()
                return result[0] if result else "n/a"
        except Exception:
            return "n/a"
