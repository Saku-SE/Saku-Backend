# from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import User
from django.urls import reverse
from support.maps import support_q_maps
from rest_framework import status

# Create your tests here.

class GeneralAdviceTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username="test_user", password="Ab654321"
        )
        self.user.is_active = True
        self.user.save()
        self.client.force_authenticate(self.user)

        self.general_advice_url = reverse("support:general_advice")

        self.base_request_data = {}
        for i in range(len(support_q_maps)):
            # initially, every question key has choice '1'
            self.base_request_data[f"q{i + 1}"] = 1

    def test_missing_key_bad_request(self):
        data = self.base_request_data
        data.pop(f"q{len(support_q_maps)}")
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_extra_invalid_key_bad_request(self):
        data = {
            **self.base_request_data,
            f"q{len(support_q_maps) + 1}": 1, 
        }
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_key_and_missing_key_bad_request(self):
        data = self.base_request_data
        data.pop(f"q{len(support_q_maps)}")
        data[f"q{len(support_q_maps) + 1}"] = 1
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_choice(self):
        quesion_one_number_of_choices = len(support_q_maps["q1"].keys())
        data = {
            **self.base_request_data,
            "q1": quesion_one_number_of_choices + 1
        }
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_level_zero(self):
        choices = [2, 1, 2, 2, 1, 1, 1, 1, 4, 2]
        data = {}
        for i in range(len(choices)):
            data[f"q{i + 1}"] = choices[i]
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["level"], 0)


    def test_level_one(self):
        data = {
            **self.base_request_data,
            "q2": 3
        }
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["level"], 1)

    def test_level_two(self):
        choices = [1, 3, 1, 1, 3, 2, 2, 2, 1, 2]
        data = {}
        for i in range(len(choices)):
            data[f"q{i + 1}"] = choices[i]
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["level"], 2)

    def test_level_three(self):
        choices = [1, 3, 1, 1, 3, 2, 2, 2, 1, 1]
        data = {}
        for i in range(len(choices)):
            data[f"q{i + 1}"] = choices[i]
        response = self.client.post(path=self.general_advice_url, data=data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["level"], 3)
