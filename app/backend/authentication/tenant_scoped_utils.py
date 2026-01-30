from dataclasses import dataclass
import logging
import os
from typing import Optional

from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request

from control_plane.models import CollaborationMembership, CollaborationSharePolicy
from .tenant_resolver import TenantResolver

SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}
EXEMPT_PATHS = {
    '/authentication/login/',
    '/authentication/token/refresh/',
    '/authentication/token/refresh/ws/',
    '/authentication/logout/',
}

logger = logging.getLogger("request")


@dataclass(frozen=True)
class TenantScope:
    tenant_id: Optional[str]
    project_id: Optional[int]
    source: str


def ensure_tenant_context(request: Request):
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        raise PermissionDenied('Authentication credentials were not provided.')

    tenant_id = getattr(user, 'athens_tenant_id', None)
    if not tenant_id:
        raise PermissionDenied('Tenant context is required.')

    tenant = TenantResolver.validate_tenant(str(tenant_id))
    if not tenant:
        raise PermissionDenied('Invalid or inactive tenant.')

    request.athens_tenant_id = str(tenant_id)
    request.athens_tenant = tenant
    user_state = getattr(user, '_state', None)
    request.tenant_db = getattr(user_state, 'db', None)

    return tenant


def ensure_project(request: Request):
    project = getattr(getattr(request, 'user', None), 'project', None)
    if not project:
        raise PermissionDenied('User must be assigned to a project.')
    return project


def enforce_collaboration_read_only(request: Request, domain: str):
    collaboration_project_id = request.query_params.get('collaboration_project_id')
    if not collaboration_project_id:
        return None

    if request.method not in SAFE_METHODS:
        raise PermissionDenied('Cross-tenant writes are not allowed.')

    tenant_id = getattr(request, 'athens_tenant_id', None)
    if not tenant_id:
        raise PermissionDenied('Tenant context is required.')

    membership = CollaborationMembership.objects.filter(
        collaboration_project_id=collaboration_project_id,
        tenant_id=tenant_id,
        status=CollaborationMembership.Status.ACTIVE,
    ).exists()

    if not membership:
        raise PermissionDenied('Tenant is not a member of this collaboration project.')

    policy = CollaborationSharePolicy.objects.filter(
        collaboration_project_id=collaboration_project_id,
        domain=domain,
    ).first()

    if not policy or 'READ' not in policy.allowed_actions:
        raise PermissionDenied('Collaboration policy does not allow READ for this domain.')

    return None


def is_tenant_scope_v2_enabled(request: Optional[Request] = None) -> bool:
    flags = getattr(settings, "FEATURE_FLAGS", {}) or {}
    if "FF_TENANT_SCOPE_V2" in flags:
        return bool(flags.get("FF_TENANT_SCOPE_V2"))
    env_value = os.getenv("FEATURE_FLAGS__FF_TENANT_SCOPE_V2")
    if env_value is None:
        return False
    return env_value.lower() in ("1", "true", "yes", "on")


def is_scope_exempt_path(path: str) -> bool:
    return path in EXEMPT_PATHS


def _normalize_project_id(value):
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def resolve_scope_from_request(request: Request) -> TenantScope:
    user = getattr(request, "user", None)
    if user and getattr(user, "is_authenticated", False):
        tenant_id = getattr(user, "athens_tenant_id", None)
        project_id = getattr(user, "project_id", None)
        if not project_id and getattr(user, "project", None):
            project_id = getattr(user.project, "id", None)
        if tenant_id or project_id:
            return TenantScope(
                tenant_id=str(tenant_id) if tenant_id else None,
                project_id=_normalize_project_id(project_id),
                source="user",
            )

    session = getattr(request, "session", None)
    if session:
        tenant_id = session.get("athens_tenant_id")
        project_id = session.get("project_id") or session.get("project")
        if tenant_id or project_id:
            return TenantScope(
                tenant_id=str(tenant_id) if tenant_id else None,
                project_id=_normalize_project_id(project_id),
                source="session",
            )

    tenant_id = request.META.get("HTTP_X_ATHENS_TENANT_ID")
    project_id = request.META.get("HTTP_X_ATHENS_PROJECT_ID")
    if tenant_id or project_id:
        return TenantScope(
            tenant_id=str(tenant_id) if tenant_id else None,
            project_id=_normalize_project_id(project_id),
            source="header",
        )

    return TenantScope(tenant_id=None, project_id=None, source="none")


