import logging
import traceback

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework.views import APIView
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.db import IntegrityError

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .choices import ConversationStatus
from .utils import parse_webhook_timestamp

logger = logging.getLogger(__name__)


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_params = {}

        for param, value in self.request.query_params.items():
            if param in [field.name for field in Conversation._meta.fields]:
                filter_params[param] = value
            elif '__' in param and param.split('__')[0] in [field.name for field in Conversation._meta.fields]:
                filter_params[param] = value

        if filter_params:
            queryset = queryset.filter(**filter_params)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": "Conversa criada com sucesso.", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"error": "Erro ao criar conversa.", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        conversation = self.get_object()
        if conversation.status == ConversationStatus.CLOSED:
            return Response({"error": "Esta conversa já está encerrada."}, status=status.HTTP_400_BAD_REQUEST)

        conversation.status = ConversationStatus.CLOSED
        conversation.save()
        return Response({"success": "Conversa encerrada com sucesso."}, status=status.HTTP_200_OK)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = super().get_queryset()
        filter_params = {}

        for param, value in self.request.query_params.items():
            if param in [field.name for field in Message._meta.fields]:
                filter_params[param] = value
            elif '__' in param and param.split('__')[0] in [field.name for field in Message._meta.fields]:
                filter_params[param] = value

        if filter_params:
            queryset = queryset.filter(**filter_params)

        return queryset

    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation")
        if not conversation_id:
            return Response({"error": "ID da conversa é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Conversa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if conversation.status == ConversationStatus.CLOSED:
            return Response({"error": "Não é possível adicionar mensagens a uma conversa encerrada."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def create_response(self, serializer):
        return Response({"success": "Mensagem registrada com sucesso.", "data": serializer.data}, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response({"success": "Mensagem excluída com sucesso."}, status=status.HTTP_204_NO_CONTENT)


class WebhookView(APIView):
    def post(self, request, *args, **kwargs):
        event_type = request.data.get("type")
        timestamp = request.data.get("timestamp")
        data = request.data.get("data")

        if not event_type or not data:
            return Response({"error": "Tipo de evento e dados são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if event_type == "NEW_CONVERSATION":
                conversation_id = data.get("id")
                if not conversation_id:
                    raise ValueError("ID da conversa é obrigatório.")

                conversation = Conversation.objects.create(
                    id=conversation_id,
                    status="OPEN",
                    created_at=parse_webhook_timestamp(timestamp)
                )
                return Response({"success": "Conversa criada com sucesso.", "id": conversation.id}, status=status.HTTP_201_CREATED)

            elif event_type == "NEW_MESSAGE":
                message_id = data.get("id")
                direction = data.get("direction")
                content = data.get("content")
                conversation_id = data.get("conversation_id")

                missing_fields = []

                if not message_id:
                    missing_fields.append("id")

                if not direction:
                    missing_fields.append("direction")
                
                if not content:
                    missing_fields.append("content")

                if not conversation_id:
                    missing_fields.append("conversation_id")

                if missing_fields:
                    raise ValueError(f"Campos obrigatórios ausentes: {', '.join(missing_fields)}")

                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    return Response({"error": "Conversa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

                if conversation.status == "CLOSED":
                    return Response({"error": "A conversa está encerrada e não pode receber novas mensagens."}, status=status.HTTP_400_BAD_REQUEST)

                Message.objects.create(
                    id = message_id,
                    direction=direction,
                    content=content,
                    conversation=conversation,
                    created_at=parse_webhook_timestamp(timestamp),
                    timestamp=parse_webhook_timestamp(timestamp)
                )

                if direction == "RECEIVED":
                    channel_layer = get_channel_layer()
                    logger.warning(f"Channel layer obtido: {channel_layer}")
                    logger.warning(f"Enviando para o grupo 'conversation_{conversation_id}' a mensagem: {content}")

                    async_to_sync(channel_layer.group_send)(
                        f'conversation_{conversation_id}',
                        {
                            'type': 'chat_message',
                            'message': content
                        }
                    )

                return Response({"success": "Mensagem registrada com sucesso."}, status=status.HTTP_201_CREATED)

            elif event_type == "CLOSE_CONVERSATION":
                conversation_id = data.get("id")
                if not conversation_id:
                    raise ValueError("ID da conversa é obrigatório.")

                try:
                    conversation = Conversation.objects.get(id=conversation_id)
                except Conversation.DoesNotExist:
                    return Response({"error": "Conversa não encontrada."}, status=status.HTTP_404_NOT_FOUND)

                conversation.status = "CLOSED"
                conversation.save()

                return Response({"success": "Conversa encerrada com sucesso."}, status=status.HTTP_200_OK)

            else:
                return Response({"error": f"Tipo de evento '{event_type}' não é suportado."}, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            tb = traceback.extract_tb(e.__traceback__)
            last = tb[-1]
            logger.error({
                'error': 'ID duplicado. A entidade já existe.',
                'file': last.filename,
                'line': last.lineno,
                'function': last.name,
                'code': last.line
            })
            return Response({"error": "ID duplicado. A entidade já existe."}, status=status.HTTP_409_CONFLICT)
        
        except ValueError as e:
            logger.error(str(e))
            return Response({"error": str(e)}, status=400)
        
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            last = tb[-1]
            logger.error({
                "detail": "Erro interno ao processar o webhook.",
                "error": str(e),
                'file': last.filename,
                'line': last.lineno,
                'function': last.name,
                'code': last.line
            })
            return Response({"detail": "Erro interno ao processar o webhook.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)