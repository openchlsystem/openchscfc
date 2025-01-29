from rest_framework import serializers
from .models import AudioFile, CaseRecord, ModelVersion, ModelTranscription

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['unique_id', 'audio_file', 'feature_text']

class CaseRecordSerializer(serializers.ModelSerializer):
    unique_id = AudioFileSerializer()  # Nested serializer to include AudioFile data

    class Meta:
        model = CaseRecord
        fields = ['unique_id', 'date', 'talk_time', 'case_id', 'narrative', 'plan', 'main_category', 'sub_category', 'gbv']

class ModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelVersion
        fields = ['version']

class ModelTranscriptionSerializer(serializers.ModelSerializer):
    audio_id = AudioFileSerializer()  # Nested serializer to include AudioFile data
    model_version_id = ModelVersionSerializer()  # Nested serializer to include ModelVersion data

    class Meta:
        model = ModelTranscription
        fields = ['audio_id', 'model_version_id', 'predicted_text', 'wer', 'model_version', 'created_at', 'updated_at']

