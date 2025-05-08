
# Plataforma de Gerenciamento de Conversas

Este projeto é uma aplicação web desenvolvida para receber, exibir e gerenciar conversas e mensagens de um sistema de atendimento via WhatsApp. Os eventos são recebidos via Webhook e processados em tempo real por meio de uma arquitetura assíncrona baseada em Django, Redis e WebSockets.

## Tecnologias

- Django
- Django Rest Framework
- Poetry
- SQLite

## Requisitos

Antes de começar, você precisa ter o Python 3.7+ e o Poetry instalados em sua máquina.

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/inboxflow.git
cd realmate-challenge
```

### 2. Instalar dependências

Com o Poetry instalado, execute o seguinte comando para instalar as dependências:

```bash
poetry install
```

### 3. Migrar o banco de dados

Aplique as migrações do banco de dados SQLite:

```bash
python manage.py migrate
```

### 4. Executar o servidor

Inicie o servidor de desenvolvimento:

```bash
python manage.py runserver
```

Agora sua API estará rodando em `http://localhost:8000`.

## Endpoints

### `/webhook/` [POST]

Este endpoint recebe os eventos via Webhook. Ele suporta os seguintes tipos de eventos:

- `NEW_CONVERSATION`: Cria uma nova conversa.
- `NEW_MESSAGE`: Adiciona uma nova mensagem à conversa.
- `CLOSE_CONVERSATION`: Marca uma conversa como encerrada.

**Exemplo de requisição para `NEW_CONVERSATION`:**

```json
{
    "type": "NEW_CONVERSATION",
    "timestamp": "2025-02-21T10:20:41.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```
