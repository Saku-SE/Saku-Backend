from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from auction.models import Auction
from bid.models import Bid
from .functions import *


class HomepageView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, year):
        user = request.user
        all_auctions = Auction.objects.all()
        all_user_auctions = all_auctions.filter(user=user)

        all_bids = Bid.objects.all()
        all_user_bids = all_bids.filter(user=user)

        response = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "income": get_income(user),
                "seccussfull_auction_count": get_seccussfull_auction_count(user, all_auctions),
                "auctions_participants_num": get_auctions_participants_num(
                    all_user_auctions
                ),
                "auctions_count": get_auctions_count(all_user_auctions),
                "last_auctions_participated": get_last_auctions_participated(
                    user, all_user_bids
                ),
                "last_auctions_created": get_last_auctions_created(all_user_auctions),
                "income_list": get_income_list(user, all_auctions),
                "your_colaberation_list": get_your_colaberation_list(
                    all_user_bids, all_user_auctions
                ),
                "your_colaberation_count": get_your_colaberation_count(
                    all_user_bids, all_user_auctions
                ),
                "others_colaberation_list": get_others_colaberation_list(user, all_bids),
                "others_colaberation_count": get_others_colaberation_count(user, all_bids),
                "expense_list": get_expense_list(all_user_bids, all_auctions),
                "expense": get_expense(user, all_user_bids, all_auctions),
                "auction1_participate_count": get_auction_participate_count(user, all_bids, 1),
                "auction1_create_count": get_auction_create_count(user, all_auctions, 1),
                "auction2_participate_count": get_auction_participate_count(user, all_bids, 2),
                "auction2_create_count": get_auction_create_count(user, all_auctions, 2),
                # 'last_chats' : get_last_chats(user),
                "yearly_income_list": get_yearly_income_list(user, year, all_auctions),
                "yearly_expense_list": get_yearly_expense_list(
                    year, all_user_bids, all_auctions
                ),
            },
        }
        return Response(response, status=status.HTTP_200_OK)
