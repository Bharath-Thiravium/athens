from rest_framework import serializers
from .models import SystemSettings, Backup

class SystemSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemSettings
        fields = [
            'siteName', 'siteDescription', 'maintenanceMode', 'allowRegistration',
            'defaultUserRole', 'sessionTimeout', 'maxFileSize', 'emailNotifications',
            'smsNotifications', 'backupFrequency', 'logLevel', 'updated_at'
        ]
        read_only_fields = ['updated_at']

class BackupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Backup
        fields = [
            'id', 'name', 'type', 'description', 'size', 'status', 
            'progress', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'size', 'status', 'progress']

