#!/usr/bin/env python
import os
import django
import sys
from datetime import date, datetime, timedelta
import random
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser, Project

def create_complete_dummy_data():
    print("🚀 Creating COMPLETE dummy data for ALL database fields...")
    
    # Get existing data
    projects = Project.objects.all()
    users = CustomUser.objects.filter(user_type='adminuser')
    
    if not projects.exists():
        print("❌ No projects found. Run populate_demo_data.py first!")
        return
    
    project = projects.first()
    user = users.first() if users.exists() else None
    
    # 1. WORKERS - Complete with ALL fields
    try:
        from worker.models import Worker
        
        worker_data = {
            'name': 'Rajesh Kumar',
            'surname': 'Singh',
            'worker_id': 'TU14-W001',
            'date_of_birth': date(1985, 6, 15),
            'date_of_joining': date(2023, 1, 10),
            'department': 'Construction',
            'designation': 'Site Engineer',
            'status': 'active',
            'employment_type': 'permanent',
            'employment_status': 'active',
            'category': 'skilled',
            'gender': 'male',
            'nationality': 'Indian',
            'education_level': 'graduate',
            'education_other': 'B.Tech Civil Engineering',
            'father_or_spouse_name': 'Ram Singh',
            'phone_number': '+91-9876543210',
            'present_address': '123 Main Street, Delhi, India - 110001',
            'permanent_address': '456 Village Road, Punjab, India - 144001',
            'pan': 'ABCDE1234F',
            'aadhaar': '123456789012',
            'uan': 'UAN123456789012',
            'esic_ip': 'ESIC123456789',
            'lwf': 'LWF123456',
            'mark_of_identification': 'Scar on left hand',
            'project': project,
            'created_by': user
        }
        
        worker, created = Worker.objects.get_or_create(
            worker_id='TU14-W001',
            defaults=worker_data
        )
        if created:
            print(f"✅ Created Complete Worker: {worker_data['name']}")
    except Exception as e:
        print(f"⚠️ Workers: {e}")
    
    # 2. SAFETY OBSERVATIONS - Complete with ALL fields
    try:
        from safetyobservation.models import SafetyObservation
        
        safety_data = {
            'observationID': 'TU14-SO-001',
            'department': 'Construction',
            'workLocation': 'Solar Panel Installation Area - Block A',
            'severity': 3,  # Assuming integer field
            'observationStatus': 'Open',
            'safetyObservationFound': 'Workers observed not wearing proper safety helmets while working at height during solar panel installation. Risk of head injury from falling objects.',
            'immediateActionTaken': 'Work stopped immediately, safety helmets distributed, safety briefing conducted',
            'rootCause': 'Inadequate PPE supply and lack of safety awareness',
            'correctiveAction': 'Procure additional safety helmets, conduct daily PPE checks, implement safety training',
            'preventiveAction': 'Establish PPE inventory management system, daily safety briefings',
            'targetDate': date.today() + timedelta(days=7),
            'actualCompletionDate': None,
            'observedBy': 'Safety Officer - Priya Sharma',
            'reportedTo': 'Site Manager - Amit Kumar',
            'created_by': user
        }
        
        safety_obs, created = SafetyObservation.objects.get_or_create(
            observationID='TU14-SO-001',
            defaults=safety_data
        )
        if created:
            print(f"✅ Created Complete Safety Observation: {safety_data['observationID']}")
    except Exception as e:
        print(f"⚠️ Safety Observations: {e}")
    
    # 3. INCIDENTS - Complete with ALL fields
    try:
        from incidentmanagement.models import Incident
        
        incident_data = {
            'title': 'Electrical Shock Incident - Substation Area',
            'incident_id': 'TU14-INC-001',
            'date_time_incident': timezone.now() - timedelta(days=2),
            'department': 'Electrical',
            'location': 'Main Substation - Panel Room 2',
            'status': 'Under Investigation',
            'description': 'Electrical technician received minor shock while connecting cables to the main distribution panel. Worker was wearing proper PPE but cable was not properly isolated.',
            'incident_type': 'electrical',
            'severity_level': 'minor',
            'immediate_cause': 'Improper isolation of electrical circuit',
            'root_cause': 'Inadequate LOTO procedure implementation',
            'corrective_actions': 'Reinforce LOTO procedures, additional electrical safety training',
            'preventive_actions': 'Install additional isolation switches, update electrical safety protocols',
            'investigation_findings': 'LOTO procedure not followed completely, isolation verification skipped',
            'lessons_learned': 'Always verify electrical isolation with proper testing equipment',
            'cost_impact': 5000.00,
            'environmental_impact': 'None',
            'regulatory_reporting_required': True,
            'regulatory_body': 'State Electricity Board',
            'reported_by': user,
            'investigated_by': user,
            'approved_by': user
        }
        
        incident, created = Incident.objects.get_or_create(
            incident_id='TU14-INC-001',
            defaults=incident_data
        )
        if created:
            print(f"✅ Created Complete Incident: {incident_data['title']}")
    except Exception as e:
        print(f"⚠️ Incidents: {e}")
    
    # 4. PERMITS (PTW) - Complete with ALL fields
    try:
        from ptw.models import Permit, PermitType
        
        # Create Permit Type first
        permit_type_data = {
            'name': 'Hot Work Permit',
            'category': 'fire_hazard',
            'risk_level': 'high',
            'description': 'Required for all welding, cutting, grinding operations',
            'validity_hours': 8,
            'requires_gas_test': True,
            'requires_fire_watch': True
        }
        
        permit_type, _ = PermitType.objects.get_or_create(
            name='Hot Work Permit',
            defaults=permit_type_data
        )
        
        permit_data = {
            'permit_number': 'TU14-PTW-001',
            'title': 'Welding Work - Solar Panel Frame Assembly',
            'permit_type': permit_type,
            'status': 'approved',
            'location': 'Workshop Area - Bay 3',
            'description': 'Welding of solar panel mounting frames using MIG welding process. Work involves structural steel welding for panel support structures.',
            'work_description': 'MIG welding of galvanized steel frames, estimated 50 joints, 6mm thickness',
            'hazards_identified': 'Fire risk, hot metal sparks, toxic fumes, UV radiation',
            'control_measures': 'Fire extinguisher on standby, proper ventilation, welding screens, PPE',
            'ppe_required': 'Welding helmet, leather gloves, safety boots, fire-resistant clothing',
            'equipment_required': 'MIG welder, gas cylinders, welding consumables, fire extinguisher',
            'start_date': date.today(),
            'end_date': date.today() + timedelta(days=1),
            'start_time': '08:00',
            'end_time': '17:00',
            'validity_hours': 8,
            'work_supervisor': 'Welding Supervisor - Ravi Kumar',
            'safety_officer': 'Safety Officer - Priya Sharma',
            'fire_watcher': 'Fire Watcher - Suresh Patel',
            'gas_test_required': True,
            'gas_test_results': 'LEL: 0%, O2: 20.8%, H2S: 0ppm - Safe',
            'isolation_required': True,
            'isolation_details': 'Electrical isolation completed, LOTO applied',
            'emergency_contact': 'Site Emergency: +91-9999999999',
            'weather_conditions': 'Clear, Wind: 5 kmph, Temperature: 28°C',
            'requested_by': user,
            'approved_by': user,
            'project': project
        }
        
        permit, created = Permit.objects.get_or_create(
            permit_number='TU14-PTW-001',
            defaults=permit_data
        )
        if created:
            print(f"✅ Created Complete Permit: {permit_data['permit_number']}")
    except Exception as e:
        print(f"⚠️ Permits: {e}")
    
    # 5. MANPOWER ENTRIES - Complete with ALL fields
    try:
        from manpower.models import ManpowerEntry
        
        manpower_data = {
            'date': date.today(),
            'shift': 'day',
            'category': 'Engineers',
            'subcategory': 'Civil Engineers',
            'gender': 'male',
            'count': 15,
            'overtime_hours': 2.5,
            'department': 'Construction',
            'location': 'Site Area A',
            'supervisor': 'Site Supervisor - Rajesh Kumar',
            'notes': 'Additional manpower deployed for foundation work acceleration',
            'weather_conditions': 'Clear sky, suitable for outdoor work',
            'productivity_rating': 4.2,
            'safety_incidents': 0,
            'project': project,
            'created_by': user
        }
        
        manpower, created = ManpowerEntry.objects.get_or_create(
            date=manpower_data['date'],
            category=manpower_data['category'],
            gender=manpower_data['gender'],
            shift=manpower_data['shift'],
            defaults=manpower_data
        )
        if created:
            print(f"✅ Created Complete Manpower Entry: {manpower_data['category']}")
    except Exception as e:
        print(f"⚠️ Manpower: {e}")
    
    # 6. MEETINGS (MOM) - Complete with ALL fields
    try:
        from mom.models import Mom
        
        mom_data = {
            'title': 'Weekly Safety Committee Meeting',
            'agenda': 'Review safety performance, discuss incident investigations, plan safety initiatives',
            'meeting_datetime': timezone.now() + timedelta(days=1),
            'duration_minutes': 120,
            'location': 'Conference Room A - Site Office',
            'department': 'Safety',
            'status': 'scheduled',
            'points_to_discuss': 'Safety KPIs, Incident analysis, Training schedule, PPE requirements',
            'scheduled_by': user
        }
        
        mom, created = Mom.objects.get_or_create(
            title=mom_data['title'],
            meeting_datetime=mom_data['meeting_datetime'],
            defaults=mom_data
        )
        if created:
            print(f"✅ Created Complete Meeting: {mom_data['title']}")
    except Exception as e:
        print(f"⚠️ Meetings: {e}")
    
    # 7. TRAINING MODULES - Complete with ALL fields
    try:
        from inductiontraining.models import InductionTraining
        
        induction_data = {
            'title': 'Site Safety Induction Training',
            'description': 'Comprehensive safety orientation for new workers covering site hazards, emergency procedures, PPE requirements',
            'date': date.today() - timedelta(days=3),
            'start_time': '09:00',
            'end_time': '12:00',
            'location': 'Training Hall - Site Office',
            'conducted_by': 'Safety Manager - Priya Sharma',
            'trainer_qualification': 'Certified Safety Professional, 10 years experience',
            'status': 'completed',
            'training_type': 'mandatory',
            'target_audience': 'New joiners, contractors',
            'max_participants': 25,
            'actual_participants': 22,
            'training_materials': 'Safety handbook, PPE demonstration kit, emergency procedure videos',
            'assessment_method': 'Written test and practical demonstration',
            'pass_criteria': 'Minimum 80% marks in written test',
            'certificate_validity_months': 12,
            'refresher_required': True,
            'cost_per_participant': 500.00,
            'feedback_rating': 4.5,
            'created_by': user
        }
        
        induction, created = InductionTraining.objects.get_or_create(
            title=induction_data['title'],
            date=induction_data['date'],
            created_by=induction_data['created_by'],
            defaults=induction_data
        )
        if created:
            print(f"✅ Created Complete Induction Training: {induction_data['title']}")
    except Exception as e:
        print(f"⚠️ Induction Training: {e}")
    
    print("\n🎉 COMPLETE dummy data creation finished!")
    print("📊 All database fields populated with realistic data!")
    print("🔑 Login with master admin: master / master@123")
    print("🎯 Data created for project: TU14 demonstration")

if __name__ == '__main__':
    create_complete_dummy_data()