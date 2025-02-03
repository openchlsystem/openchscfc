from rest_framework import serializers
from .models import Complaint, CaseNote, ComplaintStatus, Person, Voicenotes

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'age', 'gender', 'additional_info']
        extra_kwargs = {
            'age': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True, 'allow_blank': True},
            'additional_info': {'required': False, 'allow_blank': True},
        }

# Serializer for the Complaint model
class ComplaintSerializer(serializers.ModelSerializer):
    victim = PersonSerializer(required=False)  # Nested serializer for the victim
    perpetrator = PersonSerializer(required=False)  # Nested serializer for the perpetrator

    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['complaint_id', 'created_at']

    def create(self, validated_data):
        # Extract and remove nested victim and perpetrator data
        victim_data = validated_data.pop('victim', None)
        perpetrator_data = validated_data.pop('perpetrator', None)

        # Initialize victim and perpetrator as None
        victim = None
        perpetrator = None

        # Create victim and perpetrator instances if the data is provided
        if victim_data:
            victim = Person.objects.create(**victim_data)
        if perpetrator_data:
            perpetrator = Person.objects.create(**perpetrator_data)

        # Add the victim and perpetrator objects to validated data before creating the complaint
        if victim:
            validated_data['victim'] = victim
        if perpetrator:
            validated_data['perpetrator'] = perpetrator

        # Create and return the complaint instance
        complaint = Complaint.objects.create(**validated_data)
        return complaint

# Serializer for the CaseNote model
class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ['complaint', 'note_text', 'note_audio', 'created_at', 'created_by']
        read_only_fields = ['created_at', 'complaint']

    def create(self, validated_data):
        # Ensure complaint field is required
        complaint = validated_data.get('complaint')
        if not complaint:
            raise serializers.ValidationError('Complaint field is required.')

        # Create and return the CaseNote instance
        case_note = CaseNote.objects.create(**validated_data)
        return case_note

# Serializer for the ComplaintStatus model
class ComplaintStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintStatus
        fields = ['complaint', 'status', 'updated_at', 'updated_by']
        read_only_fields = ['complaint', 'updated_at']

    def update(self, instance, validated_data):
        instance.status = validated_data.get('status', instance.status)
        instance.updated_by = validated_data.get('updated_by', instance.updated_by)
        instance.save()
        return instance

# Serializer for Voicenotes model
class VoicenotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voicenotes
        fields = ['id', 'voicenote', 'created_at']
