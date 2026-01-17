"""
Athens Multi-Tenant Base Manager and QuerySet

This module provides base classes for tenant-aware database operations.
All Athens domain models should inherit from these base classes to ensure
proper tenant isolation.
"""

from django.db import models
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class TenantAwareQuerySet(models.QuerySet):
    """
    QuerySet that automatically filters by athens_tenant_id.
    
    This ensures that all database queries are tenant-isolated by default.
    """
    
    def __init__(self, *args, **kwargs):
        self._tenant_id = None
        super().__init__(*args, **kwargs)
    
    def for_tenant(self, tenant_id):
        """
        Filter queryset for a specific tenant.
        
        Args:
            tenant_id (UUID): Athens tenant ID
            
        Returns:
            TenantAwareQuerySet: Filtered queryset
        """
        if not tenant_id:
            raise ValidationError("tenant_id is required for tenant-aware queries")
        
        clone = self._clone()
        clone._tenant_id = tenant_id
        return clone.filter(athens_tenant_id=tenant_id)
    
    def _clone(self):
        """Override clone to preserve tenant context"""
        clone = super()._clone()
        clone._tenant_id = self._tenant_id
        return clone
    
    def create(self, **kwargs):
        """Override create to automatically set athens_tenant_id"""
        if self._tenant_id and 'athens_tenant_id' not in kwargs:
            kwargs['athens_tenant_id'] = self._tenant_id
        return super().create(**kwargs)
    
    def bulk_create(self, objs, **kwargs):
        """Override bulk_create to automatically set athens_tenant_id"""
        if self._tenant_id:
            for obj in objs:
                if not hasattr(obj, 'athens_tenant_id') or obj.athens_tenant_id is None:
                    obj.athens_tenant_id = self._tenant_id
        return super().bulk_create(objs, **kwargs)
    
    def update(self, **kwargs):
        """Override update to prevent athens_tenant_id changes"""
        if 'athens_tenant_id' in kwargs:
            logger.warning("Attempted to update athens_tenant_id - this is not allowed")
            raise ValidationError("athens_tenant_id cannot be updated")
        return super().update(**kwargs)


class TenantAwareManager(models.Manager):
    """
    Manager that provides tenant-aware database operations.
    
    This manager ensures that all queries are properly filtered by tenant
    and provides convenient methods for tenant-specific operations.
    """
    
    def get_queryset(self):
        """Return tenant-aware queryset"""
        return TenantAwareQuerySet(self.model, using=self._db)
    
    def for_tenant(self, tenant_id):
        """
        Get queryset filtered for a specific tenant.
        
        Args:
            tenant_id (UUID): Athens tenant ID
            
        Returns:
            TenantAwareQuerySet: Filtered queryset
        """
        return self.get_queryset().for_tenant(tenant_id)
    
    def create_for_tenant(self, tenant_id, **kwargs):
        """
        Create an object for a specific tenant.
        
        Args:
            tenant_id (UUID): Athens tenant ID
            **kwargs: Model field values
            
        Returns:
            Model instance
        """
        if not tenant_id:
            raise ValidationError("tenant_id is required")
        
        kwargs['athens_tenant_id'] = tenant_id
        return self.create(**kwargs)
    
    def get_for_tenant(self, tenant_id, **kwargs):
        """
        Get a single object for a specific tenant.
        
        Args:
            tenant_id (UUID): Athens tenant ID
            **kwargs: Lookup parameters
            
        Returns:
            Model instance
        """
        return self.for_tenant(tenant_id).get(**kwargs)
    
    def filter_for_tenant(self, tenant_id, **kwargs):
        """
        Filter objects for a specific tenant.
        
        Args:
            tenant_id (UUID): Athens tenant ID
            **kwargs: Filter parameters
            
        Returns:
            TenantAwareQuerySet: Filtered queryset
        """
        return self.for_tenant(tenant_id).filter(**kwargs)


class TenantAwareModel(models.Model):
    """
    Abstract base model for tenant-aware models.
    
    All Athens domain models should inherit from this base class
    to ensure proper tenant isolation.
    """
    
    # Multi-tenant isolation field - MANDATORY for all domain models
    athens_tenant_id = models.UUIDField(
        help_text="Athens tenant identifier for multi-tenant isolation",
        db_index=True  # Always index this field for performance
    )
    
    # Use tenant-aware manager
    objects = TenantAwareManager()
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['athens_tenant_id']),
        ]
    
    def save(self, *args, **kwargs):
        """Override save to validate tenant isolation"""
        # Ensure athens_tenant_id is set
        if not self.athens_tenant_id:
            raise ValidationError("athens_tenant_id is required for all domain objects")
        
        # Prevent tenant changes on existing objects
        if self.pk:
            try:
                existing = self.__class__.objects.get(pk=self.pk)
                if existing.athens_tenant_id != self.athens_tenant_id:
                    raise ValidationError("athens_tenant_id cannot be changed")
            except self.__class__.DoesNotExist:
                pass  # New object, allow save
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate tenant isolation"""
        super().clean()
        if not self.athens_tenant_id:
            raise ValidationError("athens_tenant_id is required")


# Utility functions for tenant operations

def get_tenant_from_request(request):
    """
    Extract athens_tenant_id from request.
    
    Args:
        request: Django request object
        
    Returns:
        UUID: Athens tenant ID or None if not found
    """
    return getattr(request, 'athens_tenant_id', None)


def ensure_tenant_isolation(queryset, tenant_id):
    """
    Ensure queryset is properly filtered by tenant.
    
    Args:
        queryset: Django QuerySet
        tenant_id (UUID): Athens tenant ID
        
    Returns:
        QuerySet: Tenant-filtered queryset
        
    Raises:
        ValidationError: If tenant_id is missing
    """
    if not tenant_id:
        raise ValidationError("tenant_id is required for tenant isolation")
    
    if hasattr(queryset, 'for_tenant'):
        return queryset.for_tenant(tenant_id)
    else:
        return queryset.filter(athens_tenant_id=tenant_id)


def validate_tenant_access(obj, tenant_id):
    """
    Validate that an object belongs to the specified tenant.
    
    Args:
        obj: Model instance
        tenant_id (UUID): Athens tenant ID
        
    Raises:
        ValidationError: If object doesn't belong to tenant
    """
    if not tenant_id:
        raise ValidationError("tenant_id is required")
    
    if not hasattr(obj, 'athens_tenant_id'):
        raise ValidationError("Object is not tenant-aware")
    
    if obj.athens_tenant_id != tenant_id:
        raise ValidationError("Object does not belong to the specified tenant")


# Decorator for tenant-aware views
def require_tenant_context(view_func):
    """
    Decorator to ensure view has tenant context.
    
    This decorator checks that the request has athens_tenant_id
    and raises an error if it's missing.
    """
    def wrapper(request, *args, **kwargs):
        if not hasattr(request, 'athens_tenant_id') or not request.athens_tenant_id:
            from django.http import JsonResponse
            return JsonResponse({
                'error': 'TENANT_CONTEXT_MISSING',
                'message': 'Tenant context is required for this operation'
            }, status=400)
        
        return view_func(request, *args, **kwargs)
    
    return wrapper