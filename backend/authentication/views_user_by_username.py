from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from rest_framework.permissions import IsAuthenticated
from .permissions import IsMasterAdmin

class MasterAdminGetUserByUsernameView(APIView):
    permission_classes = [IsAuthenticated, IsMasterAdmin]

    def get(self, request, username):
        try:
            user = CustomUser.objects.get(username=username, user_type='projectadmin')
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"id": user.id, "username": user.username}, status=status.HTTP_200_OK)
