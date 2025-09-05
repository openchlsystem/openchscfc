from rest_framework import serializers
from .models import AudioFileChunk, ModelTranscription, CaseRecord, AudioFile, ModelVersion

class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = '__all__'

class ModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelVersion
        fields = '__all__'

class ModelTranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTranscription
        fields = '__all__'

class AudioFileChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFileChunk
        fields = '__all__'

class AudioFileChunkUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFileChunk
        fields = ['true_transcription', 'is_rejected']

class CaseRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseRecord
        fields = '__all__'
