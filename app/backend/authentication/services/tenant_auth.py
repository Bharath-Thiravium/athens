from django.contrib.auth import get_user_model


def authenticate_tenant_user(tenant_db: str, email: str | None, username: str | None, password: str):
    user_model = get_user_model()
    lookup = {}

    if email:
        lookup['email__iexact'] = email
    elif username:
        lookup['username'] = username
    else:
        return None

    try:
        user = user_model.objects.using(tenant_db).get(**lookup)
    except user_model.DoesNotExist:
        return None

    if not user.check_password(password):
        return None

    return user
