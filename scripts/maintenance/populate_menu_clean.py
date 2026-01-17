#!/usr/bin/env python
import os
import sys
import django

sys.path.append('/var/www/athens/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.menu_models import MenuCategory, MenuModule, CompanyMenuAccess, UserMenuPermission

def clear_and_populate():
    print("Clearing existing menu data...")
    
    # Clear existing data in correct order
    UserMenuPermission.objects.all().delete()
    CompanyMenuAccess.objects.all().delete()
    
    # Clear ProjectMenuAccess if it exists
    try:
        from authentication.models import ProjectMenuAccess
        ProjectMenuAccess.objects.all().delete()
    except:
        pass
    
    MenuModule.objects.all().delete()
    MenuCategory.objects.all().delete()
    
    print("Existing data cleared. Populating new data...")
    
    # Create categories
    categories_data = [
        {'name': 'Dashboard', 'key': 'dashboard', 'icon': 'DashboardOutlined', 'order': 1},
        {'name': 'Safety Management', 'key': 'safety', 'icon': 'SafetyOutlined', 'order': 2},
        {'name': 'Training & Development', 'key': 'training', 'icon': 'BookOutlined', 'order': 3},
        {'name': 'Workforce Management', 'key': 'workforce', 'icon': 'TeamOutlined', 'order': 4},
        {'name': 'Communication', 'key': 'communication', 'icon': 'MessageOutlined', 'order': 5},
        {'name': 'Quality Management System', 'key': 'qms', 'icon': 'CheckCircleOutlined', 'order': 6},
        {'name': 'Environment Management', 'key': 'esg', 'icon': 'GlobalOutlined', 'order': 7},
        {'name': 'System Administration', 'key': 'admin', 'icon': 'SettingOutlined', 'order': 8},
        {'name': 'Reports & Analytics', 'key': 'reports', 'icon': 'BarChartOutlined', 'order': 9},
    ]

    categories = {}
    for cat_data in categories_data:
        category = MenuCategory.objects.create(**cat_data)
        categories[cat_data['key']] = category
        print(f"Created category: {category.name}")

    # Create modules
    modules_data = [
        # Dashboard
        {'category_key': 'dashboard', 'name': 'Main Dashboard', 'key': 'main_dashboard', 'icon': 'DashboardOutlined', 'path': '/dashboard', 'order': 1, 'description': 'Main system dashboard'},
        {'category_key': 'dashboard', 'name': 'Analytics Dashboard', 'key': 'analytics_dashboard', 'icon': 'LineChartOutlined', 'path': '/analytics', 'order': 2, 'description': 'Analytics and reporting dashboard'},
        
        # Safety Management
        {'category_key': 'safety', 'name': 'Safety Observation', 'key': 'safety_observation', 'icon': 'EyeOutlined', 'path': '/safety-observation', 'order': 1, 'description': 'Safety observation reports'},
        {'category_key': 'safety', 'name': 'Incident Management', 'key': 'incident_management', 'icon': 'ExclamationCircleOutlined', 'path': '/incidents', 'order': 2, 'description': 'Incident reporting and management'},
        {'category_key': 'safety', 'name': 'Permit to Work', 'key': 'ptw', 'icon': 'FileProtectOutlined', 'path': '/ptw', 'order': 3, 'description': 'Work permit management'},
        {'category_key': 'safety', 'name': 'Inspection Management', 'key': 'inspection', 'icon': 'SearchOutlined', 'path': '/inspections', 'order': 4, 'description': 'Safety inspections'},
        {'category_key': 'safety', 'name': 'Toolbox Talk', 'key': 'toolbox_talk', 'icon': 'CommentOutlined', 'path': '/toolbox-talk', 'order': 5, 'description': 'Daily safety talks'},
        
        # Training & Development
        {'category_key': 'training', 'name': 'Induction Training', 'key': 'induction_training', 'icon': 'UserAddOutlined', 'path': '/induction-training', 'order': 1, 'description': 'New employee induction'},
        {'category_key': 'training', 'name': 'Job Training', 'key': 'job_training', 'icon': 'ToolOutlined', 'path': '/job-training', 'order': 2, 'description': 'Job-specific training'},
        {'category_key': 'training', 'name': 'Training Records', 'key': 'training_records', 'icon': 'FileTextOutlined', 'path': '/training-records', 'order': 3, 'description': 'Training history and certificates'},
        
        # Workforce Management
        {'category_key': 'workforce', 'name': 'Worker Management', 'key': 'worker_management', 'icon': 'UserOutlined', 'path': '/workers', 'order': 1, 'description': 'Worker profiles and management'},
        {'category_key': 'workforce', 'name': 'Manpower Management', 'key': 'manpower_management', 'icon': 'UsergroupAddOutlined', 'path': '/manpower', 'order': 2, 'description': 'Manpower planning and allocation'},
        
        # Communication
        {'category_key': 'communication', 'name': 'Chatbox', 'key': 'chatbox', 'icon': 'MessageOutlined', 'path': '/chat', 'order': 1, 'description': 'Team communication'},
        {'category_key': 'communication', 'name': 'Minutes of Meeting', 'key': 'mom', 'icon': 'FileTextOutlined', 'path': '/mom', 'order': 2, 'description': 'Meeting documentation'},
        {'category_key': 'communication', 'name': 'Voice Translator', 'key': 'voice_translator', 'icon': 'SoundOutlined', 'path': '/voice-translator', 'order': 3, 'description': 'Multi-language translation'},
        
        # Quality Management System
        {'category_key': 'qms', 'name': 'Quality Standards', 'key': 'quality_standards', 'icon': 'CheckCircleOutlined', 'path': '/quality/standards', 'order': 1, 'description': 'Quality standards and procedures'},
        {'category_key': 'qms', 'name': 'Quality Audits', 'key': 'quality_audits', 'icon': 'AuditOutlined', 'path': '/quality/audits', 'order': 2, 'description': 'Quality audit management'},
        {'category_key': 'qms', 'name': 'Non-Conformance Reports', 'key': 'ncr', 'icon': 'ExclamationTriangleOutlined', 'path': '/quality/ncr', 'order': 3, 'description': 'Non-conformance tracking'},
        
        # Environment Management
        {'category_key': 'esg', 'name': 'Environmental Policies', 'key': 'env_policies', 'icon': 'FileProtectOutlined', 'path': '/environment/policies', 'order': 1, 'description': 'Environmental policies and procedures'},
        {'category_key': 'esg', 'name': 'Environmental Monitoring', 'key': 'env_monitoring', 'icon': 'MonitorOutlined', 'path': '/environment/monitoring', 'order': 2, 'description': 'Environmental data monitoring'},
        {'category_key': 'esg', 'name': 'Sustainability Reports', 'key': 'sustainability_reports', 'icon': 'FileTextOutlined', 'path': '/environment/reports', 'order': 3, 'description': 'ESG reporting and analytics'},
        
        # System Administration
        {'category_key': 'admin', 'name': 'User Management', 'key': 'user_management', 'icon': 'UserOutlined', 'path': '/admin/users', 'order': 1, 'description': 'User account management'},
        {'category_key': 'admin', 'name': 'Permission Control', 'key': 'permission_control', 'icon': 'KeyOutlined', 'path': '/admin/permissions', 'order': 2, 'description': 'Access control and permissions'},
        {'category_key': 'admin', 'name': 'System Settings', 'key': 'system_settings', 'icon': 'SettingOutlined', 'path': '/admin/settings', 'order': 3, 'description': 'System configuration'},
        
        # Reports & Analytics
        {'category_key': 'reports', 'name': 'Safety Reports', 'key': 'safety_reports', 'icon': 'BarChartOutlined', 'path': '/reports/safety', 'order': 1, 'description': 'Safety analytics and reports'},
        {'category_key': 'reports', 'name': 'Training Reports', 'key': 'training_reports', 'icon': 'LineChartOutlined', 'path': '/reports/training', 'order': 2, 'description': 'Training progress reports'},
        {'category_key': 'reports', 'name': 'Compliance Reports', 'key': 'compliance_reports', 'icon': 'FileTextOutlined', 'path': '/reports/compliance', 'order': 3, 'description': 'Regulatory compliance reports'},
    ]

    for mod_data in modules_data:
        category = categories[mod_data['category_key']]
        module_data = {k: v for k, v in mod_data.items() if k != 'category_key'}
        module_data['category'] = category
        
        module = MenuModule.objects.create(**module_data)
        print(f"Created module: {module.name}")

    print("Menu system populated successfully!")

if __name__ == '__main__':
    clear_and_populate()