import json

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase

from .models import Profile


class ProfileTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user", password="Ab654321", email="email@email.com"
        )
        self.user2 = User.objects.create_user(
            username="test_user2", password="Ab654321", email="email2@email.com"
        )
        self.user.is_active = True
        self.user.save()
        self.profile = Profile.objects.create(user=self.user, email=self.user.email)
        self.client.force_authenticate(self.user)

        self.user2.is_active = True
        self.user2.save()
        self.profile2 = Profile.objects.create(user=self.user2, email=self.user2.email)
        self.client2 = APIClient()
        self.client2.force_authenticate(self.user2)


    def test_update_profile_success(self):
        url = reverse("user_profile:update_profile")

        data1 = {"name": "Ali", "phone": "09123456789", "email": "email@email.com"}
        response = self.client.put(url, data1, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_profile_failure_phone(self):
        url = reverse("user_profile:update_profile")

        data2 = {"phone": "090", "email": "email@email.com"}
        response = self.client.put(url, data2, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            ErrorDetail(
                string="Phone number is invalid (.eg '09123456789')", code="invalid"
            ),
            response.data["phone"],
        )

    def test_update_profile_failure_email(self):
        url = reverse("user_profile:update_profile")
        data3 = {"email": "email.com"}
        response = self.client.put(url, data3, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            ErrorDetail(string="Enter a valid email address.", code="invalid"),
            response.data["email"],
        )

    def test_update_picture_failure(self):
        url = reverse("user_profile:update_profile")
        data1 = {"profile_image": "1.jpg"}
        response = self.client.put(url, data1, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            ErrorDetail(
                string="The submitted data was not a file. Check the encoding type on the form.",
                code="invalid",
            ),
            response.data["profile_image"],
        )

    def test_delete_picture_success(self):
        url = reverse("user_profile:delete_profile_image")
        response = self.client.post(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse("user_profile:update_profile")
        response = self.client.get(url, format="json")
        self.assertEqual(response.data["profile_image"], None)

    def test_detail_general_profile_info(self):
        url = f"/profile/general/{self.user2.username}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["user_id"], self.user2.id)
        self.assertEqual(response.data["data"]["username"], self.user2.username)

    def test_follow_unfollow_is_followed_field(self):
        
        url = "/profile/follow/"
        response = self.client.post(url, data={"username": self.user2.username})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = f"/profile/general/{self.user2.username}"
        response = self.client.get(f"{url}")        

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["user_id"], self.user2.id)
        self.assertEqual(response.data["data"]["username"], self.user2.username)
        self.assertEqual(response.data["data"]["following_count"], 0)
        self.assertEqual(response.data["data"]["follower_count"], 1)
        self.assertEqual(response.data["data"]["is_followed"], True)


    def test_follow_unfollow_follower_count_info(self):

        url = "/profile/follow/"
        response = self.client.post(url, data={"username": self.user2.username})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = f"/profile/general/{self.user.username}"
        response = self.client.get(f"{url}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["user_id"], self.user.id)
        self.assertEqual(response.data["data"]["username"], self.user.username)
        self.assertEqual(response.data["data"]["following_count"], 1)
        self.assertEqual(response.data["data"]["follower_count"], 0)


        url = f"/profile/unfollow/{self.user2.username}"
        response = self.client.delete(f"{url}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = f"/profile/general/{self.user.username}"
        response = self.client.get(f"{url}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["user_id"], self.user.id)
        self.assertEqual(response.data["data"]["username"], self.user.username)
        self.assertEqual(response.data["data"]["following_count"], 0)
        self.assertEqual(response.data["data"]["follower_count"], 0)

    def test_follow_unfollow_followed_count(self):
        url = "/profile/follow/"
        response = self.client2.post(url, data={"username": self.user.username})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = f"/profile/general/{self.user.username}"
        response = self.client.get(f"{url}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["user_id"], self.user.id)
        self.assertEqual(response.data["data"]["username"], self.user.username)
        self.assertEqual(response.data["data"]["following_count"], 0)
        self.assertEqual(response.data["data"]["follower_count"], 1)


        url = f"/profile/unfollow/{self.user.username}"
        response = self.client2.delete(f"{url}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = f"/profile/general/{self.user.username}"
        response = self.client.get(f"{url}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["user_id"], self.user.id)
        self.assertEqual(response.data["data"]["username"], self.user.username)
        self.assertEqual(response.data["data"]["following_count"], 0)
        self.assertEqual(response.data["data"]["follower_count"], 0)   

    def test_duplicate_follow(self):
        url = "/profile/follow/"
        response = self.client.post(url, data={"username": self.user2.username})

        url = "/profile/follow/"
        response = self.client.post(url, data={"username": self.user2.username})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_follow_username(self):
        url = "/profile/follow/"
        response = self.client.post(url, data={"username": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unfollow_not_followed_username(self):
        url = f"/profile/unfollow/{self.user2.username}"
        response = self.client.delete(f"{url}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow_invalid_username(self):
        url = f"/profile/unfollow/invalid"
        response = self.client.delete(f"{url}")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_same_follow_username(self):
        url = f"/profile/follow/"
        response = self.client.post(url, data={"username": self.user.username})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_wallet(self):
        url = reverse("user_profile:wallet-info")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["wallet"], 0)

    def test_charge_wallet_success(self):
        url = reverse("user_profile:charge-wallet")
        response = self.client.post(url, data={"charge_amount": 10})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["wallet"], 10)
        self.assertEqual(response.data["data"]["charged_amount"], 10)

    def test_charge_wallet_success_decimal_value(self):
        url = reverse("user_profile:charge-wallet")
        response = self.client.post(url, data={"charge_amount": 10.5})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["wallet"], 10)
        self.assertEqual(response.data["data"]["charged_amount"], 10)
    
    def test_charge_wallet_success_invalid_post_data_missing_key(self):
        url = reverse("user_profile:charge-wallet")
        response = self.client.post(url, data={"invalid_key": ""})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["data"], {
                "message": "Invalid data",
                "detail": {
                    "charge_amount": "This field is required.",
                }})
    
    def test_charge_wallet_invalid_value_lt_1(self):
        url = reverse("user_profile:charge-wallet")
        response = self.client.post(url, data={"charge_amount": 0.5})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["data"], {
            "message": "Invalid value",
            "detail": {
                "charge_amount": "Only greater or equal to 1 values are accepted for this field.",
            }
        })
