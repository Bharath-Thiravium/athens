from django.core.management.base import BaseCommand
from authentication.models import CustomUser

class Command(BaseCommand):
    help = 'Update user hierarchy: adminuser -> user for users created by project admins'

    def handle(self, *args, **options):
        # Update users created by project admins from 'adminuser' to 'user'
        updated_count = 0
        
        # Find all users with user_type='adminuser' who were created by project admins
        users_to_update = CustomUser.objects.filter(
            user_type='adminuser',
            created_by__user_type='projectadmin'
        )
        
        self.stdout.write(f"Found {users_to_update.count()} users to update from 'adminuser' to 'user'")
        
        for user in users_to_update:
            old_type = user.user_type
            user.user_type = 'user'
            user.save()
            updated_count += 1
            self.stdout.write(f"Updated {user.username}: {old_type} -> {user.user_type}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} users')
        )