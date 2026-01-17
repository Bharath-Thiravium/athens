from django.core.management.base import BaseCommand
from authentication.menu_models import MenuModule

class Command(BaseCommand):
    help = 'Populate default menu modules'

    def handle(self, *args, **options):
        menu_modules = [
            # Main modules
            {'name': 'Dashboard', 'key': 'dashboard', 'icon': 'DashboardOutlined'},
            {'name': 'Analytics', 'key': 'analytics', 'icon': 'BarChartOutlined'},
            {'name': 'Attendance', 'key': 'attendance', 'icon': 'ClockCircleOutlined'},
            {'name': 'Chat Box', 'key': 'chatbox', 'icon': 'MessageOutlined'},
            {'name': 'Voice Translator', 'key': 'voice-translator', 'icon': 'SoundOutlined'},
            {'name': 'Workers', 'key': 'workers', 'icon': 'TeamOutlined'},
            {'name': 'Manpower', 'key': 'manpower', 'icon': 'TeamOutlined'},
            
            # Training modules
            {'name': 'Training', 'key': 'training', 'icon': 'AuditOutlined'},
            {'name': 'Induction Training', 'key': 'inductiontraining', 'icon': 'ReadOutlined'},
            {'name': 'Job Training', 'key': 'jobtraining', 'icon': 'ReadOutlined'},
            {'name': 'Toolbox Talk', 'key': 'toolboxtalk', 'icon': 'BookOutlined'},
            
            # Safety modules
            {'name': 'Safety Observation', 'key': 'safetyobservation', 'icon': 'SafetyOutlined'},
            {'name': 'Incident Management', 'key': 'incidentmanagement', 'icon': 'SafetyOutlined'},
            
            # Work permits
            {'name': 'Permits to Work', 'key': 'ptw', 'icon': 'FormOutlined'},
            
            # Inspections
            {'name': 'Inspections', 'key': 'inspection', 'icon': 'ExperimentOutlined'},
            
            # ESG Management
            {'name': 'ESG Management', 'key': 'esg', 'icon': 'EnvironmentOutlined'},
            {'name': 'Environmental Management', 'key': 'environment', 'icon': 'EnvironmentOutlined'},
            {'name': 'Environmental Monitoring', 'key': 'monitoring', 'icon': 'ExperimentOutlined'},
            {'name': 'Carbon Footprint', 'key': 'carbon-footprint', 'icon': 'GlobalOutlined'},
            {'name': 'Water Management', 'key': 'water-management', 'icon': 'DropboxOutlined'},
            {'name': 'Energy Management', 'key': 'energy-management', 'icon': 'ThunderboltOutlined'},
            {'name': 'Environmental Incidents', 'key': 'environmental-incidents', 'icon': 'AlertOutlined'},
            {'name': 'Sustainability Targets', 'key': 'sustainability-targets', 'icon': 'TrophyOutlined'},
            {'name': 'Governance', 'key': 'governance', 'icon': 'AuditOutlined'},
            
            # Quality Management
            {'name': 'Quality Management', 'key': 'quality', 'icon': 'CheckCircleOutlined'},
            {'name': 'Quality Inspections', 'key': 'quality-inspections', 'icon': 'ExperimentOutlined'},
            {'name': 'Supplier Quality', 'key': 'suppliers', 'icon': 'TeamOutlined'},
            {'name': 'Defect Management', 'key': 'defects', 'icon': 'BugOutlined'},
            {'name': 'Quality Templates', 'key': 'templates', 'icon': 'FileTextOutlined'},
            {'name': 'Quality Standards', 'key': 'standards', 'icon': 'TrophyOutlined'},
            {'name': 'Quality Alerts', 'key': 'alerts', 'icon': 'AlertOutlined'},
            
            # Other modules
            {'name': 'Minutes of Meeting', 'key': 'mom', 'icon': 'CalendarOutlined'},
        ]

        created_count = 0
        for module_data in menu_modules:
            module, created = MenuModule.objects.get_or_create(
                key=module_data['key'],
                defaults={
                    'name': module_data['name'],
                    'icon': module_data['icon']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created menu module: {module.name}")

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} menu modules')
        )