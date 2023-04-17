from auction.consumers import AuctionConsumer
from django.urls import path

auction_websocket_urlpatterns = [
    path("auction/<str:token>/<str:sender_jwt>", AuctionConsumer.as_asgi())
]
