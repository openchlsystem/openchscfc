from rest_framework import serializers
from webhook_handler.models import (
    Complaint, 
    CaseNote, 
    ComplaintStatus, 
    Person, 
    Voicenote,
    Conversation,
    WebhookMessage,
    Notification
)

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'age', 'gender', 'additional_info']
        extra_kwargs = {
            'age': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True, 'allow_blank': True},
            'additional_info': {'required': False, 'allow_blank': True},
        }


class ComplaintSerializer(serializers.ModelSerializer):
    victim = PersonSerializer(required=False)  
    perpetrator = PersonSerializer(required=False)  
    complaint_image = serializers.ImageField(required=False, allow_null=True)
    complaint_audio = serializers.FileField(required=False, allow_null=True)
    complaint_video = serializers.FileField(required=False, allow_null=True)
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all(), required=False)

    class Meta:
        model = Complaint
        fields = [
            'complaint_id', 'session_id', 'timestamp', 'reporter_nickname', 'case_category',
            'complaint_text', 'complaint_image', 'complaint_audio', 'complaint_video',
            'message_id_ref', 'victim', 'perpetrator', 'created_at', 'conversation'
        ]
        read_only_fields = ['complaint_id', 'created_at', 'timestamp']

    def create(self, validated_data):
        victim_data = validated_data.pop('victim', None)
        perpetrator_data = validated_data.pop('perpetrator', None)

        # Create victim if data provided
        victim = None
        if victim_data:
            victim = Person.objects.create(**victim_data)
            
        # Create perpetrator if data provided
        perpetrator = None
        if perpetrator_data:
            perpetrator = Person.objects.create(**perpetrator_data)

        # Set the related objects
        validated_data['victim'] = victim
        validated_data['perpetrator'] = perpetrator

        # Create and return the complaint
        return Complaint.objects.create(**validated_data)
    
    def validate_complaint_image(self, value):
        if value and value.size > 5 * 1024 * 1024:  # 5MB limit
            raise serializers.ValidationError("Image file is too large (max 5MB)")
        return value

    def validate_complaint_audio(self, value):
        if value and value.size > 10 * 1024 * 1024:  # 10MB limit
            raise serializers.ValidationError("Audio file is too large (max 10MB)")
        return value
    
    def validate_complaint_video(self, value):
        if value and value.size > 20 * 1024 * 1024:  # 20MB limit
            raise serializers.ValidationError("Video file is too large (max 20MB)")
        return value


class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ['id', 'complaint', 'note_text', 'note_audio', 'created_at', 'created_by']
        read_only_fields = ['created_at']

    def create(self, validated_data):
        # Ensure complaint field is required
        complaint = validated_data.get('complaint')
        if not complaint:
            raise serializers.ValidationError('Complaint field is required.')

        # Create and return the CaseNote instance
        return CaseNote.objects.create(**validated_data)


class ComplaintStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintStatus
        fields = ['id', 'complaint', 'status', 'updated_at', 'updated_by']
        read_only_fields = ['updated_at']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.save()
        return instance
    
    def create(self, validated_data):
        status = super().create(validated_data)
        # Log status change in system
        complaint = validated_data.get('complaint')
        if complaint:
            # Create notification for status change
            Notification.objects.create(
                complaint=complaint,
                message=f"Status updated to: {validated_data.get('status')}",
                is_read=False
            )
        return status


class VoicenotesSerializer(serializers.ModelSerializer):
    complaint = serializers.PrimaryKeyRelatedField(queryset=Complaint.objects.all(), required=False)
    
    class Meta:
        model = Voicenote
        fields = ['id', 'complaint', 'voicenote', 'created_at']
        read_only_fields = ['created_at']
    
    def validate_voicenote(self, value):
        if value and hasattr(value, 'size') and value.size > 15 * 1024 * 1024:  # 15MB limit
            raise serializers.ValidationError("Voice note file is too large (max 15MB)")
        return value


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_id', 'complaint', 'message', 'is_read', 'created_at']
        read_only_fields = ['notification_id', 'created_at']


# Serializer for simplified complaint listings
class ComplaintListSerializer(serializers.ModelSerializer):
    victim_name = serializers.SerializerMethodField()
    perpetrator_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    
    class Meta:
        model = Complaint
        fields = [
            'complaint_id', 'reporter_nickname', 'case_category',
            'created_at', 'victim_name', 'perpetrator_name', 'status'
        ]
    
    def get_victim_name(self, obj):
        return obj.victim.name if obj.victim else None
    
    def get_perpetrator_name(self, obj):
        return obj.perpetrator.name if obj.perpetrator else None
    
    def get_status(self, obj):
        status = ComplaintStatus.objects.filter(complaint=obj).order_by('-updated_at').first()
        return status.status if status else 'New'