from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import saas_views

router = DefaultRouter()
router.register(r'tenants', saas_views.SaaSTenantViewSet, basename='saas-tenants')
router.register(r'masters', saas_views.SaaSMasterViewSet, basename='saas-masters')
router.register(r'tenants/(?P<tenant_pk>[^/.]+)/subscription', saas_views.SaaSSubscriptionViewSet, basename='saas-subscription')
router.register(r'audit-logs', saas_views.SaaSAuditLogViewSet, basename='saas-audit-logs')

urlpatterns = [
    path('metrics/overview', saas_views.SaaSMetricsOverviewAPIView.as_view(), name='saas-metrics-overview'),
    path('settings', saas_views.SaaSPlatformSettingsView.as_view(), name='saas-settings'),
    path('tenants/<uuid:tenant_id>/modules', saas_views.SaaSTenantModulesAPIView.as_view(), name='saas-tenant-modules'),
    path('tenants/<uuid:tenant_id>/sync', saas_views.SaaSTenantSyncAPIView.as_view(), name='saas-tenant-sync'),
    path('tenants-list', saas_views.SaaSTenantListView.as_view(), name='saas-tenants-search'),
    path('tenants/<uuid:pk>/stats', saas_views.SaaSTenantStatsView.as_view(), name='saas-tenant-stats'),
    path(
        'tenants/<uuid:tenant_id>/subscription/',
        saas_views.SaaSSubscriptionViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='saas-tenant-subscription',
    ),
    path('masters-list', saas_views.SaaSMasterViewSet.as_view({'get': 'list'}), name='saas-masters-search'),
    path('subscriptions', saas_views.SaaSSubscriptionListView.as_view(), name='saas-subscriptions'),
    path('', include(router.urls)),
]
