from comment.views import ListCreateComments, ReplyCommentView
from django.urls import path

app_name = "comment"
urlpatterns = [
    path("<str:token>", ListCreateComments.as_view(), name="list_create_comment"),
    path("reply/<int:pk>", ReplyCommentView.as_view(), name="reply_comment"),
]
