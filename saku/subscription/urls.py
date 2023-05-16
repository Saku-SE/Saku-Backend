from django.urls import path
from .views import SubscriptionListView

app_name = "subscription"
urlpatterns = [
    path("list", SubscriptionListView.as_view(), name="subscription-list"),
]