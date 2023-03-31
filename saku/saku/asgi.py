import os

from auction.routes import auction_websocket_urlpatterns
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from chat.routes import chat_websocket_urlpatterns
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saku.settings")

application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": AuthMiddlewareStack(
            URLRouter(chat_websocket_urlpatterns + auction_websocket_urlpatterns)
        ),
    }
)
