from unittest.mock import patch
from django.conf import settings
from django.test import override_settings

from rest_framework.test import APITestCase

from control_plane.models import TenantCompany, TenantDatabaseConfig, TenantInvitation


class TenantLookupTests(APITestCase):
    databases = {'default', 'control_plane'}

    def setUp(self):
        self.tenant = TenantCompany.objects.create(name='tenant-a', display_name='Tenant A')
        TenantDatabaseConfig.objects.create(tenant=self.tenant, connection_key='tenant-a')

    @patch('control_plane.views.tenant_user_exists')
    @patch('control_plane.views.get_tenant_db_alias')
    def test_lookup_includes_invited_tenant(self, mock_get_alias, mock_user_exists):
        TenantInvitation.objects.create(tenant=self.tenant, email='user@example.com')
        mock_get_alias.return_value = 'tenant_alias'
        mock_user_exists.return_value = False

        response = self.client.post('/api/control-plane/tenant-lookup/', {'email': 'user@example.com'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tenants']), 1)
        self.assertEqual(response.data['tenants'][0]['tenant_id'], str(self.tenant.id))

    @patch('control_plane.views.tenant_user_exists')
    @patch('control_plane.views.get_tenant_db_alias')
    def test_lookup_includes_existing_user(self, mock_get_alias, mock_user_exists):
        mock_get_alias.return_value = 'tenant_alias'
        mock_user_exists.return_value = True

        response = self.client.post('/api/control-plane/tenant-lookup/', {'email': 'user@example.com'}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['tenants']), 1)
        self.assertEqual(response.data['tenants'][0]['tenant_id'], str(self.tenant.id))

    @patch('control_plane.views.tenant_user_exists')
    @patch('control_plane.views.get_tenant_db_alias')
    def test_lookup_throttling(self, mock_get_alias, mock_user_exists):
        mock_get_alias.return_value = 'tenant_alias'
        mock_user_exists.return_value = True
        rate_settings = dict(settings.REST_FRAMEWORK)
        rate_settings['DEFAULT_THROTTLE_RATES'] = {'tenant_lookup': '1/min'}

        with override_settings(REST_FRAMEWORK=rate_settings):
            first = self.client.post('/api/control-plane/tenant-lookup/', {'email': 'user@example.com'}, format='json')
            second = self.client.post('/api/control-plane/tenant-lookup/', {'email': 'user@example.com'}, format='json')

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
