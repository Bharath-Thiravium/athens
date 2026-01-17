from django.core.exceptions import PermissionDenied
from rest_framework.request import Request

from control_plane.models import CollaborationMembership, CollaborationSharePolicy
from .tenant_resolver import TenantResolver

SAFE_METHODS = {'GET', 'HEAD', 'OPTIONS'}


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
