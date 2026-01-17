from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import Project
import logging

logger = logging.getLogger(__name__)

class ProjectListView(APIView):
    permission_classes = []

    def get(self, request):
        try:
            projects = Project.objects.all()
            
            project_data = []
            for project in projects:
                project_data.append({
                    'id': project.id,
                    'name': project.projectName,
                    'projectName': project.projectName,
                    'projectCategory': project.projectCategory,
                    'location': project.location,
                    'capacity': project.capacity
                })
            
            return Response(project_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting projects: {str(e)}")
            return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)