from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

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
)
from .permissions import IsPlatformSuperadmin
from .serializers import (
    TenantCompanySerializer,
    TenantDatabaseConfigSerializer,
    TenantModuleSubscriptionSerializer,
    SuperadminUserSerializer,
    CollaborationProjectSerializer,
    CollaborationMembershipSerializer,
    CollaborationSharePolicySerializer,
    ProjectLinkSerializer,
    TenantInvitationSerializer,
    AuditLogSerializer,
    TenantLookupSerializer,
)
from .services.tenant_db import get_tenant_db_alias, tenant_user_exists
from .throttles import TenantLookupThrottle


class TenantCompanyViewSet(viewsets.ModelViewSet):
    queryset = TenantCompany.objects.all()
    serializer_class = TenantCompanySerializer
    permission_classes = [IsPlatformSuperadmin]


class TenantDatabaseConfigViewSet(viewsets.ModelViewSet):
    queryset = TenantDatabaseConfig.objects.select_related('tenant').all()
    serializer_class = TenantDatabaseConfigSerializer
    permission_classes = [IsPlatformSuperadmin]


class TenantModuleSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = TenantModuleSubscription.objects.select_related('tenant').all()
    serializer_class = TenantModuleSubscriptionSerializer
    permission_classes = [IsPlatformSuperadmin]


class SuperadminUserViewSet(viewsets.ModelViewSet):
    queryset = SuperadminUser.objects.all()
    serializer_class = SuperadminUserSerializer
    permission_classes = [IsPlatformSuperadmin]


class CollaborationProjectViewSet(viewsets.ModelViewSet):
    queryset = CollaborationProject.objects.all()
    serializer_class = CollaborationProjectSerializer
    permission_classes = [IsPlatformSuperadmin]


class CollaborationMembershipViewSet(viewsets.ModelViewSet):
    queryset = CollaborationMembership.objects.select_related('collaboration_project', 'tenant').all()
    serializer_class = CollaborationMembershipSerializer
    permission_classes = [IsPlatformSuperadmin]


class CollaborationSharePolicyViewSet(viewsets.ModelViewSet):
    queryset = CollaborationSharePolicy.objects.select_related('collaboration_project').all()
    serializer_class = CollaborationSharePolicySerializer
    permission_classes = [IsPlatformSuperadmin]


class ProjectLinkViewSet(viewsets.ModelViewSet):
    queryset = ProjectLink.objects.select_related('collaboration_project', 'tenant').all()
    serializer_class = ProjectLinkSerializer
    permission_classes = [IsPlatformSuperadmin]


class TenantInvitationViewSet(viewsets.ModelViewSet):
    queryset = TenantInvitation.objects.select_related('tenant').all()
    serializer_class = TenantInvitationSerializer
    permission_classes = [IsPlatformSuperadmin]


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related('tenant', 'collaboration_project').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsPlatformSuperadmin]


class TenantLookupAPIView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = [TenantLookupThrottle]

    def post(self, request, *args, **kwargs):
        serializer = TenantLookupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        invitations = TenantInvitation.objects.filter(email__iexact=email).select_related('tenant')
        invited_tenant_ids = {invite.tenant_id for invite in invitations}

        tenant_records = TenantDatabaseConfig.objects.select_related('tenant').all()
        matched_tenants = []

        for tenant_config in tenant_records:
            tenant_id = tenant_config.tenant_id
            if tenant_id in invited_tenant_ids:
                matched_tenants.append(tenant_config.tenant)
                continue

            try:
                tenant_db_alias = get_tenant_db_alias(tenant_id)
            except Exception:
                continue

            if tenant_user_exists(tenant_db_alias, email):
                matched_tenants.append(tenant_config.tenant)

        response = [
            {
                'tenant_id': str(tenant.id),
                'display_name': tenant.display_name or tenant.name,
            }
            for tenant in matched_tenants
        ]

        return Response({'tenants': response}, status=status.HTTP_200_OK)
