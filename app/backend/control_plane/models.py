import uuid
from django.db import models


class TenantCompany(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        DISABLED = 'disabled', 'Disabled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)
    display_name = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.display_name or self.name


class TenantDatabaseConfig(models.Model):
    tenant = models.OneToOneField(TenantCompany, on_delete=models.CASCADE, related_name='db_config')
    connection_key = models.CharField(max_length=255, unique=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.connection_key}"


class TenantModuleSubscription(models.Model):
    tenant = models.ForeignKey(TenantCompany, on_delete=models.CASCADE, related_name='module_subscriptions')
    module_code = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    plan_tier = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'module_code')

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.module_code}"


class SuperadminUser(models.Model):
    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', 'Superadmin'
        SUPPORT = 'support', 'Support'

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, blank=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.SUPERADMIN)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.email


class CollaborationProject(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        ENDED = 'ended', 'Ended'

    slug = models.SlugField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    created_by = models.ForeignKey(
        SuperadminUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_collaboration_projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class CollaborationMembership(models.Model):
    class Role(models.TextChoices):
        CLIENT = 'client', 'Client'
        EPC = 'epc', 'EPC'
        CONTRACTOR = 'contractor', 'Contractor'
        VIEWER = 'viewer', 'Viewer'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'

    collaboration_project = models.ForeignKey(
        CollaborationProject,
        on_delete=models.CASCADE,
        related_name='memberships',
    )
    tenant = models.ForeignKey(TenantCompany, on_delete=models.CASCADE, related_name='collaboration_memberships')
    role = models.CharField(max_length=32, choices=Role.choices)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('collaboration_project', 'tenant')

    def __str__(self) -> str:
        return f"{self.collaboration_project_id}:{self.tenant_id}:{self.role}"


class CollaborationSharePolicy(models.Model):
    collaboration_project = models.ForeignKey(
        CollaborationProject,
        on_delete=models.CASCADE,
        related_name='share_policies',
    )
    domain = models.CharField(max_length=100)
    allowed_actions = models.JSONField(default=list)
    filters = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('collaboration_project', 'domain')

    def __str__(self) -> str:
        return f"{self.collaboration_project_id}:{self.domain}"


class SaaSSubscription(models.Model):
    class Status(models.TextChoices):
        TRIALING = 'trialing', 'Trialing'
        ACTIVE = 'active', 'Active'
        PAST_DUE = 'past_due', 'Past Due'
        CANCELED = 'canceled', 'Canceled'
        SUSPENDED = 'suspended', 'Suspended'

    tenant = models.OneToOneField(TenantCompany, on_delete=models.CASCADE, related_name='saas_subscription')
    plan = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TRIALING)
    seats = models.PositiveIntegerField(default=1)
    current_period_start = models.DateField(null=True, blank=True)
    current_period_end = models.DateField(null=True, blank=True)
    renewal_at = models.DateField(null=True, blank=True)
    last_payment_at = models.DateField(null=True, blank=True)
    payment_provider = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.plan or 'unset'}"


class SaaSAuditLog(models.Model):
    class EntityType(models.TextChoices):
        TENANT = 'tenant', 'Tenant'
        USER = 'user', 'User'
        SUBSCRIPTION = 'subscription', 'Subscription'
        SETTINGS = 'settings', 'Settings'

    actor = models.ForeignKey('authentication.CustomUser', null=True, blank=True, on_delete=models.SET_NULL, related_name='saas_audit_logs')
    action = models.CharField(max_length=100)
    entity_type = models.CharField(max_length=50, choices=EntityType.choices)
    entity_id = models.CharField(max_length=100)
    before = models.JSONField(null=True, blank=True)
    after = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.action} {self.entity_type}:{self.entity_id}"


class SaaSPlatformSettings(models.Model):
    id = models.PositiveSmallIntegerField(primary_key=True, default=1, editable=False)
    platform_name = models.CharField(max_length=200, default='Athens')
    platform_url = models.URLField(blank=True)
    support_email = models.EmailField(blank=True)
    support_phone = models.CharField(max_length=50, blank=True)
    logo_url = models.URLField(blank=True)
    primary_color = models.CharField(max_length=20, blank=True)

    email_from_name = models.CharField(max_length=100, blank=True)
    email_from_address = models.EmailField(blank=True)
    email_reply_to = models.EmailField(blank=True)

    billing_provider = models.CharField(max_length=100, blank=True)
    billing_mode = models.CharField(max_length=50, blank=True)
    invoice_footer = models.TextField(blank=True)

    session_timeout_minutes = models.PositiveIntegerField(default=60)
    audit_retention_days = models.PositiveIntegerField(default=365)
    allow_self_signup = models.BooleanField(default=False)
    require_mfa = models.BooleanField(default=False)
    maintenance_mode = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"SaaSPlatformSettings:{self.platform_name}"


class ProjectLink(models.Model):
    class MappingType(models.TextChoices):
        CANONICAL = 'canonical', 'Canonical'
        MIRRORED = 'mirrored', 'Mirrored'
        EXTERNAL = 'external', 'External'

    collaboration_project = models.ForeignKey(
        CollaborationProject,
        on_delete=models.CASCADE,
        related_name='project_links',
    )
    tenant = models.ForeignKey(TenantCompany, on_delete=models.CASCADE, related_name='project_links')
    tenant_project_id = models.CharField(max_length=64)
    mapping_type = models.CharField(max_length=32, choices=MappingType.choices, default=MappingType.CANONICAL)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('collaboration_project', 'tenant', 'tenant_project_id')

    def __str__(self) -> str:
        return f"{self.collaboration_project_id}:{self.tenant_id}:{self.tenant_project_id}"


class TenantInvitation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACCEPTED = 'accepted', 'Accepted'
        EXPIRED = 'expired', 'Expired'

    tenant = models.ForeignKey(TenantCompany, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('tenant', 'email')

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.email}"


class AuditLog(models.Model):
    actor = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    target_type = models.CharField(max_length=255, blank=True)
    target_id = models.CharField(max_length=255, blank=True)
    tenant = models.ForeignKey(TenantCompany, on_delete=models.SET_NULL, null=True, blank=True)
    collaboration_project = models.ForeignKey(
        CollaborationProject,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    request_id = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.created_at}:{self.action}"
