from django.shortcuts import render
from django.utils.timezone import now
from apps.conversations.models import Conversation
import logging

logger = logging.getLogger(__name__)

def conversation_list(request):
    conversations = Conversation.objects.all()
    return render(request, 'frontend/conversations.html', {'conversations': conversations})

def conversation_detail(request, conversation_id):
    conversation = Conversation.objects.prefetch_related('messages').get(id=conversation_id)
    return render(request, 'frontend/conversation_detail.html', {
        'conversation': conversation,
        'timestamp': int(now().timestamp()),
    })
