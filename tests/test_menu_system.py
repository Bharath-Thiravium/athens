#!/usr/bin/env python
import os
import sys
import django

# Add the backend directory to the Python path
sys.path.append('/var/www/athens/backend')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from authentication.menu_models import MenuCategory, MenuModule

def test_menu_system():
    print("Testing menu system...")
    
    # Test creating a category
    try:
        category, created = MenuCategory.objects.get_or_create(
            key='test_dashboard',
            defaults={
                'name': 'Test Dashboard',
                'icon': 'DashboardOutlined',
                'order': 1
            }
        )
        print(f"Category created: {created}, Category: {category}")
        
        # Test creating a module
        module, created = MenuModule.objects.get_or_create(
            key='test_main_dashboard',
            defaults={
                'category': category,
                'name': 'Test Main Dashboard',
                'icon': 'DashboardOutlined',
                'path': '/test-dashboard',
                'order': 1,
                'description': 'Test dashboard module'
            }
        )
        print(f"Module created: {created}, Module: {module}")
        
        print("Menu system is working!")
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    test_menu_system()