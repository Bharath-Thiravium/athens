from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from authentication.models import CustomUser

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users_by_type_and_grade(request):
    """Get users filtered by type and grade for PTW workflow"""
    user_type = request.GET.get('user_type')
    grade = request.GET.get('grade')
    
    if not user_type:
        return Response({'error': 'user_type parameter is required'}, status=400)
    
    user_project = getattr(request.user, 'project', None)
    
    # Filter users by type and project
    users = CustomUser.objects.filter(
        admin_type=user_type,
        project=user_project,
        is_active=True
    ).exclude(id=request.user.id)
    
    # Filter by grade if provided
    if grade:
        users = users.filter(grade=grade)
    
    # Order by name
    users = users.order_by('first_name', 'last_name')
    
    user_data = []
    for user in users:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'full_name': user.get_full_name(),
            'email': user.email,
            'admin_type': user.admin_type,
            'grade': user.grade
        })
    
    return Response({'users': user_data})