from django.urls import path
from .views import SubscriptionListView, PurchaseSubscriptionView, UserActiveSubscriptionInfoView

app_name = "subscription"
urlpatterns = [
    path("list", SubscriptionListView.as_view(), name="subscription-list"),
    path("purchase", PurchaseSubscriptionView.as_view(), name="purchase-subscription"),
    path("active", UserActiveSubscriptionInfoView.as_view(), name="user-active-subscription")
]