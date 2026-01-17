import datetime
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from authentication.models import CustomUser
from control_plane.models import TenantCompany, SaaSSubscription, SaaSAuditLog


class SaaSApiAuthTests(APITestCase):
    def setUp(self):
        self.superadmin = CustomUser.objects.create_user(
            username='superadmin',
            password='pass1234',
            user_type='superadmin',
            is_staff=True,
            is_superuser=True,
        )
        self.master = CustomUser.objects.create_user(
            username='masteruser',
            password='pass1234',
            user_type='master',
            is_staff=True,
        )

    def test_superadmin_can_access(self):
        client = APIClient()
        client.force_authenticate(self.superadmin)
        resp = client.get(reverse('saas-metrics-overview'))
        self.assertEqual(resp.status_code, 200)

    def test_master_cannot_access(self):
        client = APIClient()
        client.force_authenticate(self.master)
        resp = client.get(reverse('saas-metrics-overview'))
        self.assertEqual(resp.status_code, 403)


class SaaSListEndpointsTests(APITestCase):
    def setUp(self):
        self.superadmin = CustomUser.objects.create_user(
            username='superadmin',
            password='pass1234',
            user_type='superadmin',
            is_staff=True,
            is_superuser=True,
        )
        self.client = APIClient()
        self.client.force_authenticate(self.superadmin)
        self.tenant = TenantCompany.objects.create(name='Acme', display_name='Acme Inc')
        self.sub = SaaSSubscription.objects.create(tenant=self.tenant, plan='pro', status=SaaSSubscription.Status.ACTIVE)
        self.master = CustomUser.objects.create_user(
            username='master1',
            password='pass1234',
            user_type='master',
            is_staff=True,
            athens_tenant_id=self.tenant.id,
        )
        SaaSAuditLog.objects.create(actor=self.master, action='test', entity_type='tenant', entity_id=str(self.tenant.id))

    def test_tenants_list_filters(self):
        url = reverse('saas-tenants-search')
        resp = self.client.get(url, {'status': 'active'})
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_masters_list(self):
        url = reverse('saas-masters-search')
        resp = self.client.get(url, {'tenant_id': self.tenant.id})
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_subscriptions_list(self):
        url = reverse('saas-subscriptions')
        resp = self.client.get(url, {'status': 'active'})
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(resp.data['count'], 1)

    def test_audit_logs_filters(self):
        url = reverse('saas-audit-logs-list')
        resp = self.client.get(url, {'tenant_id': self.tenant.id})
        self.assertEqual(resp.status_code, 200)

    def test_tenant_stats(self):
        url = reverse('saas-tenant-stats', args=[self.tenant.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['masters_count'], 1)
