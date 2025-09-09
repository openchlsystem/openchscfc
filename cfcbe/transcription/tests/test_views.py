
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch, MagicMock
from django.core.files.uploadedfile import SimpleUploadedFile

class TranscribeAudioViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('transcribe_audio')

    @patch('transcription.views.transcribe_audio_file')
    @patch('transcription.views.AudioFile.objects.get_or_create')
    @patch('transcription.views.ModelTranscription.objects.create')
    @patch('transcription.views.ModelVersion.objects.get_or_create')
    def test_transcribe_audio_success(self, mock_get_or_create_model_version, mock_create_transcription, mock_get_or_create_audio_file, mock_transcribe_audio_file):
        # Mock transcription
        mock_transcribe_audio_file.return_value = 'This is a test transcription.'

        # Mock AudioFile.objects.get_or_create
        mock_audio_file_instance = MagicMock()
        mock_audio_file_instance.unique_id = 'test_audio'
        mock_audio_file_instance.audio_file.path = '/tmp/test_audio.mp3'
        mock_get_or_create_audio_file.return_value = (mock_audio_file_instance, True)

        # Mock ModelVersion.objects.get_or_create
        mock_model_version_instance = MagicMock()
        mock_get_or_create_model_version.return_value = (mock_model_version_instance, True)

        # Create a dummy audio file
        audio_file = SimpleUploadedFile("test_audio.mp3", b"file_content", content_type="audio/mpeg")

        response = self.client.post(self.url, {'audio_file': audio_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['model_transcription'], 'This is a test transcription.')
        mock_transcribe_audio_file.assert_called_once()
        mock_get_or_create_audio_file.assert_called_once()
        mock_create_transcription.assert_called_once()

    def test_transcribe_audio_no_file(self):
        response = self.client.post(self.url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'No audio file provided')
