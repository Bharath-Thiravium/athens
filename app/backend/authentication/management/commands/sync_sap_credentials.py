"""
Django management command for SAP credential synchronization
"""

from django.core.management.base import BaseCommand
from authentication.sap_sync import SAPCredentialSync
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Synchronize master credentials from SAP to Athens'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if SAP configuration is missing'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Starting SAP credential synchronization...')
        
        sync_service = SAPCredentialSync()
        
        if sync_service.sync_master_credentials():
            self.stdout.write(
                self.style.SUCCESS('SAP credential sync completed successfully')
            )
        else:
            self.stdout.write(
                self.style.ERROR('SAP credential sync failed')
            )