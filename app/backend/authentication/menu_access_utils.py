import logging

from .menu_models import MenuModule, CompanyMenuAccess
from .tenant_models import AthensTenant

logger = logging.getLogger(__name__)

# Map tenant module codes to menu module keys used by the UI.
TENANT_MODULE_TO_MENU_KEYS = {
    'authentication': [
        'main_dashboard',
        'analytics_dashboard',
        'chatbox',
        'user_management',
        'dashboard',
        'analytics',
        'attendance',
    ],
    'worker': ['worker_management', 'workers'],
    'tbt': ['toolbox_talk', 'toolboxtalk', 'training', 'training_records', 'training_reports'],
    'inductiontraining': ['induction_training', 'inductiontraining', 'training', 'training_records', 'training_reports'],
    'jobtraining': ['job_training', 'jobtraining', 'training', 'training_records', 'training_reports'],
    'mom': ['mom'],
    'safetyobservation': ['safety_observation', 'safetyobservation', 'safety_reports'],
    'ptw': ['ptw', 'compliance_reports'],
    'manpower': ['manpower_management', 'manpower', 'attendance'],
    'incidentmanagement': ['incident_management', 'incidentmanagement'],
    'inspection': ['inspection'],
    'permissions': ['permission_control'],
    'system': ['system_settings'],
    'environment': [
        'env_monitoring',
        'env_policies',
        'sustainability_reports',
        'esg',
        'environment',
        'monitoring',
        'carbon-footprint',
        'water-management',
        'energy-management',
        'environmental-incidents',
        'sustainability-targets',
        'governance',
    ],
    'quality': [
        'quality_audits',
        'quality_standards',
        'ncr',
        'quality',
        'quality-inspections',
        'suppliers',
        'defects',
        'templates',
        'standards',
        'alerts',
    ],
    'voice_translator': ['voice_translator', 'voice-translator'],
}


def _map_enabled_modules_to_menu_keys(enabled_modules):
    keys = set()
    for module in enabled_modules or []:
        keys.update(TENANT_MODULE_TO_MENU_KEYS.get(module, []))
        keys.add(module)
    return keys


def get_allowed_menu_modules_for_tenant(tenant_id):
    tenant = AthensTenant.objects.filter(id=tenant_id).only('enabled_modules').first()
    if not tenant:
        logger.warning("Tenant %s not found when resolving menu modules", tenant_id)
        return MenuModule.objects.none()
    allowed_keys = _map_enabled_modules_to_menu_keys(tenant.enabled_modules)
    if not allowed_keys:
        return MenuModule.objects.none()
    return MenuModule.objects.filter(key__in=allowed_keys, is_active=True)


def get_allowed_menu_module_ids_for_tenant(tenant_id):
    return list(get_allowed_menu_modules_for_tenant(tenant_id).values_list('id', flat=True))


def sync_company_menu_access(tenant_id):
    allowed_modules = list(get_allowed_menu_modules_for_tenant(tenant_id))
    allowed_ids = {module.id for module in allowed_modules}

    for module in allowed_modules:
        CompanyMenuAccess.objects.update_or_create(
            athens_tenant_id=tenant_id,
            module=module,
            defaults={'is_enabled': True},
        )

    if allowed_ids:
        CompanyMenuAccess.objects.filter(athens_tenant_id=tenant_id).exclude(
            module_id__in=allowed_ids
        ).update(is_enabled=False)
    else:
        CompanyMenuAccess.objects.filter(athens_tenant_id=tenant_id).update(is_enabled=False)
