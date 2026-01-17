from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from control_plane.services.tenant_db import get_tenant_db_alias
from .services.tenant_auth import authenticate_tenant_user
from .tokens import build_token_response


class TenantLoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        tenant_id = request.data.get('tenant_id')
        email = request.data.get('email')
        username = request.data.get('username')
        password = request.data.get('password')

        if not tenant_id or not password or (not email and not username):
            return Response(
                {'detail': 'tenant_id, password, and email or username are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            tenant_db_alias = get_tenant_db_alias(tenant_id)
        except Exception:
            return Response({'detail': 'Invalid tenant selection.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate_tenant_user(tenant_db_alias, email, username, password)
        if not user:
            return Response({'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not user.athens_tenant_id:
            return Response({'detail': 'User is missing tenant binding.'}, status=status.HTTP_403_FORBIDDEN)

        response_data = build_token_response(user)
        return Response(response_data, status=status.HTTP_200_OK)
