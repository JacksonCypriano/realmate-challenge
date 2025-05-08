import uuid
from django.db import models
from .choices import ConversationStatus, MessageDirection

class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=6,
        choices=ConversationStatus.choices,
        default=ConversationStatus.OPEN
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    direction = models.CharField(
        max_length=8,
        choices=MessageDirection.choices,
        default=MessageDirection.RECEIVED
    )
    content = models.TextField()
    timestamp = models.DateTimeField()
    conversation = models.ForeignKey(Conversation, related_name='messages', on_delete=models.CASCADE)
