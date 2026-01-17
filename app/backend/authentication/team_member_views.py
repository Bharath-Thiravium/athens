from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class TeamMemberViewSet(viewsets.ViewSet):
    """
    ViewSet for 8D team member selection with user type and grade filtering
    """
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def get_team_candidates(self, request):
        """
        Get all potential team members organized by user type and grade
        Excludes the current logged-in user
        """
        current_user = request.user
        
        # Get all admin users except current user
        candidates = User.objects.filter(
            admin_type__in=['adminuser', 'clientuser', 'epcuser', 'contractoruser']
        ).exclude(id=current_user.id).select_related()

        # Organize by user type
        organized_data = {
            'adminuser': {'A': [], 'B': [], 'C': []},
            'clientuser': {'A': [], 'B': [], 'C': []},
            'epcuser': {'A': [], 'B': [], 'C': []},
            'contractoruser': {'A': [], 'B': [], 'C': []}
        }

        for user in candidates:
            user_data = {
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name() or user.username,
                'email': user.email,
                'admin_type': user.admin_type,
                'grade': getattr(user, 'grade', 'A'),  # Default to A if no grade
                'department': getattr(user, 'department', ''),
                'company_name': getattr(user, 'company_name', ''),
                'phone_number': getattr(user, 'phone_number', '')
            }
            
            user_type = user.admin_type
            grade = getattr(user, 'grade', 'A')
            
            if user_type in organized_data and grade in organized_data[user_type]:
                organized_data[user_type][grade].append(user_data)

        return Response({
            'current_user': {
                'id': current_user.id,
                'username': current_user.username,
                'full_name': current_user.get_full_name() or current_user.username,
                'admin_type': current_user.admin_type,
                'role': 'champion'  # Current user is always champion
            },
            'candidates': organized_data
        })

    @action(detail=False, methods=['get'])
    def get_users_by_type_and_grade(self, request):
        """
        Get users filtered by type and grade
        """
        user_type = request.query_params.get('user_type')
        grade = request.query_params.get('grade')
        current_user = request.user

        if not user_type:
            return Response({'error': 'user_type parameter is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)

        queryset = User.objects.filter(
            admin_type=user_type
        ).exclude(id=current_user.id)

        if grade:
            queryset = queryset.filter(grade=grade)

        users = []
        for user in queryset:
            users.append({
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name() or user.username,
                'email': user.email,
                'admin_type': user.admin_type,
                'grade': getattr(user, 'grade', 'A'),
                'department': getattr(user, 'department', ''),
                'company_name': getattr(user, 'company_name', ''),
                'phone_number': getattr(user, 'phone_number', '')
            })

        return Response({'users': users})