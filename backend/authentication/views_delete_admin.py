from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import CustomUser, Project
from .permissions import IsMasterAdmin
from rest_framework.permissions import IsAuthenticated

class MasterAdminDeleteProjectAdminView(APIView):
    permission_classes = [IsAuthenticated, IsMasterAdmin]

    def delete(self, request, user_id):
        try:
            user = CustomUser.objects.get(id=user_id, user_type='projectadmin')
        except CustomUser.DoesNotExist:
            return Response({"error": "Admin user not found."}, status=status.HTTP_404_NOT_FOUND)

        # Optional: Verify user belongs to a project (or specific project if passed)
        if not user.project:
            return Response({"error": "Admin user is not associated with any project."}, status=status.HTTP_400_BAD_REQUEST)

        # Delete all users created by this admin
        related_users = CustomUser.objects.filter(created_by=user)
        related_users.delete()

        # Delete the admin user itself
        user.delete()
        return Response({"detail": "Admin user and related users deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
