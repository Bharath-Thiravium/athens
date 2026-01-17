from unittest.mock import patch
import uuid

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class TenantLoginTests(APITestCase):
    databases = {'default'}

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='tenantuser',
            password='Password123!',
            user_type='projectadmin',
        )
        self.user.athens_tenant_id = uuid.uuid4()
        self.user.save()
        self.user._state.db = 'tenant_alias'

    @patch('authentication.tenant_login_views.authenticate_tenant_user')
    @patch('authentication.tenant_login_views.get_tenant_db_alias')
    def test_tenant_login_success(self, mock_get_alias, mock_authenticate):
        mock_get_alias.return_value = 'tenant_alias'
        mock_authenticate.return_value = self.user

        response = self.client.post(
            '/authentication/login/tenant/',
            {
                'tenant_id': str(self.user.athens_tenant_id),
                'email': 'user@example.com',
                'password': 'Password123!'
            },
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['tenant_id'], str(self.user.athens_tenant_id))

    @patch('authentication.tenant_login_views.get_tenant_db_alias')
    def test_tenant_login_missing_fields(self, mock_get_alias):
        response = self.client.post(
            '/authentication/login/tenant/',
            {
                'tenant_id': 'tenant-id',
                'password': 'Password123!'
            },
            format='json',
        )

        self.assertEqual(response.status_code, 400)
