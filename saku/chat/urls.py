from chat.views import GetChat, GetMessage
from django.urls import path

urlpatterns = [
    path("my/", GetChat.as_view()),
    path("messages/<str:username>/", GetMessage.as_view()),
]
