from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Mom, Notification
import os

User = get_user_model()

class MomLiveFeatureTests(APITestCase):
    def setUp(self):
        # Create users with secure credentials from environment
        admin_password = os.environ.get('TEST_ADMIN_PASSWORD', 'secure_test_admin_pass_123!')
        participant1_password = os.environ.get('TEST_PARTICIPANT1_PASSWORD', 'secure_test_participant1_pass_123!')
        participant2_password = os.environ.get('TEST_PARTICIPANT2_PASSWORD', 'secure_test_participant2_pass_123!')
        
        self.admin_user = User.objects.create_user(username='adminuser', password=admin_password, user_type='adminuser', admin_type='clientuser')
        self.participant1 = User.objects.create_user(username='participant1', password=participant1_password, user_type='clientuser')
        self.participant2 = User.objects.create_user(username='participant2', password=participant2_password, user_type='epcuser')

        # Authenticate as admin user
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin_user)

        # Create a Mom instance
        self.mom = Mom.objects.create(
            title='Test Meeting',
            agenda='Test Agenda',
            meeting_datetime='2025-06-01T10:00:00Z',
            scheduled_by=self.admin_user,
            points_to_discuss='Initial points'
        )
        self.mom.participants.set([self.participant1, self.participant2])

    def test_get_live_meeting_data(self):
        url = reverse('mom-live', kwargs={'pk': self.mom.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('points_to_discuss', response.data)
        self.assertIn('participants', response.data)
        self.assertEqual(len(response.data['participants']), 2)

    def test_update_attendance_and_points(self):
        url = reverse('mom-live-attendance-update', kwargs={'pk': self.mom.id})
        payload = {
            'points_to_discuss': 'Updated points',
            'attendance': [
                {'id': self.participant1.id, 'attended': True},
                {'id': self.participant2.id, 'attended': False},
            ]
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mom.refresh_from_db()
        self.assertEqual(self.mom.points_to_discuss, 'Updated points')
        # Check attendance records
        self.assertTrue(self.mom.participant_attendances.filter(user=self.participant1, attended=True).exists())
        self.assertTrue(self.mom.participant_attendances.filter(user=self.participant2, attended=False).exists())

    def test_mark_meeting_complete(self):
        url = reverse('mom-complete', kwargs={'pk': self.mom.id})
        payload = {
            'completed_at': '2025-06-01T11:00:00Z',
            'duration_minutes': 60
        }
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_send_notification(self):
        url = reverse('mom-notifications-send')
        payload = {
            'user_id': self.participant1.id,
            'title': 'Test Notification',
            'message': 'This is a test notification',
            'type': 'meeting',
            'data': {'momId': self.mom.id},
            'link': '/dashboard/mom/view/{}'.format(self.mom.id)
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Notification.objects.filter(user=self.participant1, title='Test Notification').exists())
