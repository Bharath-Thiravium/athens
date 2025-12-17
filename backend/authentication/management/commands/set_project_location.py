from django.core.management.base import BaseCommand
from authentication.models import Project


class Command(BaseCommand):
    help = 'Set latitude and longitude coordinates for a project'

    def add_arguments(self, parser):
        parser.add_argument('--project-id', type=int, help='Project ID to update')
        parser.add_argument('--project-name', type=str, help='Project name to search for')
        parser.add_argument('--latitude', type=float, required=True, help='Latitude coordinate')
        parser.add_argument('--longitude', type=float, required=True, help='Longitude coordinate')
        parser.add_argument('--list-projects', action='store_true', help='List all projects')

    def handle(self, *args, **options):
        if options['list_projects']:
            self.stdout.write(self.style.SUCCESS('Available Projects:'))
            projects = Project.objects.all()
            for project in projects:
                location_info = ""
                if project.latitude and project.longitude:
                    location_info = f" (Lat: {project.latitude}, Lng: {project.longitude})"
                else:
                    location_info = " (No coordinates set)"
                
                self.stdout.write(f"ID: {project.id} - {project.projectName}{location_info}")
            return

        project_id = options.get('project_id')
        project_name = options.get('project_name')
        latitude = options['latitude']
        longitude = options['longitude']

        if not project_id and not project_name:
            self.stdout.write(
                self.style.ERROR('Please provide either --project-id or --project-name')
            )
            return

        try:
            if project_id:
                project = Project.objects.get(id=project_id)
            else:
                project = Project.objects.get(projectName__icontains=project_name)

            # Validate coordinates (basic validation for India)
            if not (6.5546 <= latitude <= 35.6745 and 68.1114 <= longitude <= 97.3956):
                self.stdout.write(
                    self.style.WARNING(
                        'Warning: Coordinates appear to be outside India. '
                        'Please verify the coordinates are correct.'
                    )
                )

            project.latitude = latitude
            project.longitude = longitude
            project.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated project "{project.projectName}" '
                    f'with coordinates: Latitude {latitude}, Longitude {longitude}'
                )
            )

        except Project.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'Project not found with {"ID " + str(project_id) if project_id else "name containing " + project_name}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating project: {str(e)}')
            )
