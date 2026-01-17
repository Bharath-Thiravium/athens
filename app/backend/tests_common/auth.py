from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken


def make_access_token(user):
    return AccessToken.for_user(user)


def auth_headers(user):
    token = make_access_token(user)
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


def api_client_with_jwt(user):
    client = APIClient()
    client.credentials(**auth_headers(user))
    return client
