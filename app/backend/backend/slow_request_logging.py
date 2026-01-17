import logging
import os
import time
from contextlib import ExitStack

from django.db import connections

logger = logging.getLogger("slow_request")


class SlowRequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = os.getenv("SLOW_REQUEST_LOGGING", "").lower() in ("1", "true", "yes")
        self.threshold_ms = float(os.getenv("SLOW_REQUEST_THRESHOLD_MS", "1000"))
        self.log_sql = os.getenv("SLOW_REQUEST_LOG_SQL", "").lower() in ("1", "true", "yes")
        self.sql_threshold_ms = float(os.getenv("SLOW_REQUEST_SQL_THRESHOLD_MS", "200"))
        self.max_sql = int(os.getenv("SLOW_REQUEST_SQL_MAX", "5"))

    def __call__(self, request):
        if not self.enabled:
            return self.get_response(request)

        start = time.monotonic()
        response = None
        error = None

        query_stats = {}
        for alias in connections:
            query_stats[alias] = {"count": 0, "time_ms": 0.0, "slow": []}

        def make_wrapper(alias):
            def wrapper_execute(execute, sql, params, many, context):
                query_start = time.monotonic()
                try:
                    return execute(sql, params, many, context)
                finally:
                    duration_ms = (time.monotonic() - query_start) * 1000
                    stats = query_stats[alias]
                    stats["count"] += 1
                    stats["time_ms"] += duration_ms
                    if self.log_sql and duration_ms >= self.sql_threshold_ms:
                        if len(stats["slow"]) < self.max_sql:
                            stats["slow"].append((duration_ms, sql))

            return wrapper_execute

        with ExitStack() as stack:
            for alias in connections:
                stack.enter_context(connections[alias].execute_wrapper(make_wrapper(alias)))

            try:
                response = self.get_response(request)
                return response
            except Exception as exc:  # noqa: BLE001
                error = exc
                raise
            finally:
                duration_ms = (time.monotonic() - start) * 1000
                if duration_ms < self.threshold_ms and error is None:
                    return

                status = response.status_code if response is not None else "exception"
                user_id = "anon"
                if hasattr(request, "user") and getattr(request.user, "is_authenticated", False):
                    user_id = str(request.user.id)

                view_name = "-"
                resolver_match = getattr(request, "resolver_match", None)
                if resolver_match:
                    view_name = resolver_match.view_name or resolver_match.route or "-"

                db_summary_parts = []
                for alias, stats in query_stats.items():
                    if stats["count"] > 0:
                        db_summary_parts.append(
                            f"{alias}:{stats['count']}q/{stats['time_ms']:.1f}ms"
                        )
                db_summary = ",".join(db_summary_parts) or "no_queries"

                logger.warning(
                    "Slow request %s %s status=%s duration_ms=%.1f user=%s view=%s db=%s",
                    request.method,
                    request.path,
                    status,
                    duration_ms,
                    user_id,
                    view_name,
                    db_summary,
                )

                if self.log_sql:
                    for alias, stats in query_stats.items():
                        for duration, sql in stats["slow"]:
                            logger.warning(
                                "Slow SQL alias=%s duration_ms=%.1f sql=%s",
                                alias,
                                duration,
                                sql,
                            )
