import os
import django


os.environ['DJANGO_SETTINGS_MODULE'] = 'realmate_challenge.settings'
django.setup()

from rest_framework.test import APITestCase
from rest_framework import status
from .models import Conversation, Message
from uuid import uuid4

class WebhookTests(APITestCase):
    def test_create_conversation(self):
        url = '/conversations/webhook/'
        data = {
            "type": "NEW_CONVERSATION",
            "timestamp": "2025-02-21T10:20:41.349308",
            "data": {
                "id": str(uuid4())
            }
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        conversation = Conversation.objects.get(id=data["data"]["id"])
        self.assertEqual(conversation.status, 'OPEN')
    
    def test_create_message(self):
        conversation = Conversation.objects.create(id=str(uuid4()), status='OPEN')

        url = '/conversations/webhook/'
        data = {
            "type": "NEW_MESSAGE",
            "timestamp": "2025-02-21T10:20:42.349308",
            "data": {
                "id": str(uuid4()),
                "direction": "RECEIVED",
                "content": "Olá, tudo bem?",
                "conversation_id": conversation.id
            }
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        message = Message.objects.get(id=data["data"]["id"])
        self.assertEqual(message.content, "Olá, tudo bem?")
        self.assertEqual(message.direction, "RECEIVED")
    
    def test_create_message_on_closed_conversation(self):
        conversation = Conversation.objects.create(id=str(uuid4()), status='CLOSED')

        url = '/conversations/webhook/'
        data = {
            "type": "NEW_MESSAGE",
            "timestamp": "2025-02-21T10:20:42.349308",
            "data": {
                "id": str(uuid4()),
                "direction": "SENT",
                "content": "Tudo ótimo e você?",
                "conversation_id": conversation.id
            }
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('A conversa está encerrada', response.data['error'])

    def test_missing_required_fields(self):
        conversation = Conversation.objects.create(id=str(uuid4()), status='OPEN')

        url = '/conversations/webhook/'
        data = {
            "type": "NEW_MESSAGE",
            "timestamp": "2025-02-21T10:20:42.349308",
            "data": {
                "id": str(uuid4()),
                "direction": "SENT",
                "content": "Mensagem sem ID",
            }
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Campos obrigatórios ausentes", response.data['error'])

class ConversationTests(APITestCase):

    def test_get_conversation(self):
        conversation = Conversation.objects.create(id=str(uuid4()), status='OPEN')

        self.assertIsNotNone(conversation.id)

        url = f'/conversations/conversations/{conversation.id}/'
        print(f"URL: {url}")

        response = self.client.get(url)
        print(f"Response data: {response.data}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(response.data['id'], str(conversation.id))
        self.assertEqual(response.data['status'], 'OPEN')

    def test_get_nonexistent_conversation(self):
        url = '/conversations/nonexistent-id/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
