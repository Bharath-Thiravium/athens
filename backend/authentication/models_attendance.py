from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class ProjectAttendance(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project_attendances')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='attendances')
    check_in_time = models.DateTimeField(null=True, blank=True)
    check_out_time = models.DateTimeField(null=True, blank=True)
    check_in_latitude = models.FloatField(null=True, blank=True)
    check_in_longitude = models.FloatField(null=True, blank=True)
    check_out_latitude = models.FloatField(null=True, blank=True)
    check_out_longitude = models.FloatField(null=True, blank=True)
    check_in_photo = models.ImageField(upload_to='attendance_photos/check_in/', null=True, blank=True)
    check_out_photo = models.ImageField(upload_to='attendance_photos/check_out/', null=True, blank=True)
    status = models.CharField(max_length=11, choices=[('checked_in', 'Checked In'), ('checked_out', 'Checked Out')], default='checked_out')
    working_time = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"Attendance of {self.user.username} for {self.project.projectName} - Status: {self.status}"

    def is_within_radius(self, latitude, longitude, radius_meters=300):
        """
        Check if the given location is within the given radius (in meters) of the project location.
        Uses Haversine formula to calculate distance.
        """
        from math import radians, cos, sin, asin, sqrt

        # Check if project has valid coordinates
        if self.project.latitude is None or self.project.longitude is None:
            return False  # If project location is not set, deny access

        # Check if provided coordinates are valid
        if latitude is None or longitude is None:
            return False

        lat1, lon1 = float(latitude), float(longitude)
        lat2, lon2 = float(self.project.latitude), float(self.project.longitude)

        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371000  # Radius of earth in meters
        distance = c * r

        return distance <= radius_meters
