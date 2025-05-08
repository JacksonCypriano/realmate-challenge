from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    direction = serializers.CharField(source='get_direction_display', read_only=True)

    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['created_at']

class ConversationSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display', read_only=True)
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'status', 'created_at', 'messages']
        read_only_fields = ['created_at']