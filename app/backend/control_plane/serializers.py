from rest_framework import serializers

from .models import (
    TenantCompany,
    TenantDatabaseConfig,
    TenantModuleSubscription,
    SuperadminUser,
    CollaborationProject,
    CollaborationMembership,
    CollaborationSharePolicy,
    ProjectLink,
    TenantInvitation,
    AuditLog,
    SaaSSubscription,
    SaaSAuditLog,
    SaaSPlatformSettings,
)
from authentication.models import CustomUser
from authentication.serializers import CustomUserSerializer
from django.db.models import Count, F


class TenantCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantCompany
        fields = '__all__'


class TenantDatabaseConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantDatabaseConfig
        fields = '__all__'


class TenantModuleSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantModuleSubscription
        fields = '__all__'


class SuperadminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperadminUser
        fields = '__all__'


class CollaborationProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborationProject
        fields = '__all__'


class CollaborationMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborationMembership
        fields = '__all__'


class CollaborationSharePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = CollaborationSharePolicy
        fields = '__all__'


class ProjectLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectLink
        fields = '__all__'


class TenantInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantInvitation
        fields = '__all__'


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'


class TenantLookupSerializer(serializers.Serializer):
    email = serializers.EmailField()


# --- SaaS control plane serializers ---

class SaaSTenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantCompany
        fields = ['id', 'name', 'display_name', 'status', 'created_at']
        read_only_fields = ['id', 'created_at']


class SaaSSubscriptionSerializer(serializers.ModelSerializer):
    tenant_id = serializers.UUIDField(source='tenant.id', read_only=True)

    class Meta:
        model = SaaSSubscription
        fields = [
            'tenant_id',
            'plan',
            'status',
            'seats',
            'current_period_start',
            'current_period_end',
            'renewal_at',
            'last_payment_at',
            'payment_provider',
            'notes',
        ]


class SaaSPlatformSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaaSPlatformSettings
        fields = [
            'id',
            'platform_name',
            'platform_url',
            'support_email',
            'support_phone',
            'logo_url',
            'primary_color',
            'email_from_name',
            'email_from_address',
            'email_reply_to',
            'billing_provider',
            'billing_mode',
            'invoice_footer',
            'session_timeout_minutes',
            'audit_retention_days',
            'allow_self_signup',
            'require_mfa',
            'maintenance_mode',
            'updated_at',
        ]
        read_only_fields = ['id', 'updated_at']


class MasterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    tenant_id = serializers.UUIDField(write_only=True, required=False)

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'tenant_id', 'is_active']
        read_only_fields = ['id']

    def validate(self, attrs):
        if self.instance is None:
            if not attrs.get('tenant_id'):
                raise serializers.ValidationError({'tenant_id': 'Tenant is required.'})
            if not attrs.get('password'):
                raise serializers.ValidationError({'password': 'Password is required.'})
        return attrs

    def create(self, validated_data):
        tenant_id = validated_data.pop('tenant_id')
        password = validated_data.pop('password')
        is_active = validated_data.pop('is_active', True)
        user = CustomUser.objects.create_user(
            user_type='master',
            admin_type='master',
            athens_tenant_id=tenant_id,
            is_staff=True,
            is_active=is_active,
            **validated_data,
        )
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        tenant_id = validated_data.pop('tenant_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tenant_id:
            instance.athens_tenant_id = tenant_id
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class SaaSAuditLogSerializer(serializers.ModelSerializer):
    actor_username = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = SaaSAuditLog
        fields = ['id', 'actor', 'actor_username', 'action', 'entity_type', 'entity_id', 'before', 'after', 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'created_at', 'actor_username']


class SaaSTenantListSerializer(serializers.ModelSerializer):
    subscription_plan = serializers.CharField(source='saas_subscription.plan', read_only=True)
    subscription_status = serializers.CharField(source='saas_subscription.status', read_only=True)
    masters_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = TenantCompany
        fields = ['id', 'name', 'display_name', 'status', 'created_at', 'subscription_plan', 'subscription_status', 'masters_count']
        read_only_fields = fields


class SaaSTenantStatsSerializer(serializers.Serializer):
    tenant_id = serializers.UUIDField()
    masters_count = serializers.IntegerField()
    subscription_status = serializers.CharField()
    seats = serializers.IntegerField()
    current_period_end = serializers.DateField(allow_null=True)
    last_activity = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()


class SaaSMasterListSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(read_only=True)
    date_joined = serializers.SerializerMethodField()

    def get_date_joined(self, obj):
        if hasattr(obj, 'user_detail') and obj.user_detail:
            # UserDetail has date_of_joining, not date_joined
            return obj.user_detail.date_of_joining or obj.user_detail.created_at
        # CustomUser doesn't have date_joined, use last_login or None
        return obj.last_login

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'tenant_name', 'athens_tenant_id', 'is_active', 'last_login', 'date_joined']
        read_only_fields = fields


class SaaSSubscriptionListSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.display_name', read_only=True)

    class Meta:
        model = SaaSSubscription
        fields = ['tenant_id', 'tenant_name', 'plan', 'status', 'seats', 'current_period_end', 'updated_at']
        read_only_fields = fields


class SaaSMetricsOverviewSerializer(serializers.Serializer):
    range = serializers.DictField()
    tenants = serializers.DictField()
    masters = serializers.DictField()
    subscriptions = serializers.DictField()
    activity = serializers.DictField()
    timeseries = serializers.DictField()
