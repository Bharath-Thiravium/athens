from django.db import IntegrityError
from django.test import TestCase

from control_plane.models import (
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


class ControlPlaneModelTests(TestCase):
    databases = {'control_plane'}

    def test_tenant_and_db_config_creation(self):
        tenant = TenantCompany.objects.create(name='tenant-a', display_name='Tenant A')
        config = TenantDatabaseConfig.objects.create(tenant=tenant, connection_key='tenant-a-db')

        self.assertEqual(config.tenant_id, tenant.id)
        self.assertEqual(config.connection_key, 'tenant-a-db')

    def test_collaboration_entities(self):
        tenant = TenantCompany.objects.create(name='tenant-a')
        superadmin = SuperadminUser.objects.create(email='admin@example.com')
        project = CollaborationProject.objects.create(slug='proj-1', title='Project 1', created_by=superadmin)
        membership = CollaborationMembership.objects.create(
            collaboration_project=project,
            tenant=tenant,
            role=CollaborationMembership.Role.CLIENT,
        )
        policy = CollaborationSharePolicy.objects.create(
            collaboration_project=project,
            domain='incidents',
            allowed_actions=['READ'],
        )
        link = ProjectLink.objects.create(
            collaboration_project=project,
            tenant=tenant,
            tenant_project_id='123',
        )

        self.assertEqual(membership.tenant_id, tenant.id)
        self.assertEqual(policy.domain, 'incidents')
        self.assertEqual(link.tenant_project_id, '123')

    def test_membership_unique_constraint(self):
        tenant = TenantCompany.objects.create(name='tenant-a')
        project = CollaborationProject.objects.create(slug='proj-1', title='Project 1')
        CollaborationMembership.objects.create(
            collaboration_project=project,
            tenant=tenant,
            role=CollaborationMembership.Role.CLIENT,
        )

        with self.assertRaises(IntegrityError):
            CollaborationMembership.objects.create(
                collaboration_project=project,
                tenant=tenant,
                role=CollaborationMembership.Role.EPC,
            )

    def test_audit_log_entry(self):
        tenant = TenantCompany.objects.create(name='tenant-a')
        log = AuditLog.objects.create(
            actor='system',
            action='collab.read',
            tenant=tenant,
            request_id='req-123',
        )

        self.assertEqual(log.actor, 'system')
        self.assertEqual(log.request_id, 'req-123')

    def test_tenant_invitation_uniqueness(self):
        tenant = TenantCompany.objects.create(name='tenant-a')
        TenantInvitation.objects.create(tenant=tenant, email='user@example.com')

        with self.assertRaises(IntegrityError):
            TenantInvitation.objects.create(tenant=tenant, email='user@example.com')

    def test_subscription_unique_constraint(self):
        tenant = TenantCompany.objects.create(name='tenant-a')
        TenantModuleSubscription.objects.create(tenant=tenant, module_code='incidents')

        with self.assertRaises(IntegrityError):
            TenantModuleSubscription.objects.create(tenant=tenant, module_code='incidents')
