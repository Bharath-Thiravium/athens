from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer

from .models import CustomUser
from .usertype_utils import is_master_user, normalize_master_type


def apply_custom_claims(token, user: CustomUser):
    token['admin_type'] = normalize_master_type(user.admin_type)
    if user.user_type == 'user' and user.admin_type:
        token['user_type'] = normalize_master_type(user.admin_type)
    else:
        token['user_type'] = normalize_master_type(user.user_type)
    token['is_superadmin'] = (user.user_type == 'superadmin')
    token['tenant_id'] = str(getattr(user, 'athens_tenant_id', '') or '') or None
    if user.project:
        token['project_id'] = user.project.id
    if user.athens_tenant_id:
        token['athens_tenant_id'] = str(user.athens_tenant_id)
    return token


def build_token_response(user: CustomUser) -> dict:
    refresh = RefreshToken.for_user(user)
    apply_custom_claims(refresh, user)

    data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

    if is_master_user(user):
        data['usertype'] = 'masteradmin'
        data['username'] = user.username
    elif user.user_type == 'superadmin':
        data['usertype'] = 'superadmin'
        data['username'] = user.username
    elif user.user_type == 'projectadmin':
        if user.admin_type == 'contractor' and user.project:
            contractor_admins = CustomUser.objects.using(user._state.db).filter(
                project=user.project,
                user_type='projectadmin',
                admin_type='contractor',
            ).order_by('id')
            index = None
            for i, admin in enumerate(contractor_admins, start=1):
                if admin.pk == user.pk:
                    index = i
                    break
            data['usertype'] = f'contractor{index}' if index else user.admin_type
        else:
            data['usertype'] = user.admin_type
        data['username'] = user.username
    elif user.user_type == 'adminuser':
        data['usertype'] = user.admin_type
        data['username'] = user.email
    else:
        data['usertype'] = getattr(user, 'user_type', 'user')
        data['username'] = getattr(user, 'username', None)

    data['isPasswordResetRequired'] = getattr(user, 'is_password_reset_required', False)
    data['user_id'] = user.id
    data['django_user_type'] = normalize_master_type(user.user_type)
    data['grade'] = getattr(user, 'grade', None)
    data['department'] = getattr(user, 'department', None)
    data['project_id'] = user.project.id if user.project else None
    data['tenant_id'] = str(user.athens_tenant_id) if user.athens_tenant_id else None
    data['is_superadmin'] = (user.user_type == 'superadmin')

    data['is_approved'] = True
    data['has_submitted_details'] = True

    if is_master_user(user):
        data['is_approved'] = True
        data['has_submitted_details'] = True
    elif user.user_type == 'projectadmin':
        try:
            admin_detail = user.admin_detail
            data['has_submitted_details'] = bool(
                admin_detail.phone_number and
                admin_detail.pan_number and
                admin_detail.gst_number
            )
            data['is_approved'] = admin_detail.is_approved
        except Exception:
            data['has_submitted_details'] = False
            data['is_approved'] = False
    elif user.user_type == 'adminuser':
        try:
            user_detail = user.user_detail
            data['has_submitted_details'] = bool(
                user_detail.mobile and
                user_detail.pan and
                user_detail.employee_id
            )
            data['is_approved'] = user_detail.is_approved
        except Exception:
            data['has_submitted_details'] = False
            data['is_approved'] = False

    return data


def build_refresh_response(refresh_token: str) -> dict:
    serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
    serializer.is_valid(raise_exception=True)
    return serializer.validated_data
