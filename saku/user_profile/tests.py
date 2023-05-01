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
        url = reverse("user_profile:detail-general-profile")
        response = self.client.get(f"{url}/{self.user2.username}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["username"], self.user2.username)

    def test_follow_unfollow_follower_count_info(self):

        url = reverse("user_profile:follow_user")
        response = self.client.post(url, data={"username": self.user2.username})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse("user_profile:detail-general-profile")
        response = self.client.get(f"{url}/{self.user2.username}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["username"], self.user2.username)
        self.assertEqual(response.data["data"]["following_count"], 1)
        self.assertEqual(response.data["data"]["follower_count"], 0)


        url = reverse("user_profile:unfollow_user")
        response = self.client.delete(f"{url}/{self.user2.username}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse("user_profile:detail-general-profile")
        response = self.client.get(f"{url}/{self.user2.username}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["username"], self.user2.username)
        self.assertEqual(response.data["data"]["following_count"], 0)
        self.assertEqual(response.data["data"]["follower_count"], 0)

    def test_follow_unfollow_followed_count(self):
        url = reverse("user_profile:follow_user")
        response = self.clien2.post(url, data={"username": self.user.username})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse("user_profile:detail-general-profile")
        response = self.client.get(f"{url}/{self.user.username}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["username"], self.user.username)
        self.assertEqual(response.data["data"]["following_count"], 0)
        self.assertEqual(response.data["data"]["follower_count"], 1)


        url = reverse("user_profile:unfollow_user")
        response = self.clien2.delete(f"{url}/{self.user.username}")

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        url = reverse("user_profile:detail-general-profile")
        response = self.client.get(f"{url}/{self.user.username}")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["username"], self.user.username)
        self.assertEqual(response.data["data"]["following_count"], 0)
        self.assertEqual(response.data["data"]["follower_count"], 0)   

    def test_duplicate_follow(self):
        url = reverse("user_profile:follow_user")
        response = self.client.post(url, data={"username": self.user2.username})

        url = reverse("user_profile:follow_user")
        response = self.client.post(url, data={"username": self.user2.username})

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_follow_username(self):
        url = reverse("user_profile:follow_user")
        response = self.client.post(url, data={"username": "invalid"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_unfollow_not_followed_username(self):
        url = reverse("user_profile:unfollow_user")
        response = self.client.delete(f"{url}/{self.user2.username}")
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unfollow_invalid_username(self):
        url = reverse("user_profile:unfollow_user")
        response = self.client.delete(f"{url}/invalid")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

