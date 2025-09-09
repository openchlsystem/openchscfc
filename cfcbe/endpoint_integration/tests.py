from django.test import TestCase
from unittest.mock import patch, MagicMock
from endpoint_integration.message_router import MessageRouter
from shared.models.standard_message import StandardMessage
from django.conf import settings

class MessageRouterTestCase(TestCase):
    def setUp(self):
        self.router = MessageRouter()
        settings.ENDPOINT_CONFIG = {
            'cases_endpoint': {
                'url': 'http://test.cases.com/api',
                'auth_token': 'test_cases_token',
                'formatter': 'cases'
            },
            'messaging_endpoint': {
                'url': 'http://test.messaging.com/api',
                'auth_token': 'test_messaging_token',
                'formatter': 'messaging'
            }
        }

    @patch('requests.post')
    def test_route_to_cases_endpoint(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'cases': [['123']]}
        mock_post.return_value = mock_response

        message = StandardMessage(
            source='webform',
            source_uid='test_webform_uid',
            source_address='test_webform_address',
            message_id='test_webform_message_id',
            source_timestamp=1678886400.0,
            content='Test complaint content',
            platform='webform',
            content_type='text/plain',
            metadata={'victim': {'name': 'John Doe'}, 'perpetrator': {'name': 'Jane Doe'}}
        )

        response = self.router.route_to_endpoint(message)
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['case_id'], '123')
        mock_post.assert_called_once()

    @patch('requests.post')
    def test_route_to_messaging_endpoint(self, mock_post):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'id': 'msg_id_123'}
        mock_post.return_value = mock_response

        message = StandardMessage(
            source='whatsapp',
            source_uid='test_whatsapp_uid',
            source_address='test_whatsapp_address',
            message_id='test_whatsapp_message_id',
            source_timestamp=1678886400.0,
            content='Hello from WhatsApp',
            platform='whatsapp',
            content_type='text/plain'
        )

        response = self.router.route_to_endpoint(message)
        self.assertEqual(response['status'], 'success')
        self.assertEqual(response['message_id'], 'msg_id_123')
        mock_post.assert_called_once()