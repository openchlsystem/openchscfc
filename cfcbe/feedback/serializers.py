from rest_framework import serializers
from .models import (
    Category, Complaint, AudioFile, Translation,
    Feedback, Metric, TriageLog, CaseworkerAction, Notification
)


# Category Serializer
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

# Complaint Serializer
class ComplaintSerializer(serializers.ModelSerializer):
# Include user details in the response
    category = CategorySerializer(read_only=True)  # Include category details
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )  # For creating/updating with category

    class Meta:
        model = Complaint
        fields = '__all__'

# Audio File Serializer
class AudioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioFile
        fields = '__all__'
        

# Translation Serializer
class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Translation
        fields = '__all__'


# Feedback Serializer
class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'


# Metric Serializer
class MetricSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metric
        fields = '__all__'
        

# Triage Log Serializer
class TriageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriageLog
        fields = '__all__'


# Caseworker Action Serializer
class CaseworkerActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseworkerAction
        fields = '__all__'


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

