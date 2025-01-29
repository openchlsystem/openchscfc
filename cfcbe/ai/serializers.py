from rest_framework import serializers
from .models import AudioFile, ModelTranscription, ModelVersion, TriageRule, TriageAnalysis, Department, CaseHistory, ComplaintRouting, Complaint

class TriageRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriageRule
        fields = '__all__'

class TriageAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriageAnalysis
        fields = '__all__'

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'

class CaseHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseHistory
        fields = '__all__'

class ComplaintRoutingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintRouting
        fields = '__all__'

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'


class AudioFileSerializer(serializers.ModelSerializer):
    file_name = serializers.CharField(read_only=True)

    class Meta:
        model = AudioFile
        fields = ['file_name', 'audio_file', 'feature_text', 'narrative']

class ModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelVersion
        fields = ['version']

class ModelTranscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModelTranscription
        fields = ['audio_id', 'model_version_id', 'predicted_text', 'wer', 'model_version']
