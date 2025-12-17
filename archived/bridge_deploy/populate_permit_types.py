#!/usr/bin/env python3
"""
Script to populate the database with comprehensive permit types
Run this script to add all the permit types that the frontend expects
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from ptw.models import PermitType

def create_permit_types():
    """Create comprehensive permit types matching frontend expectations"""
    
    permit_types_data = [
        # Hot Work
        {
            'name': 'Hot Work - Arc Welding',
            'category': 'hot_work',
            'description': 'Electric arc welding operations',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_gas_testing': True,
            'requires_fire_watch': True,
            'requires_isolation': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls'],
            'safety_checklist': [
                'Fire watch assigned and trained',
                'Combustible materials removed 35ft radius',
                'Fire extinguisher readily available',
                'Hot work permit displayed at location',
                'Atmospheric testing completed',
                'Ventilation adequate for fume removal'
            ],
            'risk_factors': ['Fire hazard', 'Toxic fumes', 'Electric shock', 'Burns'],
            'control_measures': ['Fire watch', 'Area clearance', 'PPE', 'Ventilation'],
            'emergency_procedures': ['Fire suppression', 'Medical response', 'Evacuation']
        },
        {
            'name': 'Hot Work - Gas Welding/Cutting',
            'category': 'hot_work',
            'description': 'Oxy-acetylene welding and cutting operations',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_gas_testing': True,
            'requires_fire_watch': True,
            'requires_isolation': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'coveralls'],
            'safety_checklist': [
                'Gas cylinders secured and checked',
                'Flashback arrestors installed',
                'Fire watch assigned',
                'Area cleared of combustibles',
                'Emergency shutdown procedures reviewed'
            ]
        },
        {
            'name': 'Hot Work - Cutting & Grinding',
            'category': 'hot_work',
            'description': 'Mechanical cutting and grinding operations',
            'risk_level': 'medium',
            'validity_hours': 8,
            'requires_approval_levels': 1,
            'requires_fire_watch': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'face_shield']
        },
        {
            'name': 'Hot Work - Brazing & Soldering',
            'category': 'hot_work',
            'description': 'Brazing and soldering operations',
            'risk_level': 'medium',
            'validity_hours': 8,
            'requires_approval_levels': 1,
            'requires_fire_watch': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles']
        },
        
        # Confined Space
        {
            'name': 'Confined Space - Entry',
            'category': 'confined_space',
            'description': 'Entry into confined spaces',
            'risk_level': 'extreme',
            'validity_hours': 4,
            'requires_approval_levels': 3,
            'requires_gas_testing': True,
            'requires_medical_surveillance': True,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'harness', 'respirator'],
            'safety_checklist': [
                'Atmospheric testing completed (O2, LEL, H2S, CO)',
                'Continuous gas monitoring in place',
                'Mechanical ventilation operating',
                'Entry supervisor assigned and present',
                'Rescue team on standby',
                'Communication system established',
                'Emergency evacuation plan reviewed'
            ],
            'min_personnel_required': 3,
            'escalation_time_hours': 2
        },
        {
            'name': 'Confined Space - Non-Entry',
            'category': 'confined_space',
            'description': 'Work on confined spaces without entry',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_gas_testing': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'respirator']
        },
        
        # Electrical
        {
            'name': 'Electrical - High Voltage (>1kV)',
            'category': 'electrical',
            'description': 'High voltage electrical work above 1kV',
            'risk_level': 'extreme',
            'validity_hours': 4,
            'requires_approval_levels': 3,
            'requires_isolation': True,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'electrical_ppe', 'shoes', 'gloves'],
            'safety_checklist': [
                'Electrical isolation completed and verified',
                'LOTO procedures implemented',
                'Qualified electrician assigned',
                'Arc flash analysis completed',
                'Appropriate PPE worn',
                'Insulated tools used',
                'Electrical safety boundaries established'
            ],
            'min_personnel_required': 2
        },
        {
            'name': 'Electrical - Low Voltage (<1kV)',
            'category': 'electrical',
            'description': 'Low voltage electrical work below 1kV',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_isolation': True,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'electrical_ppe', 'shoes', 'gloves']
        },
        {
            'name': 'Electrical - Live Work',
            'category': 'electrical',
            'description': 'Work on live electrical equipment',
            'risk_level': 'extreme',
            'validity_hours': 2,
            'requires_approval_levels': 3,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'electrical_ppe', 'shoes', 'gloves', 'face_shield'],
            'min_personnel_required': 2
        },
        
        # Work at Height
        {
            'name': 'Work at Height - Scaffolding',
            'category': 'height',
            'description': 'Work using scaffolding systems',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'mandatory_ppe': ['helmet', 'harness', 'shoes', 'gloves'],
            'safety_checklist': [
                'Fall protection system in place',
                'Guardrails installed where required',
                'Weather conditions acceptable',
                'Rescue plan established',
                'Exclusion zone established below',
                'Equipment inspected by competent person'
            ]
        },
        {
            'name': 'Work at Height - Ladder Work',
            'category': 'height',
            'description': 'Work using ladders',
            'risk_level': 'medium',
            'validity_hours': 8,
            'requires_approval_levels': 1,
            'mandatory_ppe': ['helmet', 'harness', 'shoes', 'gloves']
        },
        {
            'name': 'Work at Height - Rope Access',
            'category': 'height',
            'description': 'Rope access work',
            'risk_level': 'extreme',
            'validity_hours': 8,
            'requires_approval_levels': 3,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'rope_access_ppe', 'shoes', 'gloves'],
            'min_personnel_required': 2
        },
        
        # Excavation
        {
            'name': 'Excavation - Manual Digging',
            'category': 'excavation',
            'description': 'Manual excavation work',
            'risk_level': 'medium',
            'validity_hours': 8,
            'requires_approval_levels': 1,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes'],
            'safety_checklist': [
                'Underground utilities located and marked',
                'Soil conditions assessed',
                'Proper sloping or shoring in place',
                'Safe entry/exit provided',
                'Competent person assigned'
            ]
        },
        {
            'name': 'Excavation - Mechanical',
            'category': 'excavation',
            'description': 'Mechanical excavation work',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis']
        },
        
        # Chemical
        {
            'name': 'Chemical Handling - Hazardous',
            'category': 'chemical',
            'description': 'Handling of hazardous chemicals',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_gas_testing': True,
            'requires_medical_surveillance': True,
            'mandatory_ppe': ['chemical_suit', 'respirator', 'gloves', 'goggles'],
            'safety_checklist': [
                'SDS reviewed for all chemicals',
                'Chemical compatibility verified',
                'Spill response kit available',
                'Emergency shower/eyewash accessible',
                'Proper ventilation provided',
                'Waste disposal plan in place'
            ]
        },
        {
            'name': 'Chemical Handling - Corrosive',
            'category': 'chemical',
            'description': 'Handling of corrosive chemicals',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'mandatory_ppe': ['chemical_suit', 'face_shield', 'gloves', 'goggles']
        },
        
        # Crane & Lifting
        {
            'name': 'Crane Operations - Mobile Crane',
            'category': 'crane_lifting',
            'description': 'Mobile crane operations',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis'],
            'safety_checklist': [
                'Crane operator certified and current',
                'Crane inspection completed',
                'Lift plan prepared and reviewed',
                'Load weight verified',
                'Rigging equipment inspected',
                'Exclusion zone established'
            ],
            'min_personnel_required': 2
        },
        {
            'name': 'Crane Operations - Overhead Crane',
            'category': 'crane_lifting',
            'description': 'Overhead crane operations',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis']
        },
        {
            'name': 'Rigging Operations',
            'category': 'crane_lifting',
            'description': 'Rigging and slinging operations',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis']
        },
        
        # Cold Work
        {
            'name': 'Cold Work - General Maintenance',
            'category': 'cold_work',
            'description': 'General maintenance work',
            'risk_level': 'low',
            'validity_hours': 8,
            'requires_approval_levels': 1,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes'],
            'safety_checklist': [
                'Work area inspected for hazards',
                'Tools and equipment inspected',
                'LOTO procedures followed if required',
                'Housekeeping standards maintained'
            ]
        },
        {
            'name': 'Cold Work - Mechanical',
            'category': 'cold_work',
            'description': 'Mechanical maintenance work',
            'risk_level': 'medium',
            'validity_hours': 8,
            'requires_approval_levels': 1,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles']
        },
        
        # Specialized
        {
            'name': 'Radiography Work',
            'category': 'specialized',
            'description': 'Industrial radiography work',
            'risk_level': 'extreme',
            'validity_hours': 4,
            'requires_approval_levels': 3,
            'requires_training_verification': True,
            'requires_medical_surveillance': True,
            'mandatory_ppe': ['radiation_badge', 'lead_apron', 'helmet', 'gloves'],
            'min_personnel_required': 2
        },
        {
            'name': 'Pressure Testing',
            'category': 'specialized',
            'description': 'Pressure testing operations',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'face_shield']
        },
        {
            'name': 'Asbestos Work',
            'category': 'specialized',
            'description': 'Asbestos handling and removal',
            'risk_level': 'extreme',
            'validity_hours': 4,
            'requires_approval_levels': 3,
            'requires_training_verification': True,
            'requires_medical_surveillance': True,
            'mandatory_ppe': ['disposable_coveralls', 'respirator', 'gloves', 'goggles']
        },
        {
            'name': 'Demolition Work',
            'category': 'specialized',
            'description': 'Demolition operations',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'goggles', 'ear_protection']
        },
        
        # Airline Operations
        {
            'name': 'Airline - Aircraft Maintenance',
            'category': 'airline',
            'description': 'General aircraft maintenance',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis'],
            'safety_checklist': [
                'Aircraft maintenance manual consulted',
                'Airworthiness directives reviewed',
                'Ground support equipment inspected',
                'Communication with air traffic control established',
                'Safety zones established around aircraft',
                'Fire suppression equipment available',
                'Personnel certified for aircraft type'
            ]
        },
        {
            'name': 'Airline - Engine Work',
            'category': 'airline',
            'description': 'Aircraft engine maintenance',
            'risk_level': 'extreme',
            'validity_hours': 4,
            'requires_approval_levels': 3,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis', 'ear_protection']
        },
        {
            'name': 'Airline - Fuel System Work',
            'category': 'airline',
            'description': 'Aircraft fuel system maintenance',
            'risk_level': 'extreme',
            'validity_hours': 4,
            'requires_approval_levels': 3,
            'requires_gas_testing': True,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis', 'coveralls']
        },
        {
            'name': 'Airline - Avionics Work',
            'category': 'airline',
            'description': 'Aircraft avionics and electrical systems',
            'risk_level': 'high',
            'validity_hours': 8,
            'requires_approval_levels': 2,
            'requires_training_verification': True,
            'mandatory_ppe': ['helmet', 'electrical_ppe', 'shoes', 'gloves']
        },
        {
            'name': 'Airline - Ground Support Equipment',
            'category': 'airline',
            'description': 'Ground support equipment operations',
            'risk_level': 'medium',
            'validity_hours': 8,
            'requires_approval_levels': 1,
            'mandatory_ppe': ['helmet', 'gloves', 'shoes', 'high_vis']
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for permit_data in permit_types_data:
        permit_type, created = PermitType.objects.get_or_create(
            name=permit_data['name'],
            defaults=permit_data
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {permit_type.name}")
        else:
            # Update existing permit type with new data
            for key, value in permit_data.items():
                if key != 'name':  # Don't update the name
                    setattr(permit_type, key, value)
            permit_type.save()
            updated_count += 1
            print(f"↻ Updated: {permit_type.name}")
    
    print(f"\n✅ Summary:")
    print(f"   Created: {created_count} permit types")
    print(f"   Updated: {updated_count} permit types")
    print(f"   Total permit types in database: {PermitType.objects.count()}")
    print(f"   Active permit types: {PermitType.objects.filter(is_active=True).count()}")

if __name__ == '__main__':
    print("🚀 Populating permit types database...")
    create_permit_types()
    print("✅ Done!")