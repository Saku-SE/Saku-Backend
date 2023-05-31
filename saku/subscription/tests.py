import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from .models import Subscription
from user_profile.models import Profile


class SubscriptionTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user", password="Ab654321", email="email@email.com"
        )
        self.user.is_active = True
        self.user.save()
        self.subscription1 = Subscription.objects.create(
            name="name1", description="description1", usage_limit=10, price=15
        )
        self.subscription2 = Subscription.objects.create(
            name="name2", description="description2", usage_limit=15, price=40
        )
        self.profile = Profile.objects.create(user=self.user, email=self.user.email, wallet=30)
        self.client.force_authenticate(self.user)
    
    def test_subscription_list_view(self):
        url = reverse("subscription:subscription-list")

        response = self.client.get(url, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 2)
    
    def test_purchase_subscription_success(self):
        url = reverse("subscription:purchase-subscription")
        data = {"id": self.subscription1.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["data"]["type"], self.subscription1.name)
    
    def test_purchase_subscription_invalid_purchase_already_active(self):
        url = reverse("subscription:purchase-subscription")
        data = {"id": self.subscription1.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["data"]["type"], self.subscription1.name)

        response = self.client.post(url, data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data["message"], "Invalid purchase")
    
    def test_purchase_subscription_insufficient_funds(self):
        url = reverse("subscription:purchase-subscription")
        data = {"id": self.subscription2.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        self.assertEqual(response.data["message"], "Insufficient funds")
    
    def test_user_active_subscription_empty(self):
        url = reverse("subscription:user-active-subscription")
        
        response = self.client.get(url, format="json")
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        
    def test_user_active_subscription_not_empty(self):
        url = reverse("subscription:purchase-subscription")
        data = {"id": self.subscription1.id}

        response = self.client.post(url, data, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["data"]["type"], self.subscription1.name)

        url = reverse("subscription:user-active-subscription")

        response = self.client.get(url, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data["id"], self.subscription1.id)
        self.assertEqual(response.data["name"], self.subscription1.name)
        self.assertEqual(response.data["left_time_in_days"], 30)



        
