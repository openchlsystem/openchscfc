from django.test import TestCase, Client
from django.urls import reverse
import json

from django.test import TestCase, Client, override_settings

@override_settings(PLATFORM_CONFIGS={
    'whatsapp': {
        'verify_token': 'test_token'
    }
})
class UnifiedWebhookViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_verification(self):
        # Test with a platform that has a verification handler
        url = reverse('unified-webhook', kwargs={'platform': 'whatsapp'})
        response = self.client.get(url, {'hub.mode': 'subscribe', 'hub.challenge': '12345', 'hub.verify_token': 'test_token'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), '12345')

    def test_post_whatsapp_message(self):
        # Test with a simple WhatsApp text message
        url = reverse('unified-webhook', kwargs={'platform': 'whatsapp'})
        data = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "PHONE_NUMBER",
                            "phone_number_id": "PHONE_NUMBER_ID"
                        },
                        "contacts": [{
                            "profile": {
                                "name": "Test User"
                            },
                            "wa_id": "WHATSAPP_ID"
                        }],
                        "messages": [{
                            "from": "SENDER_WHATSAPP_ID",
                            "id": "MESSAGE_ID",
                            "timestamp": "1678886400",
                            "text": {
                                "body": "Hello"
                            },
                            "type": "text"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)