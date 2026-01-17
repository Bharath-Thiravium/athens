from typing import Optional

MASTER_TYPES = {'master', 'masteradmin', 'MASTER_ADMIN'}


def normalize_master_type(value: Optional[str]) -> Optional[str]:
    if value in MASTER_TYPES:
        return 'masteradmin'
    return value


def is_master_type(value: Optional[str]) -> bool:
    return value in MASTER_TYPES


def is_master_user(user) -> bool:
    return is_master_type(getattr(user, 'user_type', None)) or is_master_type(getattr(user, 'admin_type', None))
