import datetime
import time


from auction.models import Auction, Category, Tags, Score, City
from bid.models import Bid
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ErrorDetail
from rest_framework.test import APIClient, APITestCase
from auction.serializers import CitySerializer


# Create your tests here.
class CreateAuctionTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(id=1, username="Mehdi")
        self.user2 = User.objects.create(id=2, username="Mehdi2")
        self.client.force_authenticate(self.user)
        Category.objects.create(name="C1")
        self.request_data = {
            "created_at": "2019-08-24T14:15:22Z",
            "name": "string",
            "finished_at": "2019-08-24T14:15:22Z",
            "mode": 1,
            "limit": 0,
            "is_private": True,
            "user": 0,
            "category": "C1",
            "tags": "T1,T2",
        }

    def test_not_found_user(self):
        response = self.client.post(
            path="/auction/", data=self.request_data, format="json"
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertIn(
            ErrorDetail(
                string='Invalid pk "0" - object does not exist.', code="does_not_exist"
            ),
            response.data["user"],
        )

    def test_with_equal_dates(self):
        self.request_data["user"] = 1
        response = self.client.post(
            path="/auction/", data=self.request_data, format="json"
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(1, len(response.data))
        self.assertIn(
            ErrorDetail(
                string="created_at can't be greater or equal to finished_at",
                code="invalid",
            ),
            response.data["non_field_errors"],
        )

    def test_create_valid_auction(self):
        auctions_count = Auction.objects.count()
        self.request_data["user"] = 1
        self.request_data["finished_at"] = "2020-08-24T14:15:22Z"
        response = self.client.post(
            path="/auction/", data=self.request_data, format="json"
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(auctions_count + 1, Auction.objects.count())

    def test_get_category_list(self):
        response = self.client.get(path="/auction/categories/")
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data[0]))

    def test_auction_best_bid(self):
        category = Category.objects.create(name="Category")
        tags = [Tags.objects.create(name="T1"), Tags.objects.create(name="T2")]
        auction = Auction.objects.create(
            **{"id": 5,
                "created_at": "2019-08-24T14:15:22Z",
               "name": "auction1",
               "finished_at": datetime.datetime.now() + datetime.timedelta(0, 10),
               "mode": 1,
               "limit": 0,
               "is_private": False,
               "user": self.user,
               "token": "qwertyui",
               "category": category,
               }
        )
        auction.tags.set(tags)
        Bid.objects.create(
            user=self.user2,
            price=500,
            auction=auction,
            time="2022-07-24T14:15:22Z",
        )
        time.sleep(40)
        response = self.client.get(path="/auction/qwertyui")
        self.assertEqual(500, response.data["best_bid"]["price"])


class GetAuctionTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(id=1, username="Mehdi")
        self.client.force_authenticate(self.user)
        category = Category.objects.create(name="Category")
        tags = [Tags.objects.create(name="T1"), Tags.objects.create(name="T2")]
        Auction.objects.create(
            **{
                "created_at": "2019-08-24T14:15:22Z",
                "name": "auction1",
                "finished_at": "2019-08-24T14:15:22Z",
                "mode": 1,
                "limit": 0,
                "is_private": False,
                "user": self.user,
                "token": "qwertyui",
                "category": category,
            }
        ).tags.set(tags)
        Auction.objects.create(
            **{
                "created_at": "2020-08-24T14:15:22Z",
                "name": "auction2",
                "finished_at": "2024-08-24T14:15:22Z",
                "mode": 1,
                "limit": 0,
                "is_private": False,
                "user": self.user,
                "token": "asdfghjk",
                "category": category,
            }
        ).tags.set(tags)

    def test_get_auction_list(self):
        response = self.client.get(path="/auction/")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))
        self.assertEqual("auction2", response.data[0]["name"])

    def test_get_auction_list_by_name(self):
        response = self.client.get(path="/auction/?name=auc")
        self.assertEqual(200, response.status_code)
        self.assertEqual(2, len(response.data))

    def test_get_auction_list_by_finished(self):
        response = self.client.get(path="/auction/?finished=false")
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.data))

    def test_get_auction_list_by_limit(self):
        response = self.client.get(path="/auction/?limit=500")
        self.assertEqual(200, response.status_code)
        self.assertEqual(0, len(response.data))

    def test_get_detailed_auction(self):
        response = self.client.get(path="/auction/qwertyui")
        self.assertEqual(200, response.status_code)
        auction = Auction.objects.get(token="qwertyui")
        self.assertEqual(auction.name, response.data["name"])

    def test_not_found_auction(self):
        response = self.client.get(path="/auction/notfound")
        self.assertEqual(404, response.status_code)
        self.assertIn(
            ErrorDetail(string="Not found.", code="not_found"), response.data["detail"]
        )


