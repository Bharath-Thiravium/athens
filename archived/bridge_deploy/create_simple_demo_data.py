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

def create_simple_demo_data():
    print("🚀 Creating simple demo data for key modules...")
    
    # Get existing data
    projects = Project.objects.all()[:3]
    users = CustomUser.objects.filter(user_type='adminuser')[:5]
    
    if not projects.exists():
        print("❌ No projects found. Run populate_demo_data.py first!")
        return
    
    # 1. WORKERS - Using correct field names
    try:
        from worker.models import Worker
        
        worker_data = [
            {
                'name': 'Rajesh Kumar',
                'surname': 'Kumar',
                'department': 'Construction',
                'designation': 'Site Engineer',
                'status': 'active',
                'worker_id': 'W001',
                'phone_number': '+91-9876543210',
                'project': projects[0],
                'created_by': users[0] if users.exists() else None
            },
            {
                'name': 'Priya',
                'surname': 'Sharma',
                'department': 'Safety',
                'designation': 'Safety Officer',
                'status': 'active',
                'worker_id': 'W002',
                'phone_number': '+91-9876543211',
                'project': projects[1] if len(projects) > 1 else projects[0],
                'created_by': users[1] if len(users) > 1 else users[0]
            },
            {
                'name': 'Amit',
                'surname': 'Patel',
                'department': 'Quality',
                'designation': 'QC Inspector',
                'status': 'active',
                'worker_id': 'W003',
                'phone_number': '+91-9876543212',
                'project': projects[2] if len(projects) > 2 else projects[0],
                'created_by': users[2] if len(users) > 2 else users[0]
            }
        ]
        
        for data in worker_data:
            obj, created = Worker.objects.get_or_create(
                worker_id=data['worker_id'],
                defaults=data
            )
            if created:
                print(f"✅ Created Worker: {data['name']} {data['surname']}")
    except Exception as e:
        print(f"⚠️ Workers: {e}")
    
    # 2. SAFETY OBSERVATIONS - Using correct field names
    try:
        from safetyobservation.models import SafetyObservation
        
        safety_data = [
            {
                'observationID': 'SO-2024-001',
                'department': 'Engineering',
                'workLocation': 'Solar Panel Area',
                'severity': 'Medium',
                'observationStatus': 'Open',
                'safetyObservationFound': 'Workers not wearing proper PPE',
                'created_by': users[0] if users.exists() else None
            },
            {
                'observationID': 'SO-2024-002',
                'department': 'Construction',
                'workLocation': 'Wind Turbine Base',
                'severity': 'High',
                'observationStatus': 'In Progress',
                'safetyObservationFound': 'Unsafe scaffolding setup',
                'created_by': users[1] if len(users) > 1 else users[0]
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
    
    # 3. INCIDENTS - Using correct field names
    try:
        from incidentmanagement.models import Incident
        
        incident_data = [
            {
                'title': 'Minor Electrical Shock',
                'department': 'Electrical',
                'location': 'Substation Area',
                'status': 'Under Investigation',
                'description': 'Technician received minor shock',
                'incident_type': 'electrical',
                'reported_by': users[0] if users.exists() else None
            },
            {
                'title': 'Equipment Malfunction',
                'department': 'Operations',
                'location': 'Turbine #3',
                'status': 'Resolved',
                'description': 'Hydraulic system failure',
                'incident_type': 'equipment',
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
    
    # 4. MEETINGS (MOM) - Using correct field names
    try:
        from mom.models import Mom
        
        mom_data = [
            {
                'title': 'Weekly Safety Review',
                'status': 'completed',
                'department': 'Safety',
                'location': 'Conference Room A',
                'agenda': 'Review safety incidents and preventive measures',
                'meeting_datetime': datetime.now(),
                'scheduled_by': users[0] if users.exists() else None
            },
            {
                'title': 'Project Progress Meeting',
                'status': 'scheduled',
                'department': 'Engineering',
                'location': 'Site Office',
                'agenda': 'Discuss project milestones',
                'meeting_datetime': datetime.now() + timedelta(days=2),
                'scheduled_by': users[1] if len(users) > 1 else users[0]
            }
        ]
        
        for data in mom_data:
            obj, created = Mom.objects.get_or_create(
                title=data['title'],
                defaults=data
            )
            if created:
                print(f"✅ Created Meeting: {data['title']}")
    except Exception as e:
        print(f"⚠️ Meetings: {e}")
    
    # 5. TRAINING MODULES - Using correct field names
    try:
        from inductiontraining.models import InductionTraining
        
        induction_data = [
            {
                'title': 'Site Safety Induction',
                'date': date.today() - timedelta(days=5),
                'location': 'Training Room',
                'conducted_by': 'Safety Manager',
                'status': 'completed',
                'description': 'Basic safety orientation',
                'created_by': users[0] if users.exists() else None
            }
        ]
        
        for data in induction_data:
            obj, created = InductionTraining.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                created_by=data['created_by'],
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
                'description': 'Specialized crane training',
                'created_by': users[0] if users.exists() else None
            }
        ]
        
        for data in job_training_data:
            obj, created = JobTraining.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                created_by=data['created_by'],
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
                'created_by': users[0] if users.exists() else None
            }
        ]
        
        for data in tbt_data:
            obj, created = ToolboxTalk.objects.get_or_create(
                title=data['title'],
                date=data['date'],
                created_by=data['created_by'],
                defaults=data
            )
            if created:
                print(f"✅ Created Toolbox Talk: {data['title']}")
    except Exception as e:
        print(f"⚠️ Toolbox Talks: {e}")
    
    print("\n🎉 Simple demo data creation completed!")
    print("📊 Key EHS modules now have sample data!")
    print("🔑 Login with master admin: master / master@123")

if __name__ == '__main__':
    create_simple_demo_data()