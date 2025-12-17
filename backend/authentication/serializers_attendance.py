from rest_framework import serializers
from .models_attendance import ProjectAttendance

class ProjectAttendanceSerializer(serializers.ModelSerializer):
    check_in_photo = serializers.ImageField(required=False, allow_null=True)
    check_out_photo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = ProjectAttendance
        fields = [
            'id',
            'user',
            'project',
            'check_in_time',
            'check_out_time',
            'check_in_latitude',
            'check_in_longitude',
            'check_out_latitude',
            'check_out_longitude',
            'check_in_photo',
            'check_out_photo',
            'status',
        ]
        read_only_fields = ['id', 'check_in_time', 'check_out_time']
