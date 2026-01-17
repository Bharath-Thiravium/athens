"""
SAP Credential Synchronization Service

Handles synchronization of master credentials between SAP and Athens.
"""

import requests
import logging
from django.conf import settings
from django.contrib.auth.hashers import make_password
from .models import CustomUser
from .tenant_models import AthensTenant
import os

logger = logging.getLogger(__name__)

class SAPCredentialSync:
    """Synchronizes master credentials from SAP to Athens"""
    
    def __init__(self):
        self.sap_api_url = os.getenv('SAP_API_URL')
        self.sap_api_key = os.getenv('SAP_API_KEY')
        self.sap_client_id = os.getenv('SAP_CLIENT_ID')
        
    def sync_master_credentials(self):
        """Fetch and sync master credentials from SAP"""
        if not self._validate_sap_config():
            logger.error("SAP configuration missing - skipping sync")
            return False
            
        try:
            # Fetch master users from SAP
            sap_masters = self._fetch_sap_masters()
            
            for sap_master in sap_masters:
                self._sync_master_user(sap_master)
                
            logger.info(f"Synced {len(sap_masters)} master credentials from SAP")
            return True
            
        except Exception as e:
            logger.error(f"SAP credential sync failed: {e}")
            return False
    
    def _validate_sap_config(self):
        """Validate SAP API configuration"""
        return all([self.sap_api_url, self.sap_api_key, self.sap_client_id])
    
    def _fetch_sap_masters(self):
        """Fetch master users from SAP API"""
        headers = {
            'Authorization': f'Bearer {self.sap_api_key}',
            'Content-Type': 'application/json',
            'X-SAP-Client-ID': self.sap_client_id
        }
        
        response = requests.get(
            f"{self.sap_api_url}/athens/master-users",
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        
        return response.json().get('master_users', [])
    
    def _sync_master_user(self, sap_master):
        """Sync individual master user from SAP"""
        username = sap_master['username']
        athens_tenant_id = sap_master['athens_tenant_id']
        is_active = sap_master.get('is_active', True)
        
        # Create or update master user
        user, created = CustomUser.objects.update_or_create(
            username=username,
            defaults={
                'user_type': 'master',
                'admin_type': 'master',
                'athens_tenant_id': athens_tenant_id,
                'is_active': is_active,
                'password': make_password(None)  # SAP manages passwords
            }
        )
        
        # Ensure tenant exists
        self._ensure_tenant_exists(athens_tenant_id, sap_master)
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} master user: {username} for tenant: {athens_tenant_id}")
    
    def _ensure_tenant_exists(self, tenant_id, sap_master):
        """Ensure Athens tenant record exists"""
        AthensTenant.objects.update_or_create(
            id=tenant_id,
            defaults={
                'master_admin_id': sap_master.get('user_id'),
                'tenant_name': sap_master.get('company_name', 'Unknown'),
                'is_active': sap_master.get('service_active', True),
                'enabled_modules': sap_master.get('enabled_modules', []),
                'enabled_menus': sap_master.get('enabled_menus', [])
            }
        )


class SAPAuthValidator:
    """Validates master credentials against SAP in real-time"""
    
    def __init__(self):
        self.sap_api_url = os.getenv('SAP_API_URL')
        self.sap_api_key = os.getenv('SAP_API_KEY')
    
    def validate_master_credentials(self, username, password):
        """Validate master credentials against SAP"""
        if not self.sap_api_url or not self.sap_api_key:
            logger.warning("SAP validation disabled - missing configuration")
            return False
            
        try:
            response = requests.post(
                f"{self.sap_api_url}/athens/validate-master",
                json={
                    'username': username,
                    'password': password
                },
                headers={
                    'Authorization': f'Bearer {self.sap_api_key}',
                    'Content-Type': 'application/json'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('valid', False)
            
            return False
            
        except Exception as e:
            logger.error(f"SAP credential validation failed: {e}")
            return False