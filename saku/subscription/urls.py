from django.urls import path
from .views import SubscriptionListView, PurchaseSubscriptionView

app_name = "subscription"
urlpatterns = [
    path("list", SubscriptionListView.as_view(), name="subscription-list"),
    path("purchase", PurchaseSubscriptionView.as_view(), name="purchase-subscription"),
]