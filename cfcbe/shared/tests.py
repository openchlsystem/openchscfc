from django.test import TestCase
from shared.models.standard_message import StandardMessage

class StandardMessageModelTestCase(TestCase):
    def test_create_standard_message(self):
        message = StandardMessage(
            source='test_source',
            source_uid='test_uid',
            source_address='test_address',
            message_id='test_message_id',
            source_timestamp=1234567890.0,
            content='Test content',
            platform='test_platform',
            content_type='text/plain',
            media_url='http://example.com/media.jpg',
            media_content=b'test_media_content',
            media_mime='image/jpeg',
            media_filename='media.jpg',
            media_size=100,
            metadata={'key': 'value'}
        )
        self.assertIsInstance(message, StandardMessage)
        self.assertEqual(message.source, 'test_source')
        self.assertEqual(message.content, 'Test content')