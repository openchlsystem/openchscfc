from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
import json

from feedback.models import Complaint, Person

class ComplaintViewSetTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.person = Person.objects.create(name='Test Person')

    def test_create_complaint(self):
        url = reverse('complaint-list')
        data = {
            'reporter_nickname': 'testuser',
            'case_category': 'test category',
            'complaint_text': 'This is a test complaint.',
            'victim': self.person.id,
            'perpetrator': self.person.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Complaint.objects.count(), 1)
        self.assertEqual(Complaint.objects.get().reporter_nickname, 'testuser')