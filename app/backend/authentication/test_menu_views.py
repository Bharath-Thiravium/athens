from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class TestMenuView(APIView):
    permission_classes = []

    def get(self, request):
        # Return simple test data
        return Response({
            'projects': [
                {'id': 1, 'name': 'Test Project 1', 'projectName': 'Test Project 1'},
                {'id': 2, 'name': 'Test Project 2', 'projectName': 'Test Project 2'}
            ],
            'modules': [
                {'id': 1, 'name': 'Dashboard', 'description': 'Main dashboard', 'is_enabled': True},
                {'id': 2, 'name': 'Safety', 'description': 'Safety management', 'is_enabled': True}
            ]
        }, status=status.HTTP_200_OK)