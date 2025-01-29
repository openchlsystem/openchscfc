from rest_framework import serializers
from .models import Transcription, CaseRecord

class TranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcription
        fields = ["id", "audio_file", "transcript", "created_at"]



class CaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseRecord
        fields = '__all__'


