from rest_framework import serializers
from .models import WhatsAppMessage, WhatsAppResponse, WhatsAppConversation, IncomingMessage, OutgoingMessage

class WhatsAppMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppMessage
        fields = '__all__'

class WhatsAppResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = WhatsAppResponse
        fields = '__all__'


class WhatsAppConversationSerializer(serializers.ModelSerializer):
    messages = WhatsAppMessageSerializer(many=True, read_only=True)
    responses = WhatsAppResponseSerializer(many=True, read_only=True)

    class Meta:
        model = WhatsAppConversation
        fields = '__all__'


# serializers.py

from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp']


class IncomingMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = IncomingMessage
        fields = '__all__'
        
class OutgoingMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutgoingMessage
        fields = '__all__'