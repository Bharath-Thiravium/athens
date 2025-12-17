#!/usr/bin/env python3
"""
Clear old PTW notifications with incorrect links
"""

import os
import sys
import django

# Add the project root to Python path
sys.path.append('/home/athenas/Documents/project/10.07.2025 upatepro/upatepro/project')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()

from authentication.models_notification import Notification

def clear_old_ptw_notifications():
    """Clear old PTW notifications with incorrect test links"""
    
    try:
        # Find notifications with ptw-test links
        old_notifications = Notification.objects.filter(
            link__contains='ptw-test'
        )
        
        count = old_notifications.count()
        
        if count > 0:
            # Show details of notifications to be deleted
            for notif in old_notifications:
            
            # Delete them
            deleted_count, _ = old_notifications.delete()
        else:
            
        # Also clear any notifications with old permit links
        old_permit_notifications = Notification.objects.filter(
            link__contains='ptw/permits/view'
        )
        
        permit_count = old_permit_notifications.count()
        if permit_count > 0:
            for notif in old_permit_notifications:
            
            deleted_permit_count, _ = old_permit_notifications.delete()
        
        return True
        
    except Exception as e:
        return False

def main():
    
    success = clear_old_ptw_notifications()
    
    if success:
    else:

if __name__ == "__main__":
    main()
