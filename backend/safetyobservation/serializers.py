from rest_framework import serializers
from .models import SafetyObservation, SafetyObservationFile

class SafetyObservationFileSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = SafetyObservationFile
        fields = ['id', 'file', 'file_name', 'file_type', 'uploaded_at', 'uploaded_by', 'uploaded_by_name']
        read_only_fields = ['uploaded_at', 'uploaded_by', 'uploaded_by_name']

class SafetyObservationSerializer(serializers.ModelSerializer):
    files = SafetyObservationFileSerializer(many=True, read_only=True)
    
    # File upload fields
    beforePictures = serializers.ListField(
        child=serializers.FileField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )

    class Meta:
        model = SafetyObservation
        fields = [
            'id', 'observationID', 'date', 'time', 'reportedBy', 'department',
            'workLocation', 'activityPerforming', 'contractorName',
            'typeOfObservation', 'classification', 'safetyObservationFound',
            'severity', 'likelihood', 'riskScore',
            'correctivePreventiveAction', 'correctiveActionAssignedTo', 'commitmentDate',
            'observationStatus', 'remarks',
            'is_environmental', 'env_incident_type',
            'created_at', 'updated_at', 'created_by',
            'files', 'beforePictures'
        ]
        read_only_fields = ['id', 'riskScore', 'created_at', 'updated_at', 'created_by', 'files']

    def create(self, validated_data):
        # Extract file data
        before_pictures = validated_data.pop('beforePictures', [])

        # Create the safety observation
        safety_observation = SafetyObservation.objects.create(**validated_data)

        # Handle file uploads
        for file in before_pictures:
            # Determine file type based on filename
            file_type = 'fixed' if 'fixed_' in file.name.lower() else 'before'

            SafetyObservationFile.objects.create(
                safety_observation=safety_observation,
                file=file,
                file_name=file.name,
                file_type=file_type,
                uploaded_by=self.context['request'].user
            )

        return safety_observation

    def update(self, instance, validated_data):
        # Extract file data
        before_pictures = validated_data.pop('beforePictures', [])

        # Update only the provided fields (partial update support)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Only save if there are actual field updates or files to upload
        if validated_data or before_pictures:
            instance.save()

        # Handle new file uploads (append to existing files)
        for file in before_pictures:
            # Determine file type based on filename
            file_type = 'fixed' if 'fixed_' in file.name.lower() else 'before'

            SafetyObservationFile.objects.create(
                safety_observation=instance,
                file=file,
                file_name=file.name,
                file_type=file_type,
                uploaded_by=self.context['request'].user
            )

        return instance
