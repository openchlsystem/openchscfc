from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json
from emailfeedback.models import Email

class EmailListCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_create_email(self):
        url = reverse('email-list-create')
        data = {
            'sender': 'test@example.com',
            'recipient': 'recipient@example.com',
            'subject': 'Test Subject',
            'body': 'This is a test email.',
            'received_date': '2023-03-15T12:00:00Z',
            'raw_message': b''
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Email.objects.count(), 1)
        self.assertEqual(Email.objects.get().sender, 'test@example.com')