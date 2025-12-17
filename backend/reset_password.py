#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser

# Reset master admin password
master = CustomUser.objects.get(username='ilaiaraja')
master.set_password('admin123')
master.save()
print(f"Password reset for {master.username}")
print("New password: admin123")