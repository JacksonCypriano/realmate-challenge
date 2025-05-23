import json
from channels.generic.websocket import AsyncWebsocketConsumer

import logging

logger = logging.getLogger(__name__)

class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'conversation_{self.conversation_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        logger.warning(f"Conexão WebSocket estabelecida com sucesso para o grupo {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        logger.warning(f"Mensagem recebida no grupo {self.room_group_name}: {message}")
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']
        logger.warning(f"Mensagem recebida no grupo {self.room_group_name}: {message}")

        await self.send(text_data=json.dumps({
            'message': message
        }))