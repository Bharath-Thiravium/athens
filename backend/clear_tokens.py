#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

# Clear all outstanding tokens
OutstandingToken.objects.all().delete()
BlacklistedToken.objects.all().delete()
print("All tokens cleared from database")