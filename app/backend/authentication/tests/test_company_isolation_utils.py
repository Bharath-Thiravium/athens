import uuid
from datetime import date, timedelta

from django.test import TestCase

from authentication.company_isolation import get_company_isolated_queryset
from authentication.models import CustomUser, Project


class CompanyIsolationUtilsTests(TestCase):
    def setUp(self):
        self.tenant_id = uuid.uuid4()
        self.other_tenant_id = uuid.uuid4()

        self.project_a = Project.objects.create(
            projectName="Project A",
            projectCategory=Project.CONSTRUCTION,
            capacity="100",
            location="Site A",
            nearestPoliceStation="Station A",
            nearestPoliceStationContact="000",
            nearestHospital="Hospital A",
            nearestHospitalContact="111",
            commencementDate=date.today(),
            deadlineDate=date.today() + timedelta(days=30),
            athens_tenant_id=self.tenant_id,
        )
        self.project_b = Project.objects.create(
            projectName="Project B",
            projectCategory=Project.CONSTRUCTION,
            capacity="200",
            location="Site B",
            nearestPoliceStation="Station B",
            nearestPoliceStationContact="222",
            nearestHospital="Hospital B",
            nearestHospitalContact="333",
            commencementDate=date.today(),
            deadlineDate=date.today() + timedelta(days=60),
            athens_tenant_id=self.other_tenant_id,
        )

        self.user = CustomUser.objects.create_user(
            username="user_a",
            password="Password123!",
            user_type="adminuser",
            admin_type="clientuser",
            project=self.project_a,
        )
        self.user.athens_tenant_id = self.tenant_id
        self.user.save()

    def test_get_company_isolated_queryset_filters_by_tenant(self):
        queryset = get_company_isolated_queryset(Project.objects.all(), self.user)
        self.assertEqual(list(queryset), [self.project_a])
