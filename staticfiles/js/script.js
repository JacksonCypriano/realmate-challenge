document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form');
    const textarea = form.querySelector('textarea');
    const messageContainer = document.querySelector('.messages');
    const conversationId = window.location.pathname.split('/').filter(Boolean).pop();

    const socket = new WebSocket(`ws://${window.location.host}/ws/messages/${conversationId}/`);

    socket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const message = data.message;

        const newMessage = document.createElement('div');
        newMessage.classList.add('message', 'received');
        newMessage.innerHTML = `<p><strong>Recebida:</strong> ${message}</p>`;
        messageContainer.appendChild(newMessage);
        messageContainer.scrollTop = messageContainer.scrollHeight;
    };

    socket.onopen = function () {
        console.log('Conexão WebSocket aberta');
    };

    socket.onclose = function () {
        console.error('Conexão WebSocket fechada');
    };

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const messageContent = textarea.value.trim();
        if (!messageContent) return;

        const messageId = crypto.randomUUID();

        const payload = {
            type: "NEW_MESSAGE",
            timestamp: new Date().toISOString(),
            data: {
                id: messageId,
                direction: "SENT",
                content: messageContent,
                conversation_id: conversationId
            }
        };

        try {
            const response = await fetch('/webhook/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                const newMessage = document.createElement('div');
                newMessage.classList.add('message', 'sent');
                newMessage.innerHTML = `<p><strong>Enviada:</strong> ${messageContent}</p>`;
                messageContainer.appendChild(newMessage);
                messageContainer.scrollTop = messageContainer.scrollHeight;

                textarea.value = '';
            } else {
                const errorData = await response.json();
                showErrorPopup(errorData.error || 'Erro ao enviar mensagem.');
            }
        } catch (error) {
            console.error('Erro de rede ao enviar mensagem:', error);
        }
    });

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function showErrorPopup(message) {
        const popup = document.getElementById('popup-error');
        popup.textContent = message;
        popup.style.display = 'block';
        popup.style.opacity = '1';

        setTimeout(() => {
            popup.style.opacity = '0';
            setTimeout(() => {
                popup.style.display = 'none';
            }, 500);
        }, 4000);
    }
});
