from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .team_members_api import get_users_by_type_and_grade

# Create router and register viewsets
router = DefaultRouter()
router.register(r'permit-types', views.PermitTypeViewSet)
router.register(r'hazards', views.HazardLibraryViewSet)
router.register(r'workflow-templates', views.WorkflowTemplateViewSet)
router.register(r'permits', views.PermitViewSet)
router.register(r'permit-workers', views.PermitWorkerViewSet)
router.register(r'permit-approvals', views.PermitApprovalViewSet)
router.register(r'permit-extensions', views.PermitExtensionViewSet)
router.register(r'permit-audits', views.PermitAuditViewSet)
router.register(r'gas-readings', views.GasReadingViewSet)
router.register(r'permit-photos', views.PermitPhotoViewSet)
router.register(r'digital-signatures', views.DigitalSignatureViewSet)
router.register(r'workflow-instances', views.WorkflowInstanceViewSet)
router.register(r'system-integrations', views.SystemIntegrationViewSet)
router.register(r'compliance-reports', views.ComplianceReportViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Workflow URLs
    path('', include('ptw.workflow_urls')),
    
    # Additional API endpoints
    path('sync-offline-data/', views.sync_offline_data, name='sync-offline-data'),
    path('qr-scan/<str:qr_code>/', views.qr_scan_permit, name='qr-scan-permit'),
    path('mobile-permit/<int:permit_id>/', views.mobile_permit_view, name='mobile-permit-view'),
    path('team-members/get_users_by_type_and_grade/', get_users_by_type_and_grade, name='get-users-by-type-and-grade'),
    
    # Legacy endpoints for backward compatibility
    path('permit-types/', views.PermitTypeViewSet.as_view({'get': 'list', 'post': 'create'}), name='permit-types-list'),
    path('permits/', views.PermitViewSet.as_view({'get': 'list', 'post': 'create'}), name='permits-list'),
    path('permits/<int:pk>/', views.PermitViewSet.as_view({
        'get': 'retrieve', 
        'put': 'update', 
        'patch': 'partial_update', 
        'delete': 'destroy'
    }), name='permit-detail'),
    path('permits/<int:pk>/verify/', views.PermitViewSet.as_view({
        'post': 'verify'
    }), name='permit-verify'),
    path('permits/<int:pk>/approve/', views.PermitViewSet.as_view({
        'post': 'approve'
    }), name='permit-approve'),
    path('permits/<int:pk>/reject/', views.PermitViewSet.as_view({
        'post': 'reject'
    }), name='permit-reject'),
]