class EditAuctionTest(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create(id=1, username="Mehdi")
        self.client.force_authenticate(self.user)
        category = Category.objects.create(name="Category")
        tags = [Tags.objects.create(name="T1"), Tags.objects.create(name="T2")]
        Auction.objects.create(
            **{
                "created_at": "2019-08-24T14:15:22Z",
                "name": "auction1",
                "finished_at": "2019-08-24T14:15:22Z",
                "mode": 1,
                "limit": 0,
                "is_private": False,
                "user": self.user,
                "token": "qwertyui",
                "category": category,
            }
        ).tags.set(tags)

    def test_edit_auction(self):
        data = {"name": "string", "finished_at": "2020-08-24T14:15:22Z"}
        response = self.client.put(path="/auction/qwertyui", data=data)
        self.assertEqual(200, response.status_code)
        auction = Auction.objects.get(token="qwertyui")
        self.assertEqual(auction.name, response.data["name"])

    def test_edit_auction_failure(self):
        data = {"finished_at": "2018-08-24T14:15:22Z"}
        response = self.client.put(path="/auction/qwertyui", data=data)
        self.assertEqual(400, response.status_code)
        self.assertIn(
            ErrorDetail(
                string="created_at can't be greater or equal to finished_at",
                code="invalid",
            ),
            response.data["non_field_errors"],
        )

    def test_update_image_failure(self):
        data1 = {"auction_image": "1.jpg"}
        response = self.client.put(path="/auction/qwertyui", data=data1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(
            ErrorDetail(
                string="The submitted data was not a file. Check the encoding type on the form.",
                code="invalid",
            ),
            response.data["auction_image"],
        )

    def test_delete_image_success(self):
        response = self.client.post(path="/auction/remove-picture/qwertyui")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.get(path="/auction/qwertyui")
        self.assertEqual(response.data["auction_image"], None)
        

class ScoreTest(APITestCase): 
    def setUp(self) -> None:
        self.category = Category.objects.create(name="Category")
        self.tags = [Tags.objects.create(name="T1"), Tags.objects.create(name="T2")]
        # create a user
        self.user = User.objects.create(id=1, username="Emad")
        # create an auction
        self.auction = Auction.objects.create(
            **{"id": 5,
                "created_at": "2019-08-24T14:15:22Z",
               "name": "auction1",
               "finished_at": datetime.datetime.now() + datetime.timedelta(0, 10),
               "mode": 1,
               "limit": 0,
               "is_private": False,
               "user": self.user,
               "token": "qwertyui",
               "category": self.category,
               }
        )
        # authenticate the user
        self.client.force_authenticate(user=self.user)
        
        
        # create a user
        self.scored_user = User.objects.create(id=2, username="Emad2")
        self.score = Score.objects.create(user= self.scored_user, auction= self.auction, 
                                          q1= 1, q2= 2, q3= 3, q4= 4, q5= 5)
    
    
    def test_create_score(self):
        # make a post request to create a score for the auction
        dataTest = {
            'q1': 2, 
            'q2': 3, 
            'q3': 2,
            'q4': 1,
            'q5': 2
        }
        response = self.client.post(path=f"/auction/score/{self.auction.token}", data= dataTest)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        
    def test_create_score_invalid_data(self):
        # make a post request to create a score for the auction with invalid data
        dataTest = {
            'q1': 6, 
            'q2': 3, 
            'q3': 2,
            'q4': -1,
            'q5': 2
        }
        response = self.client.post(path=f"/auction/score/{self.auction.token}", data= dataTest)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    
    def test_get_auction_score_detail(self):
        response = self.client.get(path=f"/auction/score/{self.auction.token}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_response_data = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "mean_score": 15.0/5.0,
                "number_of_scores": 1,
            }
        }
        self.assertEqual(response.data, expected_response_data)
        
        
    def test_get_auction_score_detail_false_auctionToken(self):
        response = self.client.get(path=f"/auction/score/faToken")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        

class CityListViewTestCase(APITestCase):
    def setUp(self):
        self.city1 = City.objects.create(name='Unkown')
        self.city1 = City.objects.create(name='New York')
        self.city2 = City.objects.create(name='Los Angeles')
        self.city3 = City.objects.create(name='Chicago')
        self.city4 = City.objects.create(name='Houston')
        # create a user
        self.user = User.objects.create(id=1, username="Emad")
        # authenticate the user
        self.client.force_authenticate(user=self.user)

    def test_list_cities(self):
        url = reverse('get_city_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        self.assertEqual(response.data, serializer.data)
