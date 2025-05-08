# Plataforma de Gerenciamento de Conversas

Este projeto é uma aplicação web desenvolvida para receber, exibir e gerenciar conversas e mensagens de um sistema de atendimento via WhatsApp. Os eventos são recebidos via Webhook e processados em tempo real por meio de uma arquitetura assíncrona baseada em Django, Redis e WebSockets.

> Desenvolvido por **Jackson Cypriano Cobra**.

## Tecnologias

- Django
- Django Rest Framework
- Django Channels
- Daphne
- Redis
- Poetry
- Docker
- SQLite

## Requisitos

Você precisará do Docker e Docker Compose instalados.

### 📦 Instalar Docker

#### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install docker.io docker-compose -y
sudo systemctl enable docker
sudo systemctl start docker
```

Adicione seu usuário ao grupo docker para evitar usar `sudo`:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### Windows

- Instale o **Docker Desktop** via: https://www.docker.com/products/docker-desktop/
- Após a instalação, reinicie o computador e abra o Docker Desktop antes de usar os comandos abaixo.

## Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/JacksonCypriano/realmate-challenge.git
cd realmate-challenge
```

### 2. Iniciar containers Docker

```bash
docker compose up --build
```

A aplicação estará disponível em `http://localhost:8000`.

### 3. Criar migrações e aplicar no banco (dentro do container)

Abra outro terminal:

```bash
docker exec -it django_app poetry run python manage.py makemigrations
docker exec -it django_app poetry run python manage.py migrate
```

## Frontend

O frontend está localizado na pasta /frontend/ e será servido automaticamente junto com o backend no container Docker.
Você pode acessá-lo diretamente em: http://localhost:8000/frontend/

Certifique-se de que o container Docker esteja rodando corretamente para que a comunicação via WebSocket entre o backend e o frontend funcione como esperado, utilizando Django Channels, Daphne e Redis para suportar operações assíncronas em tempo real.

## WebSocket, Channels e Redis

Este projeto utiliza **Django Channels**, **Daphne** e **Redis** para suportar comunicação assíncrona em tempo real entre o backend e o frontend.

- **Channels** permite lidar com WebSockets e outras conexões assíncronas no Django.
- **Daphne** é um servidor ASGI necessário para rodar o Django Channels.
- **Redis** funciona como um "canal" de mensagens entre processos, facilitando a troca de dados entre os consumidores de WebSocket.

Essas tecnologias permitem que o frontend receba novas mensagens em tempo real, sem a necessidade de atualizações manuais.

## Endpoints

### `/webhook/` [POST]

Este endpoint recebe eventos via Webhook. Ele suporta os seguintes tipos de eventos:

- `NEW_CONVERSATION`: Cria uma nova conversa.
- `NEW_MESSAGE`: Adiciona uma nova mensagem à conversa.
- `CLOSE_CONVERSATION`: Marca uma conversa como encerrada.

### Exemplos de eventos

#### Novo evento de conversa iniciada

```json
{
    "type": "NEW_CONVERSATION",
    "timestamp": "2025-02-21T10:20:41.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

#### Novo evento de mensagem recebida

```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:42.349308",
    "data": {
        "id": "49108c71-4dca-4af3-9f32-61bc745926e2",
        "direction": "RECEIVED",
        "content": "Olá, tudo bem?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

#### Novo evento de mensagem enviada

```json
{
    "type": "NEW_MESSAGE",
    "timestamp": "2025-02-21T10:20:44.349308",
    "data": {
        "id": "16b63b04-60de-4257-b1a1-20a5154abc6d",
        "direction": "SENT",
        "content": "Tudo ótimo e você?",
        "conversation_id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```

#### Novo evento de conversa encerrada

```json
{
    "type": "CLOSE_CONVERSATION",
    "timestamp": "2025-02-21T10:20:45.349308",
    "data": {
        "id": "6a41b347-8d80-4ce9-84ba-7af66f369f6a"
    }
}
```