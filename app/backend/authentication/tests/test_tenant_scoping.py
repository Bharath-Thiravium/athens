import os
import uuid
from datetime import date, timedelta

import pytest
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from authentication.models import CustomUser, Project


TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "masterpassword")


def _create_project(tenant_id: uuid.UUID, name: str) -> Project:
    return Project.objects.create(
        projectName=name,
        projectCategory=Project.CONSTRUCTION,
        capacity="100",
        location="Test Location",
        nearestPoliceStation="Test Police Station",
        nearestPoliceStationContact="000",
        nearestHospital="Test Hospital",
        nearestHospitalContact="111",
        commencementDate=date.today(),
        deadlineDate=date.today() + timedelta(days=30),
        athens_tenant_id=tenant_id,
    )


@override_settings(FEATURE_FLAGS={"FF_TENANT_SCOPE_V2": True})
@pytest.mark.django_db
def test_authentication_writes_require_tenant_and_project():
    client = APIClient()
    tenant_id = uuid.uuid4()
    project = _create_project(tenant_id, "Project A")

    user = CustomUser.objects.create_user(
        username="scoped_user",
        password=TEST_PASSWORD,
        user_type="projectadmin",
        admin_type="client",
        project=project,
    )

    url = reverse("userdetail_retrieve_update")

    # Case A: missing tenant scope
    user.athens_tenant_id = None
    user.save()
    client.force_authenticate(user=user)
    response = client.patch(url, {"mobile": "1234567890"}, format="multipart")
    assert response.status_code == 403

    # Case B: missing project scope
    user.athens_tenant_id = tenant_id
    user.project = None
    user.save()
    response = client.patch(url, {"mobile": "0987654321"}, format="multipart")
    assert response.status_code == 403


@override_settings(FEATURE_FLAGS={"FF_TENANT_SCOPE_V2": True})
@pytest.mark.django_db
def test_cross_tenant_access_forbidden():
    client = APIClient()
    tenant_a = uuid.uuid4()
    tenant_b = uuid.uuid4()

    project_a = _create_project(tenant_a, "Project A")
    project_b = _create_project(tenant_b, "Project B")

    user_a = CustomUser.objects.create_user(
        username="tenant_a_user",
        password=TEST_PASSWORD,
        user_type="projectadmin",
        admin_type="client",
        project=project_a,
        athens_tenant_id=tenant_a,
    )

    client.force_authenticate(user=user_a)
    url = reverse("project_update", kwargs={"pk": project_b.id})
    response = client.put(
        url,
        {
            "projectName": project_b.projectName,
            "projectCategory": project_b.projectCategory,
            "capacity": project_b.capacity,
            "location": project_b.location,
            "nearestPoliceStation": project_b.nearestPoliceStation,
            "nearestPoliceStationContact": project_b.nearestPoliceStationContact,
            "nearestHospital": project_b.nearestHospital,
            "nearestHospitalContact": project_b.nearestHospitalContact,
            "commencementDate": project_b.commencementDate.isoformat(),
            "deadlineDate": project_b.deadlineDate.isoformat(),
        },
        format="json",
    )
    assert response.status_code == 403


@override_settings(FEATURE_FLAGS={"FF_TENANT_SCOPE_V2": True})
@pytest.mark.django_db
def test_cross_project_access_forbidden():
    client = APIClient()
    tenant_id = uuid.uuid4()

    project_a = _create_project(tenant_id, "Project A")
    project_b = _create_project(tenant_id, "Project B")

    user_a = CustomUser.objects.create_user(
        username="project_a_user",
        password=TEST_PASSWORD,
        user_type="projectadmin",
        admin_type="client",
        project=project_a,
        athens_tenant_id=tenant_id,
    )

    client.force_authenticate(user=user_a)
    url = reverse("project_update", kwargs={"pk": project_b.id})
    response = client.put(
        url,
        {
            "projectName": project_b.projectName,
            "projectCategory": project_b.projectCategory,
            "capacity": project_b.capacity,
            "location": project_b.location,
            "nearestPoliceStation": project_b.nearestPoliceStation,
            "nearestPoliceStationContact": project_b.nearestPoliceStationContact,
            "nearestHospital": project_b.nearestHospital,
            "nearestHospitalContact": project_b.nearestHospitalContact,
            "commencementDate": project_b.commencementDate.isoformat(),
            "deadlineDate": project_b.deadlineDate.isoformat(),
        },
        format="json",
    )
    assert response.status_code == 403


@override_settings(FEATURE_FLAGS={"FF_TENANT_SCOPE_V2": True})
@pytest.mark.django_db
def test_exempt_auth_endpoints_still_work():
    client = APIClient()
    tenant_id = uuid.uuid4()
    project = _create_project(tenant_id, "Project A")

    user = CustomUser.objects.create_user(
        username="login_user",
        password=TEST_PASSWORD,
        user_type="projectadmin",
        admin_type="client",
        project=project,
        athens_tenant_id=tenant_id,
    )

    login_url = reverse("secure_login")
    login_response = client.post(
        login_url,
        {"username": user.username, "password": TEST_PASSWORD},
        format="json",
    )
    assert login_response.status_code != 403

    refresh_token = login_response.data.get("refresh")
    access_token = login_response.data.get("access")

    refresh_url = reverse("token_refresh")
    refresh_response = client.post(refresh_url, {"refresh": refresh_token}, format="json")
    assert refresh_response.status_code != 403

    ws_refresh_url = reverse("token_refresh_ws")
    ws_refresh_response = client.post(ws_refresh_url, {"refresh": refresh_token}, format="json")
    assert ws_refresh_response.status_code != 403

    logout_url = reverse("auth_logout")
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
    logout_response = client.post(logout_url, {"refresh": refresh_token}, format="json")
    assert logout_response.status_code != 403
