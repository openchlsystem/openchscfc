from rest_framework import serializers
from .models import AudioFile, RawData, TriageRule, TriageAnalysis, Department, CaseHistory, ComplaintRouting, Complaint

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
    class Meta:
        model = AudioFile
        fields = ['unique_id', 'audio_data']

class RawDataSerializer(serializers.ModelSerializer):
    unique_id = AudioFileSerializer()  # Nested serializer to include AudioFile data

    class Meta:
        model = RawData
        fields = ['unique_id', 'date', 'talk_time', 'case_id', 'narrative', 'plan', 'main_category', 'sub_category', 'gbv']
