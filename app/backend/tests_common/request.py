from urllib.parse import urlencode

from rest_framework.test import APIRequestFactory

from .auth import auth_headers


def jwt_request(user, method, path, data=None, params=None):
    factory = APIRequestFactory()
    method = method.lower()
    request_method = getattr(factory, method)

    url = path
    if params:
        url = f"{path}?{urlencode(params, doseq=True)}"

    headers = auth_headers(user) if user is not None else {}

    if method in {"get", "delete"}:
        return request_method(url, **headers)

    return request_method(url, data=data or {}, format="json", **headers)
