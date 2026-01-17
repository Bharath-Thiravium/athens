"""
URL configuration for Athens tenant management APIs.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .tenant_views import AthensTenantViewSet, TenantConfigView

# Create router for tenant management
router = DefaultRouter()
router.register(r'tenants', AthensTenantViewSet, basename='tenant')
router.register(r'config', TenantConfigView, basename='tenant-config')

urlpatterns = [
    path('api/tenant/', include(router.urls)),
]