def log_scope_decision(request: Request, decision: str, reason: str, status_code: int, scope: Optional[TenantScope] = None):
    user = getattr(request, "user", None)
    user_id = str(getattr(user, "id", "anon")) if getattr(user, "is_authenticated", False) else "anon"
    request_id = getattr(request, "request_id", "unknown")
    tenant_id = None
    project_id = None
    scope_source = "none"
    if scope:
        tenant_id = scope.tenant_id
        project_id = scope.project_id
        scope_source = scope.source
    else:
        tenant_id = getattr(request, "scope_tenant_id", None)
        project_id = getattr(request, "scope_project_id", None)
        scope_source = getattr(request, "scope_source", "none")

    logger.info(
        "tenant_scope decision=%s reason=%s request_id=%s user_id=%s tenant_id=%s project_id=%s scope_source=%s endpoint=%s method=%s status_code=%s",
        decision,
        reason,
        request_id,
        user_id,
        tenant_id,
        project_id,
        scope_source,
        getattr(request, "path", ""),
        getattr(request, "method", ""),
        status_code,
    )


def enforce_scope_or_403(request: Request, *, require_project: bool = True) -> Optional[TenantScope]:
    if not is_tenant_scope_v2_enabled(request) or is_scope_exempt_path(request.path):
        return None

    user = getattr(request, "user", None)
    if not user or not getattr(user, "is_authenticated", False):
        log_scope_decision(request, "deny", "authentication_required", 401)
        raise NotAuthenticated("Authentication credentials were not provided.")

    scope = resolve_scope_from_request(request)
    if not scope.tenant_id:
        log_scope_decision(request, "deny", "tenant_scope_missing", 403, scope)
        raise PermissionDenied("Tenant scope missing")
    if require_project and not scope.project_id:
        log_scope_decision(request, "deny", "project_scope_missing", 403, scope)
        raise PermissionDenied("Project scope missing")

    request.scope_tenant_id = scope.tenant_id
    request.scope_project_id = scope.project_id
    request.scope_source = scope.source
    log_scope_decision(request, "allow", "scope_resolved", 200, scope)
    return scope


def _resolve_object_tenant_id(obj, tenant_attr: str):
    tenant_id = getattr(obj, tenant_attr, None)
    if tenant_id is None and hasattr(obj, "user"):
        tenant_id = getattr(obj.user, "athens_tenant_id", None)
    return tenant_id


def _resolve_object_project_id(obj, project_attr: str):
    project_id = getattr(obj, project_attr, None)
    if project_id is None and hasattr(obj, "project"):
        project_id = getattr(obj.project, "id", None)
    if project_id is None and hasattr(obj, "user"):
        project_id = getattr(getattr(obj.user, "project", None), "id", None)
        if project_id is None:
            project_id = getattr(obj.user, "project_id", None)
    return _normalize_project_id(project_id)


def enforce_object_scope_or_403(
    request: Request,
    obj,
    *,
    tenant_attr: str = "athens_tenant_id",
    project_attr: str = "project_id",
):
    scope = None
    if getattr(request, "scope_tenant_id", None) or getattr(request, "scope_project_id", None):
        scope = TenantScope(
            tenant_id=getattr(request, "scope_tenant_id", None),
            project_id=getattr(request, "scope_project_id", None),
            source=getattr(request, "scope_source", "unknown"),
        )
    else:
        scope = enforce_scope_or_403(request)
        if scope is None:
            return None

    obj_tenant_id = _resolve_object_tenant_id(obj, tenant_attr)
    obj_project_id = _resolve_object_project_id(obj, project_attr)

    if not obj_tenant_id:
        log_scope_decision(request, "deny", "object_tenant_missing", 403, scope)
        raise PermissionDenied("Object tenant scope missing")
    if not obj_project_id:
        log_scope_decision(request, "deny", "object_project_missing", 403, scope)
        raise PermissionDenied("Object project scope missing")

    if str(obj_tenant_id) != str(scope.tenant_id):
        log_scope_decision(request, "deny", "tenant_scope_mismatch", 403, scope)
        raise PermissionDenied("Object tenant scope mismatch")
    if str(obj_project_id) != str(scope.project_id):
        log_scope_decision(request, "deny", "project_scope_mismatch", 403, scope)
        raise PermissionDenied("Object project scope mismatch")

    return None


class ScopedWriteMixin:
    scope_require_project = True

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.method in SAFE_METHODS:
            return
        enforce_scope_or_403(request, require_project=self.scope_require_project)
