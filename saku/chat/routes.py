from chat.consumers import ChatConsumer
from django.urls import path

chat_websocket_urlpatterns = [
    path("chat/<str:username>/<str:sender_jwt>", ChatConsumer.as_asgi())
]
