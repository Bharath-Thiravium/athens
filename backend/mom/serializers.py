from rest_framework import serializers
from .models import Mom, ParticipantResponse, ParticipantAttendance
from authentication.models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'name', 'email', 'department']

class ParticipantAttendanceSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ParticipantAttendance
        fields = ['user', 'attended']

class MomLiveSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    points_to_discuss = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = Mom
        fields = ['id', 'title', 'agenda', 'meeting_datetime', 'points_to_discuss', 'participants', 'status', 'completed_at', 'duration_minutes']

    def get_participants(self, obj):
        # Get all participants with their status and attendance
        participant_responses = {pr.user_id: pr for pr in obj.participant_responses.all()}
        participant_attendance = {pa.user_id: pa for pa in obj.participant_attendances.all()}
        participants_data = []
        request = self.context.get('request')
        
        def get_participant_company_name(user):
            # Logic similar to AdminUserCommonSerializer.get_company_name
            if user.company_name:
                return user.company_name
            elif user.created_by and user.created_by.company_name:
                return user.created_by.company_name
            elif hasattr(user, 'company_detail') and user.company_detail and user.company_detail.company_name:
                return user.company_detail.company_name
            return None


        for user in obj.participants.all():
            response = participant_responses.get(user.id)
            attendance = participant_attendance.get(user.id)
            signature_url = None
            if hasattr(user, 'user_detail') and user.user_detail and user.user_detail.specimen_signature:
                if request:
                    signature_url = request.build_absolute_uri(user.user_detail.specimen_signature.url)
                else:
                    signature_url = user.user_detail.specimen_signature.url

            participants_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'status': response.status if response else 'noresponse',
                'attended': attendance.attended if attendance else False,
                'designation': user.designation,
                'company_name': get_participant_company_name(user),
                'signature': signature_url,
                'user_type': user.admin_type or user.user_type, # Provide user_type for potential frontend logic
            })
        return participants_data

class MomSerializer(serializers.ModelSerializer):
    scheduled_by = UserSerializer(read_only=True)
    participants = UserSerializer(many=True, read_only=True)
    participants_ids = serializers.PrimaryKeyRelatedField(
        many=True, queryset=CustomUser.objects.all(), write_only=True, source='participants'
    )
    
    class Meta:
        model = Mom
        fields = [
            'id',
            'title',
            'agenda',
            'meeting_datetime',
            'scheduled_by',
            'participants',
            'participants_ids',
            'department',
            'location',
            'created_at',
            'updated_at',
            'status',
            'completed_at',
            'duration_minutes',
        ]

    def create(self, validated_data):
        participants = validated_data.pop('participants', [])
        mom = Mom.objects.create(**validated_data)
        mom.participants.set(participants)
        return mom

# Removed NotificationSerializer - now using authentication notification system

class ParticipantResponseSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ParticipantResponse
        fields = ['id', 'mom', 'user', 'status', 'responded_at']
        read_only_fields = ['id', 'mom', 'user', 'responded_at']

class ParticipantResponseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParticipantResponse
        fields = ['status']

class ParticipantListSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ParticipantResponse
        fields = ['user', 'status']
