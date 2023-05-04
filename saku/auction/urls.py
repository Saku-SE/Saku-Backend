
from django.urls import path

from auction.views import (
    CreateListAuction,
    CategoryList,
    DetailedAuction,
    DeleteAuctionPicture,
    AuctionScoreDetail,
    CityList,
    AuctionsByCityView,
)

urlpatterns = [
    path("", CreateListAuction.as_view(), name="auction"),
    path("categories/", CategoryList.as_view()),
    path("<str:token>", DetailedAuction.as_view(), name="detailed_auction"),
    path(
        "remove-picture/<str:token>",
        DeleteAuctionPicture.as_view(),
        name="delete_auction_picture",
    ),
    path("score/<str:token>", AuctionScoreDetail.as_view(), name="detailed_score_auction"),
    path("city/", CityList.as_view(), name="get_city_list"),
    path('city/<str:city_id>/', AuctionsByCityView.as_view(), name='auctions_by_city'),
    
]
