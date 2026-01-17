"""Shared test fixtures for creating common test data."""
from django.utils import timezone
from authentication.models import CustomUser, Project
from authentication.tenant_models import AthensTenant
from inductiontraining.models import InductionTraining, InductionAttendance
import uuid


def create_test_tenant(tenant_name='Test Tenant', enabled_modules=None):
    """Create a test tenant with default settings."""
    if enabled_modules is None:
        enabled_modules = ['ptw']
    
    return AthensTenant.objects.create(
        id=uuid.uuid4(),
        master_admin_id=uuid.uuid4(),
        enabled_modules=enabled_modules,
        enabled_menus=[],
        tenant_name=tenant_name,
        is_active=True
    )


def create_test_project(name='Test Project', category=None):
    """Create a test project with default settings."""
    if category is None:
        category = Project.CONSTRUCTION
    
    today = timezone.now().date()
    return Project.objects.create(
        projectName=name,
        projectCategory=category,
        capacity='100',
        location='Test Location',
        nearestPoliceStation='Test PS',
        nearestPoliceStationContact='0000000000',
        nearestHospital='Test Hospital',
        nearestHospitalContact='0000000000',
        commencementDate=today,
        deadlineDate=today
    )


def create_test_user(username='testuser', project=None, tenant=None, admin_type='epcuser'):
    """Create a test user with optional project and tenant."""
    user = CustomUser.objects.create_user(
        username=username,
        email=f'{username}@example.com',
        password='testpass123',
        name='Test',
        surname='User',
        user_type='epcuser',
        admin_type=admin_type,
        grade='C',
        project=project
    )
    
    if tenant:
        user.athens_tenant_id = tenant.id
        user.save(update_fields=['athens_tenant_id'])
    
    return user


def create_test_induction(project, user):
    """Create a test induction training and mark user as attended."""
    induction = InductionTraining.objects.create(
        title='Test Induction',
        description='Test induction',
        date=timezone.now().date(),
        conducted_by='Trainer',
        status='completed',
        project=project,
        created_by=user
    )
    
    InductionAttendance.objects.create(
        induction=induction,
        worker_id=-user.id,
        worker_name=user.username,
        participant_type='user',
        status='present'
    )
    
    return induction


def create_ptw_test_fixtures(username='testuser', tenant_name='PTW Test Tenant'):
    """Create complete PTW test fixtures: tenant, project, user, and induction."""
    tenant = create_test_tenant(tenant_name=tenant_name)
    project = create_test_project()
    user = create_test_user(username=username, project=project, tenant=tenant, admin_type='master')
    induction = create_test_induction(project, user)
    
    return {
        'tenant': tenant,
        'project': project,
        'user': user,
        'induction': induction
    }


def create_ptw_permit_fixtures(user=None, project=None, permit_type_name='Hot Work', permit_type_category='hot_work'):
    """Create PTW-specific permit fixtures: permit type and permit.
    
    Args:
        user: User to create permit for (if None, creates basic fixtures)
        project: Project for permit (if None, creates basic fixtures)
        permit_type_name: Name for permit type
        permit_type_category: Category for permit type
    
    Returns:
        dict with permit_type, permit, and optionally user/project if created
    """
    from ptw.models import PermitType, Permit
    
    # Create basic fixtures if not provided
    created_fixtures = {}
    if user is None or project is None:
        fixtures = create_ptw_test_fixtures()
        if user is None:
            user = fixtures['user']
            created_fixtures['user'] = user
        if project is None:
            project = fixtures['project']
            created_fixtures['project'] = project
        created_fixtures.update({
            'tenant': fixtures['tenant'],
            'induction': fixtures['induction']
        })
    
    # Create permit type
    permit_type = PermitType.objects.create(
        name=permit_type_name,
        category=permit_type_category,
        risk_level='high',
        is_active=True
    )
    
    # Create permit
    permit = Permit.objects.create(
        permit_type=permit_type,
        title=f'Test {permit_type_name} Permit',
        description='Test permit for automated testing',
        location='Test Site A',
        created_by=user,
        project=project,
        status='draft',
        risk_level='high',
        probability=4,
        severity=4,
        planned_start_time=timezone.now(),
        planned_end_time=timezone.now() + timezone.timedelta(hours=8)
    )
    
    result = {
        'permit_type': permit_type,
        'permit': permit,
    }
    result.update(created_fixtures)
    
    return result


def create_ptw_closeout_fixtures(permit=None, template_items=None):
    """Create PTW closeout fixtures: template and closeout record.
    
    Args:
        permit: Permit to create closeout for (if None, creates permit fixtures)
        template_items: List of template items (if None, uses default)
    
    Returns:
        dict with template, closeout, and permit fixtures
    """
    from ptw.models import CloseoutChecklistTemplate, PermitCloseout
    
    # Create permit if not provided
    if permit is None:
        permit_fixtures = create_ptw_permit_fixtures()
        permit = permit_fixtures['permit']
        permit_type = permit_fixtures['permit_type']
    else:
        permit_type = permit.permit_type
        permit_fixtures = {}
    
    # Default template items
    if template_items is None:
        template_items = [
            {'key': 'tools_removed', 'label': 'Tools and equipment removed', 'required': True},
            {'key': 'area_cleaned', 'label': 'Work area cleaned', 'required': True},
            {'key': 'safety_check', 'label': 'Final safety check completed', 'required': True},
            {'key': 'documentation', 'label': 'Documentation completed', 'required': False}
        ]
    
    # Create closeout template
    template = CloseoutChecklistTemplate.objects.create(
        permit_type=permit_type,
        name=f'{permit_type.name} Closeout Checklist',
        risk_level=permit.risk_level,
        items=template_items,
        is_active=True
    )
    
    # Create closeout record
    closeout = PermitCloseout.objects.create(
        permit=permit,
        template=template
    )
    
    result = {
        'template': template,
        'closeout': closeout,
        'permit': permit,
    }
    result.update(permit_fixtures)
    
    return result