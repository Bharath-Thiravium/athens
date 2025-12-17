#!/usr/bin/env python3

"""
Script to create comprehensive permit types for the PTW system.
This script creates all the permit types defined in the management command.
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

def create_comprehensive_permit_types():
    """Create comprehensive permit types"""
    
    permit_types = [
        # HOT WORK PERMITS
        {'name': 'Hot Work - Arc Welding', 'category': 'hot_work', 'description': 'Electric arc welding (SMAW, GMAW, GTAW)', 'color_code': '#ff4d4f', 'risk_level': 'high', 'validity_hours': 8, 'requires_gas_testing': True, 'requires_fire_watch': True, 'requires_isolation': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls'], 'min_personnel_required': 2},
        {'name': 'Hot Work - Gas Welding/Cutting', 'category': 'hot_work', 'description': 'Oxy-fuel welding and cutting', 'color_code': '#ff4d4f', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_gas_testing': True, 'requires_fire_watch': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls'], 'min_personnel_required': 2},
        {'name': 'Hot Work - Plasma Cutting', 'category': 'hot_work', 'description': 'Plasma arc cutting operations', 'color_code': '#ff7a45', 'risk_level': 'high', 'validity_hours': 8, 'requires_fire_watch': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls']},
        {'name': 'Hot Work - Grinding/Cutting', 'category': 'hot_work', 'description': 'Abrasive wheel grinding and cutting', 'color_code': '#ff7a45', 'risk_level': 'medium', 'validity_hours': 8, 'requires_fire_watch': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'face_shield']},
        {'name': 'Hot Work - Brazing/Soldering', 'category': 'hot_work', 'description': 'Brazing and soldering operations', 'color_code': '#ffa940', 'risk_level': 'medium', 'validity_hours': 8, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles']},

        # CONFINED SPACE PERMITS
        {'name': 'Confined Space - Tank Entry', 'category': 'confined_space', 'description': 'Entry into storage tanks and vessels', 'color_code': '#722ed1', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_gas_testing': True, 'requires_isolation': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'harness', 'respirator'], 'min_personnel_required': 3},
        {'name': 'Confined Space - Manhole Entry', 'category': 'confined_space', 'description': 'Entry into manholes and underground spaces', 'color_code': '#722ed1', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_gas_testing': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'harness', 'respirator'], 'min_personnel_required': 3},
        {'name': 'Confined Space - Vessel Entry', 'category': 'confined_space', 'description': 'Entry into pressure vessels and reactors', 'color_code': '#722ed1', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_gas_testing': True, 'requires_isolation': True, 'requires_medical_surveillance': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'harness', 'respirator', 'coveralls'], 'min_personnel_required': 4},

        # ELECTRICAL WORK PERMITS
        {'name': 'Electrical - High Voltage (>1kV)', 'category': 'electrical', 'description': 'Work on HV electrical systems', 'color_code': '#fadb14', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_isolation': True, 'requires_training_verification': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'electrical_ppe'], 'min_personnel_required': 2},
        {'name': 'Electrical - Low Voltage (<1kV)', 'category': 'electrical', 'description': 'Work on LV electrical systems', 'color_code': '#fadb14', 'risk_level': 'high', 'validity_hours': 8, 'requires_isolation': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles']},
        {'name': 'Electrical - Live Work', 'category': 'electrical', 'description': 'Work on energized equipment', 'color_code': '#ff4d4f', 'risk_level': 'extreme', 'validity_hours': 4, 'requires_training_verification': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'electrical_ppe', 'face_shield'], 'min_personnel_required': 2},

        # WORK AT HEIGHT PERMITS
        {'name': 'Height - Scaffolding Work', 'category': 'height', 'description': 'Work on scaffolds above 6 feet', 'color_code': '#1890ff', 'risk_level': 'high', 'validity_hours': 12, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'harness']},
        {'name': 'Height - Ladder Work', 'category': 'height', 'description': 'Work using ladders above 6 feet', 'color_code': '#40a9ff', 'risk_level': 'medium', 'validity_hours': 8, 'mandatory_ppe': ['helmet', 'gloves', 'shoes']},
        {'name': 'Height - Rope Access', 'category': 'height', 'description': 'Industrial rope access work', 'color_code': '#096dd9', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_training_verification': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'harness', 'rope_access_ppe'], 'min_personnel_required': 2},

        # EXCAVATION PERMITS
        {'name': 'Excavation - Manual Digging', 'category': 'excavation', 'description': 'Hand digging operations', 'color_code': '#8c8c8c', 'risk_level': 'medium', 'validity_hours': 8, 'mandatory_ppe': ['helmet', 'gloves', 'shoes']},
        {'name': 'Excavation - Mechanical', 'category': 'excavation', 'description': 'Machine excavation operations', 'color_code': '#595959', 'risk_level': 'high', 'validity_hours': 8, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis']},

        # CHEMICAL WORK PERMITS
        {'name': 'Chemical - Hazardous Materials', 'category': 'chemical', 'description': 'Work with hazardous chemicals', 'color_code': '#fa8c16', 'risk_level': 'high', 'validity_hours': 8, 'requires_gas_testing': True, 'requires_medical_surveillance': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'chemical_suit', 'respirator']},
        {'name': 'Chemical - Corrosive Materials', 'category': 'chemical', 'description': 'Work with acids and bases', 'color_code': '#fa541c', 'risk_level': 'high', 'validity_hours': 8, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'chemical_suit', 'face_shield']},

        # CRANE & LIFTING PERMITS
        {'name': 'Crane - Mobile Crane Operations', 'category': 'crane_lifting', 'description': 'Mobile crane lifting operations', 'color_code': '#52c41a', 'risk_level': 'high', 'validity_hours': 8, 'requires_training_verification': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis'], 'min_personnel_required': 2},
        {'name': 'Crane - Overhead Crane', 'category': 'crane_lifting', 'description': 'Overhead bridge crane operations', 'color_code': '#73d13d', 'risk_level': 'medium', 'validity_hours': 8, 'mandatory_ppe': ['helmet', 'gloves', 'shoes']},

        # COLD WORK PERMITS
        {'name': 'Cold Work - General Maintenance', 'category': 'cold_work', 'description': 'General maintenance work', 'color_code': '#13c2c2', 'risk_level': 'low', 'validity_hours': 12, 'mandatory_ppe': ['helmet', 'gloves', 'shoes']},
        {'name': 'Cold Work - Mechanical Work', 'category': 'cold_work', 'description': 'Mechanical maintenance work', 'color_code': '#36cfc9', 'risk_level': 'low', 'validity_hours': 12, 'requires_isolation': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles']},

        # SPECIALIZED PERMITS
        {'name': 'Radiography - Industrial X-Ray', 'category': 'specialized', 'description': 'Industrial radiography work', 'color_code': '#f759ab', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_training_verification': True, 'requires_medical_surveillance': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'radiation_badge', 'lead_apron'], 'min_personnel_required': 2},
        {'name': 'Pressure Testing - Hydrostatic', 'category': 'specialized', 'description': 'Hydrostatic pressure testing', 'color_code': '#ff85c0', 'risk_level': 'high', 'validity_hours': 8, 'requires_isolation': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'face_shield']},
        {'name': 'Asbestos - Removal/Abatement', 'category': 'specialized', 'description': 'Asbestos removal work', 'color_code': '#d3adf7', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_gas_testing': True, 'requires_medical_surveillance': True, 'requires_training_verification': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'respirator', 'disposable_coveralls'], 'min_personnel_required': 2},

        # AIRLINE OPERATIONS
        {'name': 'Airline - Aircraft Maintenance', 'category': 'airline', 'description': 'Aircraft maintenance and inspection', 'color_code': '#1890ff', 'risk_level': 'high', 'validity_hours': 8, 'requires_training_verification': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis']},
        {'name': 'Airline - Engine Work', 'category': 'airline', 'description': 'Aircraft engine maintenance', 'color_code': '#096dd9', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_training_verification': True, 'requires_isolation': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'ear_protection'], 'min_personnel_required': 2},
        {'name': 'Airline - Fuel System Work', 'category': 'airline', 'description': 'Aircraft fuel system maintenance', 'color_code': '#ff4d4f', 'risk_level': 'extreme', 'validity_hours': 6, 'requires_gas_testing': True, 'requires_fire_watch': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls'], 'min_personnel_required': 2},

        # BIOLOGICAL HAZARDS
        {'name': 'Biological - Infectious Materials', 'category': 'biological', 'description': 'Work with infectious biological materials', 'color_code': '#52c41a', 'risk_level': 'extreme', 'validity_hours': 8, 'requires_medical_surveillance': True, 'requires_training_verification': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls', 'respirator'], 'min_personnel_required': 2},
        {'name': 'Biological - Laboratory Work', 'category': 'biological', 'description': 'Biological laboratory operations', 'color_code': '#73d13d', 'risk_level': 'high', 'validity_hours': 8, 'requires_medical_surveillance': True, 'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls']},
    ]

    created_count = 0
    updated_count = 0
    
    for permit_data in permit_types:
        permit_type, created = PermitType.objects.get_or_create(
            name=permit_data['name'],
            defaults=permit_data
        )
        if created:
            created_count += 1
            print(f"Created: {permit_type.name}")
        else:
            # Update existing permit type
            for key, value in permit_data.items():
                setattr(permit_type, key, value)
            permit_type.save()
            updated_count += 1
            print(f"Updated: {permit_type.name}")

    print(f"\nSummary:")
    print(f"Created: {created_count} permit types")
    print(f"Updated: {updated_count} permit types")
    print(f"Total: {len(permit_types)} permit types processed")
    
    # Show current count in database
    total_in_db = PermitType.objects.count()
    print(f"Total permit types in database: {total_in_db}")
    
    # Show categories
    categories = PermitType.objects.values_list('category', flat=True).distinct()
    print(f"Categories: {list(categories)}")

if __name__ == '__main__':
    create_comprehensive_permit_types()