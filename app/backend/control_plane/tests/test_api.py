from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from control_plane.models import TenantCompany


class ControlPlaneApiTests(APITestCase):
    databases = {'default', 'control_plane'}

    def setUp(self):
        user_model = get_user_model()
        self.superuser = user_model.objects.create_superuser(
            username='superadmin',
            email='superadmin@example.com',
            password='password123',
        )
        self.client.force_authenticate(user=self.superuser)

    def test_create_tenant_company(self):
        payload = {'name': 'tenant-a', 'display_name': 'Tenant A'}
        response = self.client.post('/api/control-plane/tenants/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(TenantCompany.objects.count(), 1)
        self.assertEqual(TenantCompany.objects.first().name, 'tenant-a')
