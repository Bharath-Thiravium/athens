from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

import logging
from django.contrib.auth.backends import ModelBackend
from .models import CustomUser

logger = logging.getLogger(__name__)

class CustomAuthBackend(ModelBackend):
    """
    Custom authentication backend for CustomUser model.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = CustomUser.objects.get(username=username)
            if user.check_password(password):
                if user.is_active:
                    return user
                else:
                    logger.warning(f"User {username} is inactive.")
            else:
                logger.warning(f"Invalid password for user {username}.")
        except CustomUser.DoesNotExist:
            logger.warning(f"User {username} does not exist.")
        return None
        
    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
