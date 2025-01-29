from rest_framework import serializers
<<<<<<< HEAD
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
=======
from .models import Transcription, CaseRecord, AudioFile, Transcription_done

# Serializer for AudioFile model
class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = ['id', 'file', 'file_size', 'duration', 'created_at']

# Serializer for Transcription model
class TranscriptionSerializer(serializers.ModelSerializer):
    # Include related AudioFile details in the serialization
    #audio_file = AudioFileSerializer(read_only=True)  # Displaying audio file details

    class Meta:
        model = Transcription
        fields = '__all__'

# Serializer for CaseRecord model
class CaseRecordSerializer(serializers.ModelSerializer):
    # Include related AudioFile and Transcriptions
    audio_file = AudioFileSerializer(read_only=True)
    transcriptions = TranscriptionSerializer(read_only=True, many=True)  # Nested serializer for transcriptions
>>>>>>> 8ac1186 (Updated files)

    class Meta:
        model = CaseRecord
        fields = ['id', 'unique_id', 'date', 'talk_time', 'case_id', 'narrative', 'plan', 'main_category', 
                  'sub_category', 'gbv', 'audio_file', 'transcriptions']
