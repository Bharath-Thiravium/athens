from django.contrib.auth.backends import ModelBackend
from .models import CustomUser
from .tenant_models import AthensTenant
from .sap_sync import SAPAuthValidator
from .usertype_utils import is_master_type
import logging

logger = logging.getLogger(__name__)

class SAPIntegratedAuthBackend(ModelBackend):
    """
    SAP-Athens Integration Authentication Backend
    
    ENTRY POINT RULE:
    - Only accepts SAP-issued credentials with usertype: master
    - Validates Athens service is active for the company
    - All other users are Athens-internal only
    """
    
    def __init__(self):
        self.sap_validator = SAPAuthValidator()
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        logger.info(f"SAP Auth: Attempting authentication for '{username}'")
        
        if username is None or password is None:
            logger.warning("SAP Auth: Missing username or password")
            return None
            
        try:
            user = CustomUser.objects.get(username=username)
            logger.info(f"SAP Auth: User '{username}' found")
            
            # SAP ENTRY POINT VALIDATION
            if is_master_type(user.user_type):
                logger.info(f"SAP Auth: Master user detected - validating SAP credentials")
                return self._authenticate_sap_master(user, password)
            else:
                logger.info(f"SAP Auth: Athens internal user - standard authentication")
                return self._authenticate_athens_user(user, password)
                
        except CustomUser.DoesNotExist:
            logger.warning(f"SAP Auth: User '{username}' not found")
            return None
    
    def _authenticate_sap_master(self, user, password):
        """
        Authenticate SAP-issued master credentials
        
        CRITICAL: Validates credentials against SAP in real-time
        Athens validates service activation status
        """
        # Real-time SAP credential validation
        if not self.sap_validator.validate_master_credentials(user.username, password):
            logger.warning(f"SAP Auth: SAP rejected credentials for {user.username}")
            return None
        
        # Validate user is active
        if not user.is_active:
            logger.warning(f"SAP Auth: Master user {user.username} is inactive")
            return None
        
        # Validate Athens service is active for this company
        user_tenant_id = getattr(user, 'athens_tenant_id', None)
        if user_tenant_id:
            try:
                tenant = AthensTenant.objects.get(id=user_tenant_id)
                if not tenant.is_active:
                    logger.warning(f"SAP Auth: Athens service disabled for tenant {user_tenant_id}")
                    return None
                logger.info(f"SAP Auth: Athens service active for tenant {user_tenant_id}")
            except AthensTenant.DoesNotExist:
                logger.warning(f"SAP Auth: Tenant {user_tenant_id} not found")
                return None
        
        logger.info(f"SAP Auth: Master user {user.username} authenticated successfully")
        return user
    
    def _authenticate_athens_user(self, user, password):
        """
        Authenticate Athens-internal users (non-master)
        
        Standard Django authentication for Athens-managed users
        """
        if not user.check_password(password):
            logger.warning(f"Athens Auth: Invalid password for user {user.username}")
            return None
        
        if not user.is_active:
            logger.warning(f"Athens Auth: User {user.username} is inactive")
            return None
        
        logger.info(f"Athens Auth: User {user.username} authenticated successfully")
        return user
        
    def get_user(self, user_id):
        logger.debug(f"SAP Auth: Getting user with id {user_id}")
        try:
            user = CustomUser.objects.get(pk=user_id, is_active=True)
            
            # Additional validation for master users
            if is_master_type(user.user_type):
                user_tenant_id = getattr(user, 'athens_tenant_id', None)
                if user_tenant_id:
                    try:
                        tenant = AthensTenant.objects.get(id=user_tenant_id)
                        if not tenant.is_active:
                            logger.warning(f"SAP Auth: Athens service disabled for tenant {user_tenant_id}")
                            return None
                    except AthensTenant.DoesNotExist:
                        logger.warning(f"SAP Auth: Tenant {user_tenant_id} not found")
                        return None
            
            return user
        except CustomUser.DoesNotExist:
            logger.warning(f"SAP Auth: User with id {user_id} not found")
            return None
