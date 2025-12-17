#!/usr/bin/env python3

"""
Script to clean up duplicate permit types and ensure only the correct 25 types exist
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ptw.models import PermitType
from collections import Counter

def cleanup_permit_types():
    """Clean up duplicate permit types"""
    
    # First, let's see what we have
    all_types = PermitType.objects.all()
    
    # Check for duplicates by name
    names = [pt.name for pt in all_types]
    name_counts = Counter(names)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    if duplicates:
        for name, count in duplicates.items():
            
            # Keep only the first one, delete the rest
            duplicate_records = PermitType.objects.filter(name=name).order_by('id')
            for record in duplicate_records[1:]:  # Skip the first one
                record.delete()
    
    # Define the correct 25 permit types we want
    correct_types = [
        {'name': 'Hot Work - Arc Welding', 'category': 'hot_work'},
        {'name': 'Hot Work - Gas Welding/Cutting', 'category': 'hot_work'},
        {'name': 'Hot Work - Cutting & Grinding', 'category': 'hot_work'},
        {'name': 'Hot Work - Brazing & Soldering', 'category': 'hot_work'},
        {'name': 'Confined Space - Entry', 'category': 'confined_space'},
        {'name': 'Confined Space - Non-Entry', 'category': 'confined_space'},
        {'name': 'Electrical - High Voltage (>1kV)', 'category': 'electrical'},
        {'name': 'Electrical - Low Voltage (<1kV)', 'category': 'electrical'},
        {'name': 'Electrical - Live Work', 'category': 'electrical'},
        {'name': 'Work at Height - Scaffolding', 'category': 'height'},
        {'name': 'Work at Height - Ladder Work', 'category': 'height'},
        {'name': 'Work at Height - Rope Access', 'category': 'height'},
        {'name': 'Excavation - Manual Digging', 'category': 'excavation'},
        {'name': 'Excavation - Mechanical', 'category': 'excavation'},
        {'name': 'Chemical Handling - Hazardous', 'category': 'chemical'},
        {'name': 'Chemical Handling - Corrosive', 'category': 'chemical'},
        {'name': 'Crane Operations - Mobile Crane', 'category': 'crane_lifting'},
        {'name': 'Crane Operations - Overhead Crane', 'category': 'crane_lifting'},
        {'name': 'Rigging Operations', 'category': 'crane_lifting'},
        {'name': 'Cold Work - General Maintenance', 'category': 'cold_work'},
        {'name': 'Cold Work - Mechanical', 'category': 'cold_work'},
        {'name': 'Radiography Work', 'category': 'specialized'},
        {'name': 'Pressure Testing', 'category': 'specialized'},
        {'name': 'Asbestos Work', 'category': 'specialized'},
        {'name': 'Demolition Work', 'category': 'specialized'},
    ]
    
    correct_names = {pt['name'] for pt in correct_types}
    
    # Delete any permit types that are not in our correct list
    unwanted_types = PermitType.objects.exclude(name__in=correct_names)
    if unwanted_types.exists():
        for pt in unwanted_types:
            pt.delete()
    
    # Ensure all correct types exist
    for type_data in correct_types:
        pt, created = PermitType.objects.get_or_create(
            name=type_data['name'],
            defaults={
                'category': type_data['category'],
                'description': f"{type_data['name']} operations",
                'is_active': True,
                'risk_level': 'medium',
                'validity_hours': 8
            }
        )
        if created:
    
    # Final count
    final_count = PermitType.objects.count()
    
    # List all by category
    categories = {}
    for pt in PermitType.objects.all().order_by('category', 'name'):
        if pt.category not in categories:
            categories[pt.category] = []
        categories[pt.category].append(pt.name)
    
    for category, names in sorted(categories.items()):
        for name in names:

if __name__ == '__main__':
    cleanup_permit_types()