from auction.views import (CategoryList, CreateListAuction,
                           DeleteAuctionPicture, DetailedAuction)
from django.urls import path

from auction.views import (
    CreateListAuction,
    CategoryList,
    DetailedAuction,
    DeleteAuctionPicture,
    AuctionScoreDetail
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
]
