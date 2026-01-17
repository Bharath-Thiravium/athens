"""
Athens Tenant Management API Views

This module provides API endpoints for managing Athens tenants,
including tenant configuration, module/menu management, and tenant status.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.db import transaction
from .tenant_models import AthensTenant, TenantAuditLog, DEFAULT_MODULES, DEFAULT_MENUS
from .tenant_permissions import IsMasterAdmin, IsTenantAdmin, IsSAPInternal
from .serializers import AthensTenantSerializer, TenantAuditLogSerializer
import logging

logger = logging.getLogger(__name__)


class AthensTenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Athens tenants.
    
    Only master admins can create/delete tenants.
    Tenant admins can view and update their own tenant configuration.
    """
    
    queryset = AthensTenant.objects.all()
    serializer_class = AthensTenantSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions required for this view.
        
        SECURITY: Tenant creation/deletion MUST only come from SAP.
        Athens is a governed service, not a tenant authority.
        """
        if self.action in ['create', 'destroy']:
            # LOCKED: Only SAP can create/delete tenants
            # Athens should never autonomously manage tenant lifecycle
            permission_classes = [IsAuthenticated, IsSAPInternal]
        elif self.action in ['update', 'partial_update']:
            # Tenant admins can update their own tenant configuration
            permission_classes = [IsAuthenticated, IsTenantAdmin]
        else:
            # Anyone authenticated can view (filtered by permissions)
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions.
        """
        user = self.request.user
        
        # Master admins can see all tenants
        if hasattr(user, 'admin_type') and user.admin_type in ['master', 'masteradmin']:
            return AthensTenant.objects.all()
        
        # Tenant admins can only see their own tenant
        if hasattr(user, 'athens_tenant_id') and user.athens_tenant_id:
            return AthensTenant.objects.filter(id=user.athens_tenant_id)
        
        # No access for others
        return AthensTenant.objects.none()
    
    def perform_create(self, serializer):
        """Create tenant with audit logging"""
        with transaction.atomic():
            tenant = serializer.save()
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='created',
                description=f'Tenant created: {tenant.tenant_name}',
                performed_by=self.request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f'Tenant {tenant.id} created by user {self.request.user.id}')
    
    def perform_update(self, serializer):
        """Update tenant with audit logging"""
        with transaction.atomic():
            old_tenant = AthensTenant.objects.get(pk=serializer.instance.pk)
            tenant = serializer.save()
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='updated',
                description=f'Tenant updated: {tenant.tenant_name}',
                previous_value={
                    'enabled_modules': old_tenant.enabled_modules,
                    'enabled_menus': old_tenant.enabled_menus,
                    'is_active': old_tenant.is_active,
                },
                new_value={
                    'enabled_modules': tenant.enabled_modules,
                    'enabled_menus': tenant.enabled_menus,
                    'is_active': tenant.is_active,
                },
                performed_by=self.request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=self.request.META.get('HTTP_USER_AGENT', '')
            )
            
            logger.info(f'Tenant {tenant.id} updated by user {self.request.user.id}')
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def enable_module(self, request, pk=None):
        """Enable a module for the tenant"""
        tenant = self.get_object()
        module_name = request.data.get('module_name')
        
        if not module_name:
            return Response(
                {'error': 'module_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if module_name not in DEFAULT_MODULES:
            return Response(
                {'error': f'Invalid module: {module_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            tenant.enable_module(module_name)
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='module_enabled',
                description=f'Module enabled: {module_name}',
                new_value={'module': module_name},
                performed_by=request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return Response({'message': f'Module {module_name} enabled successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def disable_module(self, request, pk=None):
        """Disable a module for the tenant"""
        tenant = self.get_object()
        module_name = request.data.get('module_name')
        
        if not module_name:
            return Response(
                {'error': 'module_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            tenant.disable_module(module_name)
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='module_disabled',
                description=f'Module disabled: {module_name}',
                previous_value={'module': module_name},
                performed_by=request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return Response({'message': f'Module {module_name} disabled successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def enable_menu(self, request, pk=None):
        """Enable a menu for the tenant"""
        tenant = self.get_object()
        menu_name = request.data.get('menu_name')
        
        if not menu_name:
            return Response(
                {'error': 'menu_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if menu_name not in DEFAULT_MENUS:
            return Response(
                {'error': f'Invalid menu: {menu_name}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            tenant.enable_menu(menu_name)
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='menu_enabled',
                description=f'Menu enabled: {menu_name}',
                new_value={'menu': menu_name},
                performed_by=request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return Response({'message': f'Menu {menu_name} enabled successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsTenantAdmin])
    def disable_menu(self, request, pk=None):
        """Disable a menu for the tenant"""
        tenant = self.get_object()
        menu_name = request.data.get('menu_name')
        
        if not menu_name:
            return Response(
                {'error': 'menu_name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            tenant.disable_menu(menu_name)
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='menu_disabled',
                description=f'Menu disabled: {menu_name}',
                previous_value={'menu': menu_name},
                performed_by=request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return Response({'message': f'Menu {menu_name} disabled successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMasterAdmin])
    def activate(self, request, pk=None):
        """Activate a tenant"""
        tenant = self.get_object()
        
        with transaction.atomic():
            tenant.is_active = True
            tenant.save()
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='activated',
                description=f'Tenant activated: {tenant.tenant_name}',
                new_value={'is_active': True},
                performed_by=request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return Response({'message': 'Tenant activated successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsMasterAdmin])
    def deactivate(self, request, pk=None):
        """Deactivate a tenant"""
        tenant = self.get_object()
        
        with transaction.atomic():
            tenant.is_active = False
            tenant.save()
            
            # Create audit log
            TenantAuditLog.objects.create(
                tenant=tenant,
                action='deactivated',
                description=f'Tenant deactivated: {tenant.tenant_name}',
                previous_value={'is_active': True},
                new_value={'is_active': False},
                performed_by=request.user.id,
                ip_address=self.get_client_ip(),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return Response({'message': 'Tenant deactivated successfully'})
    
    @action(detail=False, methods=['get'])
    def available_modules(self, request):
        """Get list of available modules"""
        return Response({
            'modules': DEFAULT_MODULES,
            'count': len(DEFAULT_MODULES)
        })
    
    @action(detail=False, methods=['get'])
    def available_menus(self, request):
        """Get list of available menus"""
        return Response({
            'menus': DEFAULT_MENUS,
            'count': len(DEFAULT_MENUS)
        })
    
    @action(detail=True, methods=['get'])
    def audit_logs(self, request, pk=None):
        """Get audit logs for a tenant"""
        tenant = self.get_object()
        logs = tenant.audit_logs.all()[:50]  # Last 50 logs
        serializer = TenantAuditLogSerializer(logs, many=True)
        return Response(serializer.data)
    
    def get_client_ip(self):
        """Get client IP address from request"""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip


class TenantConfigView(viewsets.ReadOnlyModelViewSet):
    """Read-only view for tenant configuration (used by frontend)"""
    
    serializer_class = AthensTenantSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the current user's tenant"""
        if hasattr(self.request, 'athens_tenant_id') and self.request.athens_tenant_id:
            return AthensTenant.objects.filter(id=self.request.athens_tenant_id)
        return AthensTenant.objects.none()
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current tenant configuration"""
        if not hasattr(request, 'athens_tenant') or not request.athens_tenant:
            return Response(
                {'error': 'No tenant context available'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(request.athens_tenant)
        return Response(serializer.data)
