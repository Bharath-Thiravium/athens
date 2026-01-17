from django.core.management.base import BaseCommand
from authentication.models import CustomUser, Project
from authentication.company_isolation import get_company_isolated_queryset

class Command(BaseCommand):
    help = 'Test company data isolation between master users'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing Company Data Isolation'))
        self.stdout.write('=' * 50)
        
        # Get both master users
        try:
            master1 = CustomUser.objects.get(username='master')
            master2 = CustomUser.objects.get(username='master2')
        except CustomUser.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'Master user not found: {e}'))
            return
        
        self.stdout.write(f'Master 1: {master1.username} - Project: {master1.project.projectName if master1.project else "None"}')
        self.stdout.write(f'Master 2: {master2.username} - Project: {master2.project.projectName if master2.project else "None"}')
        self.stdout.write('')
        
        # Test project isolation
        self.stdout.write('Testing Project Isolation:')
        self.stdout.write('-' * 30)
        
        # Projects visible to master1
        master1_projects = get_company_isolated_queryset(Project.objects.all(), master1)
        self.stdout.write(f'Master1 sees {master1_projects.count()} projects:')
        for project in master1_projects:
            self.stdout.write(f'  - {project.projectName}')
        
        # Projects visible to master2
        master2_projects = get_company_isolated_queryset(Project.objects.all(), master2)
        self.stdout.write(f'Master2 sees {master2_projects.count()} projects:')
        for project in master2_projects:
            self.stdout.write(f'  - {project.projectName}')
        
        self.stdout.write('')
        
        # Test user isolation
        self.stdout.write('Testing User Isolation:')
        self.stdout.write('-' * 30)
        
        # Users visible to master1
        master1_users = get_company_isolated_queryset(CustomUser.objects.all(), master1)
        self.stdout.write(f'Master1 sees {master1_users.count()} users from their company')
        
        # Users visible to master2
        master2_users = get_company_isolated_queryset(CustomUser.objects.all(), master2)
        self.stdout.write(f'Master2 sees {master2_users.count()} users from their company')
        
        # Check for data leakage
        self.stdout.write('')
        self.stdout.write('Data Isolation Verification:')
        self.stdout.write('-' * 30)
        
        # Check if master1 can see master2's project
        master1_can_see_master2_project = master1_projects.filter(id=master2.project.id if master2.project else 0).exists()
        master2_can_see_master1_project = master2_projects.filter(id=master1.project.id if master1.project else 0).exists()
        
        if master1_can_see_master2_project:
            self.stdout.write(self.style.ERROR('❌ DATA LEAK: Master1 can see Master2\'s project'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Master1 cannot see Master2\'s project'))
        
        if master2_can_see_master1_project:
            self.stdout.write(self.style.ERROR('❌ DATA LEAK: Master2 can see Master1\'s project'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Master2 cannot see Master1\'s project'))
        
        # Check if users from different companies can see each other
        master1_users_list = list(master1_users.values_list('id', flat=True))
        master2_users_list = list(master2_users.values_list('id', flat=True))
        
        common_users = set(master1_users_list) & set(master2_users_list)
        if common_users:
            self.stdout.write(self.style.ERROR(f'❌ DATA LEAK: {len(common_users)} users visible to both masters'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ No user data leakage between companies'))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('Company Data Isolation Test Complete'))
        
        # Summary
        self.stdout.write('')
        self.stdout.write('SUMMARY:')
        self.stdout.write('=' * 50)
        self.stdout.write(f'Company 1 ({master1.project.projectName if master1.project else "No Project"}):')
        self.stdout.write(f'  - Projects: {master1_projects.count()}')
        self.stdout.write(f'  - Users: {master1_users.count()}')
        self.stdout.write('')
        self.stdout.write(f'Company 2 ({master2.project.projectName if master2.project else "No Project"}):')
        self.stdout.write(f'  - Projects: {master2_projects.count()}')
        self.stdout.write(f'  - Users: {master2_users.count()}')
        self.stdout.write('')
        
        if not master1_can_see_master2_project and not master2_can_see_master1_project and not common_users:
            self.stdout.write(self.style.SUCCESS('🎉 COMPANY DATA ISOLATION IS WORKING CORRECTLY'))
        else:
            self.stdout.write(self.style.ERROR('⚠️  COMPANY DATA ISOLATION HAS ISSUES - REVIEW REQUIRED'))