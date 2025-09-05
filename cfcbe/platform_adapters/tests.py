from django.test import TestCase
from platform_adapters.base_adapter import BaseAdapter
from abc import ABC, abstractmethod

class ConcreteAdapter(BaseAdapter):
    def handle_verification(self, request):
        pass

    def validate_request(self, request):
        pass

    def parse_messages(self, request):
        pass

    def send_message(self, recipient_id, message_content):
        pass

    def format_webhook_response(self, responses):
        pass

class BaseAdapterTestCase(TestCase):
    def test_get_platform_name(self):
        adapter = ConcreteAdapter()
        self.assertEqual(adapter.get_platform_name(), 'concrete')