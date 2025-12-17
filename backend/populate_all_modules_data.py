#!/usr/bin/env python
import os
import django
import sys
from datetime import date, datetime, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.models import CustomUser, Project

def create_all_modules_data():
    print("🚀 Creating dummy data for all EHS modules...")
    
    # Get existing data
    projects = Project.objects.all()[:3]  # Use first 3 projects
    users = CustomUser.objects.filter(user_type='adminuser')[:10]  # Use first 10 users
    
    if not projects.exists():
        print("❌ No projects found. Run populate_demo_data.py first!")
        return
    
    # 1. SAFETY OBSERVATIONS
    try:
        from safetyobservation.models import SafetyObservation
        
        safety_data = [
            {
                'observationID': 'SO-2024-001',
                'department': 'Engineering',
                'workLocation': 'Solar Panel Installation Area',
                'severity': 'Medium',
                'observationStatus': 'Open',
                'safetyObservationFound': 'Workers not wearing proper PPE while handling solar panels',
                'actionTaken': 'Immediate PPE distribution and safety briefing conducted',
                'project': projects[0],
                'created_by': users[0] if users.exists() else None
            },
            {
                'observationID': 'SO-2024-002',
                'department': 'Construction',
                'workLocation': 'Wind Turbine Foundation',
                'severity': 'High',
                'observationStatus': 'In Progress',
                'safetyObservationFound': 'Unsafe scaffolding setup near turbine base',
                'actionTaken': 'Scaffolding reinforced and safety barriers installed',
                'project': projects[1] if len(projects) > 1 else projects[0],
                'created_by': users[1] if len(users) > 1 else users[0]
            },
            {
                'observationID': 'SO-2024-003',
                'department': 'Quality',
                'workLocation': 'Manufacturing Floor',
                'severity': 'Low',
                'observationStatus': 'Closed',
                'safetyObservationFound': 'Minor housekeeping issues in assembly area',
                'actionTaken': 'Area cleaned and housekeeping schedule updated',
                'project': projects[2] if len(projects) > 2 else projects[0],
                'created_by': users[2] if len(users) > 2 else users[0]
            }
        ]
        
        for data in safety_data:
            obj, created = SafetyObservation.objects.get_or_create(
                observationID=data['observationID'],
                defaults=data
            )
            if created:
                print(f"✅ Created Safety Observation: {data['observationID']}")
    except Exception as e:
        print(f"⚠️ Safety Observations: {e}")
    
    # 2. INCIDENTS
    try:
        from incidentmanagement.models import Incident
        
        incident_data = [
            {
                'title': 'Minor Electrical Shock',
                'department': 'Electrical',
                'location': 'Substation Area',
                'status': 'Under Investigation',
                'description': 'Technician received minor shock while connecting cables',
                'incident_type': 'electrical',
                'severity': 'minor',
                'project': projects[0],
                'reported_by': users[0] if users.exists() else None
            },
            {
                'title': 'Equipment Malfunction',
                'department': 'Operations',
                'location': 'Turbine #3',
                'status': 'Resolved',
                'description': 'Hydraulic system failure in wind turbine',
                'incident_type': 'equipment',
                'severity': 'moderate',
                'project': projects[1] if len(projects) > 1 else projects[0],
                'reported_by': users[1] if len(users) > 1 else users[0]
            }
        ]
        
        for data in incident_data:
            obj, created = Incident.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                print(f"✅ Created Incident: {data['title']}")
    except Exception as e:
        print(f"⚠️ Incidents: {e}")
    
    # 3. PERMITS (PTW)
    try:
        from ptw.models import Permit, PermitType
        
        # Create Permit Types first
        permit_types_data = [
            {'name': 'Hot Work', 'category': 'fire_hazard', 'risk_level': 'high'},
            {'name': 'Confined Space', 'category': 'confined_space', 'risk_level': 'high'},
            {'name': 'Working at Height', 'category': 'height_work', 'risk_level': 'medium'},
            {'name': 'Electrical Work', 'category': 'electrical', 'risk_level': 'high'},
            {'name': 'Excavation', 'category': 'excavation', 'risk_level': 'medium'}
        ]
        
        for pt_data in permit_types_data:
            pt, created = PermitType.objects.get_or_create(
                name=pt_data['name'],
                defaults=pt_data
            )
            if created:
                print(f"✅ Created Permit Type: {pt_data['name']}")
        
        # Create Permits
        permit_data = [
            {
                'permit_number': 'PTW-2024-001',
                'title': 'Welding Work on Solar Panel Frames',
                'status': 'approved',
                'location': 'Solar Installation Area A',
                'description': 'Hot work permit for welding solar panel mounting frames',
                'project': projects[0],
                'requested_by': users[0] if users.exists() else None
            },
            {
                'permit_number': 'PTW-2024-002',
                'title': 'Turbine Maintenance Work',
                'status': 'pending',
                'location': 'Wind Turbine #5',
                'description': 'Working at height permit for turbine blade inspection',
                'project': projects[1] if len(projects) > 1 else projects[0],
                'requested_by': users[1] if len(users) > 1 else users[0]
            }
        ]
        
        for data in permit_data:
            obj, created = Permit.objects.get_or_create(
                permit_number=data['permit_number'],
                defaults=data
            )
            if created:
                print(f"✅ Created Permit: {data['permit_number']}")
    except Exception as e:
        print(f"⚠️ Permits: {e}")
    
    # 4. WORKERS
    try:
        from worker.models import Worker
        
        worker_data = [
            {
                'name': 'Rajesh Kumar',
                'department': 'Construction',
                'designation': 'Site Engineer',
                'status': 'active',
                'employee_id': 'EMP001',
                'project': projects[0],
                'created_by': users[0] if users.exists() else None
            },
            {
                'name': 'Priya Sharma',
                'department': 'Safety',
                'designation': 'Safety Officer',
                'status': 'active',
                'employee_id': 'EMP002',
                'project': projects[1] if len(projects) > 1 else projects[0],
                'created_by': users[1] if len(users) > 1 else users[0]
            },
            {
                'name': 'Amit Patel',
                'department': 'Quality',
                'designation': 'QC Inspector',
                'status': 'active',
                'employee_id': 'EMP003',
                'project': projects[2] if len(projects) > 2 else projects[0],
                'created_by': users[2] if len(users) > 2 else users[0]
            }
        ]
        
        for data in worker_data:
            obj, created = Worker.objects.get_or_create(
                employee_id=data['employee_id'],
                defaults=data
            )
            if created:
                print(f"✅ Created Worker: {data['name']}")
    except Exception as e:
        print(f"⚠️ Workers: {e}")
    
    # 5. MANPOWER ENTRIES
    try:
        from manpower.models import ManpowerEntry
        
        manpower_data = [
            {
                'date': date.today(),
                'category': 'Engineers',
                'gender': 'Male',
                'count': 15,
                'shift': 'Day',
                'project': projects[0]
            },
            {
                'date': date.today(),
                'category': 'Technicians',
                'gender': 'Female',
                'count': 8,
                'shift': 'Day',
                'project': projects[1] if len(projects) > 1 else projects[0]
            },
            {
                'date': date.today() - timedelta(days=1),
                'category': 'Supervisors',
                'gender': 'Male',
                'count': 5,
                'shift': 'Night',
                'project': projects[2] if len(projects) > 2 else projects[0]
            }
        ]
        
        for data in manpower_data:
            obj, created = ManpowerEntry.objects.get_or_create(
                date=data['date'],
                category=data['category'],
                gender=data['gender'],
                shift=data['shift'],
                project=data['project'],
                defaults=data
            )
            if created:
                print(f"✅ Created Manpower Entry: {data['category']} - {data['date']}")
    except Exception as e:
        print(f"⚠️ Manpower: {e}")
    
    # 6. MEETINGS (MOM)
    try:
        from mom.models import Mom
        
        mom_data = [
            {
                'title': 'Weekly Safety Review',
                'status': 'completed',
                'department': 'Safety',
                'location': 'Conference Room A',
                'agenda': 'Review safety incidents and preventive measures',
                'date': date.today(),
                'project': projects[0],
                'created_by': users[0] if users.exists() else None
            },
            {
                'title': 'Project Progress Meeting',
                'status': 'scheduled',
                'department': 'Engineering',
                'location': 'Site Office',
                'agenda': 'Discuss project milestones and upcoming tasks',
                'date': date.today() + timedelta(days=2),
                'project': projects[1] if len(projects) > 1 else projects[0],
                'created_by': users[1] if len(users) > 1 else users[0]
            }
        ]
        
        for data in mom_data:
            obj, created = Mom.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                defaults=data
            )
            if created:
                print(f"✅ Created Meeting: {data['title']}")
    except Exception as e:
        print(f"⚠️ Meetings: {e}")
    
    # 7. TRAINING MODULES
    try:
        from inductiontraining.models import InductionTraining
        
        induction_data = [
            {
                'title': 'Site Safety Induction',
                'date': date.today() - timedelta(days=5),
                'location': 'Training Room',
                'conducted_by': 'Safety Manager',
                'status': 'completed',
                'description': 'Basic safety orientation for new workers',
                'project': projects[0]
            },
            {
                'title': 'Equipment Operation Training',
                'date': date.today() - timedelta(days=3),
                'location': 'Workshop',
                'conducted_by': 'Technical Lead',
                'status': 'completed',
                'description': 'Training on heavy equipment operation',
                'project': projects[1] if len(projects) > 1 else projects[0]
            }
        ]
        
        for data in induction_data:
            obj, created = InductionTraining.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                defaults=data
            )
            if created:
                print(f"✅ Created Induction Training: {data['title']}")
    except Exception as e:
        print(f"⚠️ Induction Training: {e}")
    
    try:
        from jobtraining.models import JobTraining
        
        job_training_data = [
            {
                'title': 'Crane Operation Certification',
                'date': date.today() - timedelta(days=7),
                'location': 'Construction Site',
                'conducted_by': 'Certified Trainer',
                'status': 'completed',
                'description': 'Specialized training for crane operators',
                'project': projects[0]
            }
        ]
        
        for data in job_training_data:
            obj, created = JobTraining.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                defaults=data
            )
            if created:
                print(f"✅ Created Job Training: {data['title']}")
    except Exception as e:
        print(f"⚠️ Job Training: {e}")
    
    try:
        from tbt.models import ToolboxTalk
        
        tbt_data = [
            {
                'title': 'Electrical Safety Awareness',
                'date': date.today() - timedelta(days=2),
                'location': 'Site Office',
                'conducted_by': 'Electrical Supervisor',
                'status': 'completed',
                'description': 'Daily toolbox talk on electrical hazards',
                'project': projects[0]
            },
            {
                'title': 'Fall Protection Measures',
                'date': date.today() - timedelta(days=1),
                'location': 'Turbine Base',
                'conducted_by': 'Safety Officer',
                'status': 'completed',
                'description': 'Safety briefing for working at height',
                'project': projects[1] if len(projects) > 1 else projects[0]
            }
        ]
        
        for data in tbt_data:
            obj, created = ToolboxTalk.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                defaults=data
            )
            if created:
                print(f"✅ Created Toolbox Talk: {data['title']}")
    except Exception as e:
        print(f"⚠️ Toolbox Talks: {e}")
    
    # 8. QUALITY MANAGEMENT
    try:
        from quality.models import QualityInspection, QualityNonConformance
        
        inspection_data = [
            {
                'inspection_id': 'QI-2024-001',
                'title': 'Solar Panel Quality Check',
                'status': 'completed',
                'inspector_name': 'Quality Inspector',
                'location': 'Panel Assembly Area',
                'project': projects[0]
            }
        ]
        
        for data in inspection_data:
            obj, created = QualityInspection.objects.get_or_create(
                inspection_id=data['inspection_id'],
                defaults=data
            )
            if created:
                print(f"✅ Created Quality Inspection: {data['inspection_id']}")
    except Exception as e:
        print(f"⚠️ Quality Management: {e}")
    
    # 9. ENVIRONMENT (ESG)
    try:
        from environment.models import EnvironmentalMonitoring, WasteManagement
        
        env_data = [
            {
                'monitoring_type': 'air_quality',
                'location': 'Site Boundary',
                'parameter': 'PM2.5',
                'value': 45.2,
                'unit': 'µg/m³',
                'status': 'within_limits',
                'project': projects[0]
            }
        ]
        
        for data in env_data:
            obj, created = EnvironmentalMonitoring.objects.get_or_create(
                monitoring_type=data['monitoring_type'],
                location=data['location'],
                parameter=data['parameter'],
                defaults=data
            )
            if created:
                print(f"✅ Created Environmental Monitoring: {data['parameter']}")
    except Exception as e:
        print(f"⚠️ Environmental: {e}")
    
    print("\n🎉 All modules dummy data creation completed!")
    print("\n📊 Complete EHS System Ready for Demonstration!")
    print("🔑 Login with master admin: master / master@123")

if __name__ == '__main__':
    create_all_modules_data()