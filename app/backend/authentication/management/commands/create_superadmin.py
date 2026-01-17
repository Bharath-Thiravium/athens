import secrets
import string

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Create a platform superadmin (SaaS control plane)."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email for the superadmin.")
        parser.add_argument("--username", help="Username (defaults to email local-part).")
        parser.add_argument("--password", help="Password to set. If omitted, a random strong password is generated.")
        parser.add_argument("--random-password", action="store_true", help="Force-generate a random password.")
        parser.add_argument("--force", action="store_true", help="Update existing user if username already exists.")

    def handle(self, *args, **options):
        email = options["email"]
        username = options.get("username") or email.split("@")[0]
        password = options.get("password")
        if options["random_password"] or not password:
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
            password = "".join(secrets.choice(alphabet) for _ in range(20))
            generated = True
        else:
            generated = False

        try:
            user = User.objects.get(username=username)
            if not options["force"]:
                raise CommandError(f"User '{username}' already exists. Use --force to update.")
            self.stdout.write(self.style.WARNING(f"Updating existing user '{username}' to superadmin."))
        except User.DoesNotExist:
            user = None

        if user is None:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type="superadmin",
                is_staff=True,
                is_superuser=True,
                is_active=True,
                athens_tenant_id=None,
                project=None,
            )
        else:
            user.email = email
            user.user_type = "superadmin"
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.athens_tenant_id = None
            user.project_id = None
            user.set_password(password)
            user.save()

        self.stdout.write(self.style.SUCCESS(f"Superadmin ready: {user.username} (email: {user.email})"))
        if generated:
            self.stdout.write(self.style.WARNING(f"Generated password: {password}"))
