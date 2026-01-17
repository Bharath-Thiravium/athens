"""
Celery tasks for SAP credential synchronization
"""

from celery import shared_task
from .sap_sync import SAPCredentialSync
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def sync_sap_credentials_task(self):
    """
    Automated SAP credential synchronization task
    Runs periodically to keep Athens in sync with SAP
    """
    try:
        sync_service = SAPCredentialSync()
        success = sync_service.sync_master_credentials()
        
        if success:
            logger.info("Automated SAP credential sync completed successfully")
            return "SAP sync completed"
        else:
            logger.error("Automated SAP credential sync failed")
            raise Exception("SAP sync failed")
            
    except Exception as exc:
        logger.error(f"SAP credential sync task failed: {exc}")
        raise self.retry(exc=exc, countdown=300)  # Retry after 5 minutes