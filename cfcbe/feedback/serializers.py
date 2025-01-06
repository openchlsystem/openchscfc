from rest_framework import serializers
from .models import Complaint, CaseNote, ComplaintStatus, Person

# Serializer for the Person model (Victim/Perpetrator)
class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name', 'age', 'gender', 'additional_info']

# Serializer for the Complaint model
class ComplaintSerializer(serializers.ModelSerializer):
    victim = PersonSerializer(required=False)  # Nested serializer for the victim
    perpetrator = PersonSerializer(required=False)  # Nested serializer for the perpetrator

    class Meta:
        model = Complaint
        fields = ['complaint_id', 'reporter_nickname', 'case_category', 'complaint_text', 
                  'complaint_audio', 'victim', 'perpetrator', 'created_at']
        read_only_fields = ['complaint_id', 'created_at']

    def create(self, validated_data):
        # Separate nested victim and perpetrator data, if provided
        victim_data = validated_data.pop('victim', None)
        perpetrator_data = validated_data.pop('perpetrator', None)

        # Create the complaint first
        complaint = Complaint.objects.create(**validated_data)

        # Create related victim and perpetrator if data is provided
        if victim_data:
            victim = Person.objects.create(**victim_data)
            complaint.victim = victim
            complaint.save()

        if perpetrator_data:
            perpetrator = Person.objects.create(**perpetrator_data)
            complaint.perpetrator = perpetrator
            complaint.save()

        return complaint

# Serializer for the CaseNote model
class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = ['complaint', 'note_text', 'note_audio', 'created_at', 'created_by']
        read_only_fields = ['created_at', 'complaint']

    def create(self, validated_data):
        complaint = validated_data.get('complaint')
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
