from datetime import date, timedelta
import uuid

from authentication.models import Project


def create_project(name="Test Project", tenant_id=None):
    tenant_id = tenant_id or uuid.uuid4()
    project = Project.objects.create(
        projectName=name,
        projectCategory=Project.CONSTRUCTION,
        capacity="100",
        location="Site A",
        nearestPoliceStation="Station A",
        nearestPoliceStationContact="000",
        nearestHospital="Hospital A",
        nearestHospitalContact="111",
        commencementDate=date.today(),
        deadlineDate=date.today() + timedelta(days=30),
        athens_tenant_id=tenant_id,
    )
    return project, tenant_id


def create_user(
    user_model,
    username,
    password,
    project,
    tenant_id,
    user_type="adminuser",
    admin_type="clientuser",
):
    user = user_model.objects.create_user(
        username=username,
        password=password,
        user_type=user_type,
        admin_type=admin_type,
        project=project,
    )
    user.athens_tenant_id = tenant_id
    user.save()
    return user
