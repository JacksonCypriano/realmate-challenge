from django.db import models

class ConversationStatus(models.TextChoices):
    OPEN = 'OPEN', 'Aberta'
    CLOSED = 'CLOSED', 'Fechada'


class MessageDirection(models.TextChoices):
    SENT = 'SENT', 'Enviada'
    RECEIVED = 'RECEIVED', 'Recebida'
