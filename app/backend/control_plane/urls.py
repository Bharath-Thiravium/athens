from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'tenants', views.TenantCompanyViewSet, basename='control-tenant')
router.register(r'tenant-db-configs', views.TenantDatabaseConfigViewSet, basename='control-tenant-db-config')
router.register(r'tenant-subscriptions', views.TenantModuleSubscriptionViewSet, basename='control-tenant-subscription')
router.register(r'superadmins', views.SuperadminUserViewSet, basename='control-superadmin')
router.register(r'collaboration-projects', views.CollaborationProjectViewSet, basename='control-collab-project')
router.register(r'collaboration-memberships', views.CollaborationMembershipViewSet, basename='control-collab-membership')
router.register(r'collaboration-policies', views.CollaborationSharePolicyViewSet, basename='control-collab-policy')
router.register(r'project-links', views.ProjectLinkViewSet, basename='control-project-link')
router.register(r'invitations', views.TenantInvitationViewSet, basename='control-tenant-invitation')
router.register(r'audit-logs', views.AuditLogViewSet, basename='control-audit-log')

urlpatterns = [
    path('tenant-lookup/', views.TenantLookupAPIView.as_view(), name='control-tenant-lookup'),
    path('', include(router.urls)),
]
