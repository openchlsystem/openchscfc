from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json
from django.contrib.auth import get_user_model

User = get_user_model()

class RequestOTPViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('1234567890')

    def test_request_otp(self):
        url = reverse('request-otp')
        data = {
            'whatsapp_number': '1234567890',
            'org_id': 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)