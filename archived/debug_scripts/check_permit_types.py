#!/usr/bin/env python3

"""
Script to check permit types in the database for duplicates and list all types
"""

import os
import sys
import django

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ptw.models import PermitType
from collections import Counter

def check_permit_types():
    """Check all permit types in database"""
    
    # Get all permit types
    permit_types = PermitType.objects.all().order_by('category', 'name')
    
    print(f"Total permit types in database: {permit_types.count()}")
    print("=" * 80)
    
    # Check for duplicates by name
    names = [pt.name for pt in permit_types]
    name_counts = Counter(names)
    duplicates = {name: count for name, count in name_counts.items() if count > 1}
    
    if duplicates:
        print("DUPLICATE PERMIT TYPE NAMES FOUND:")
        for name, count in duplicates.items():
            print(f"  '{name}' appears {count} times")
            duplicate_records = PermitType.objects.filter(name=name)
            for record in duplicate_records:
                print(f"    ID: {record.id}, Category: {record.category}, Active: {record.is_active}")
        print("=" * 80)
    else:
        print("No duplicate permit type names found.")
        print("=" * 80)
    
    # Group by category
    categories = {}
    for pt in permit_types:
        if pt.category not in categories:
            categories[pt.category] = []
        categories[pt.category].append(pt)
    
    print("PERMIT TYPES BY CATEGORY:")
    print("=" * 80)
    
    for category, types in sorted(categories.items()):
        category_display = category.replace('_', ' ').title()
        print(f"\n{category_display} ({len(types)} types):")
        for i, pt in enumerate(types, 1):
            status = "Active" if pt.is_active else "Inactive"
            print(f"  {i:2d}. {pt.name} (ID: {pt.id}) - {status}")
    
    print("\n" + "=" * 80)
    print("SUMMARY:")
    print(f"Total categories: {len(categories)}")
    print(f"Total permit types: {len(permit_types)}")
    print(f"Active permit types: {PermitType.objects.filter(is_active=True).count()}")
    print(f"Inactive permit types: {PermitType.objects.filter(is_active=False).count()}")
    
    # Check for airline category specifically
    airline_types = PermitType.objects.filter(category='airline')
    if airline_types.exists():
        print(f"\nAIRLINE CATEGORY FOUND ({airline_types.count()} types):")
        for pt in airline_types:
            print(f"  - {pt.name} (ID: {pt.id})")
    else:
        print("\nNo airline category permit types found.")

if __name__ == '__main__':
    check_permit_types()