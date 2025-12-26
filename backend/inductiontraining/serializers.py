from rest_framework import serializers
from .models import InductionTraining, InductionAttendance

class InductionAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = InductionAttendance
        fields = ['id', 'worker_id', 'worker_name', 'status', 'created_at']
        read_only_fields = ['created_at']

class InductionTrainingSerializer(serializers.ModelSerializer):
    attendances = InductionAttendanceSerializer(many=True, read_only=True)
    
    class Meta:
        model = InductionTraining
        fields = [
            'id', 'title', 'description', 'date', 'location', 
            'conducted_by', 'status', 'created_by', 'created_at', 
            'updated_at', 'attendances'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by']
    
    def create(self, validated_data):
        # Set the created_by field to the current user
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

class InductionTrainingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = InductionTraining
        fields = [
            'id', 'title', 'description', 'date', 'location', 
            'conducted_by', 'status', 'created_at', 'updated_at'
        ]