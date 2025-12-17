#!/usr/bin/env python3

"""
Script to add airline permit types to the database
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ptw.models import PermitType

def add_airline_permits():
    """Add airline permit types"""
    
    airline_permits = [
        {
            'name': 'Airline - Aircraft Maintenance',
            'category': 'airline',
            'description': 'Aircraft maintenance and inspection',
            'color_code': '#1890ff',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis'],
            'is_active': True
        },
        {
            'name': 'Airline - Engine Work',
            'category': 'airline',
            'description': 'Aircraft engine maintenance',
            'color_code': '#096dd9',
            'risk_level': 'extreme',
            'validity_hours': 8,
            'requires_training_verification': True,
            'requires_isolation': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'ear_protection'],
            'min_personnel_required': 2,
            'is_active': True
        },
        {
            'name': 'Airline - Fuel System Work',
            'category': 'airline',
            'description': 'Aircraft fuel system maintenance',
            'color_code': '#ff4d4f',
            'risk_level': 'extreme',
            'validity_hours': 6,
            'requires_gas_testing': True,
            'requires_fire_watch': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls'],
            'min_personnel_required': 2,
            'is_active': True
        },
        {
            'name': 'Airline - Avionics Work',
            'category': 'airline',
            'description': 'Aircraft electronics and avionics',
            'color_code': '#fadb14',
            'risk_level': 'medium',
            'validity_hours': 8,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles'],
            'is_active': True
        },
        {
            'name': 'Airline - Ground Support Equipment',
            'category': 'airline',
            'description': 'GSE maintenance and operation',
            'color_code': '#52c41a',
            'risk_level': 'medium',
            'validity_hours': 8,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis'],
            'is_active': True
        }
    ]
    
    created_count = 0
    for permit_data in airline_permits:
        permit_type, created = PermitType.objects.get_or_create(
            name=permit_data['name'],
            defaults=permit_data
        )
        if created:
            created_count += 1
        else:
    
    
    # Show final count
    total_permits = PermitType.objects.count()
    airline_permits = PermitType.objects.filter(category='airline').count()

if __name__ == '__main__':
    add_airline_permits()