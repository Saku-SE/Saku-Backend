import os
from datetime import datetime

from auction.filters import AuctionListFilter
from auction.models import Auction, Category, Tags, City
from auction.serializers import (CreateAuctionRequestSerializer,
                                 GetAuctionRequestSerializer,
                                 GetCategoriesSerializer,
                                 UpdateAuctionRequestSerializer,
                                 CitySerializer)
from django_filters import rest_framework as filters
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status

from auction.serializers import (
    CreateAuctionRequestSerializer,
    GetAuctionRequestSerializer,
    UpdateAuctionRequestSerializer,
    GetCategoriesSerializer,
    CreateScoreSreializer
)
from rest_framework.response import Response
from saku.serializers import (
    GeneralCreateResponseSerializer,
    GeneralErrorResponseSerializer,
)
from rest_framework.permissions import IsAuthenticated
from auction.models import Auction, Category, Tags, Score
from datetime import datetime
from django_filters import rest_framework as filters
from django.db.models import Q
from auction.filters import AuctionListFilter
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from saku.serializers import (GeneralCreateResponseSerializer,
                              GeneralErrorResponseSerializer)



class CreateListAuction(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Auction.objects.order_by("finished_at")

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = AuctionListFilter

    @swagger_auto_schema(
        responses={
            201: GeneralCreateResponseSerializer,
            400: GeneralErrorResponseSerializer,
        },
    )
    def post(self, request, *args, **kwargs):
        tag_names = request.data.get("tags")
        tags = []
        if tag_names:
            try:
                splited_tags = [x.strip() for x in tag_names.split(',')]
            except:
                splited_tags = tags
            for tag in splited_tags:
                tag_instance, _ = Tags.objects.get_or_create(name=tag)
                tags.append(tag_instance)
        request.data["tags"] = tags
        return super().post(request, *args, **kwargs)

    def get_queryset(self):
        auctions = Auction.objects.order_by("-created_at")
        return auctions

    @swagger_auto_schema(
        responses={
            201: GeneralCreateResponseSerializer,
            400: GeneralErrorResponseSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        auctions = self.get_queryset()
        auctions = self.filter_queryset(auctions)
        serializer = GetAuctionRequestSerializer(
            auctions, many=True, context={"request": request}
        )
        return Response(serializer.data, status=200)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetAuctionRequestSerializer
        return CreateAuctionRequestSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code != 201:
            return super().finalize_response(request, response, args, kwargs)
        response = GeneralCreateResponseSerializer(
            data={"status_code": 201, "message": "Created!", "token": Auction.objects.get(id=response.data["id"]).token}
        )
        if response.is_valid():
            return super().finalize_response(
                request, Response(response.data, status=201), args, kwargs
            )


class DetailedAuction(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Auction.objects.all()
    lookup_field = "token"

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        tag_names = request.data.get("tags")
        tags = []
        if tag_names:
            splited_tags = [x.strip() for x in tag_names.split(',')]
            for tag in splited_tags:
                tag_instance, _ = Tags.objects.get_or_create(name=tag)
                tags.append(tag_instance)
            request.data["tags"] = tags

        instance = self.get_object()
        old_image = instance.auction_image
        new_image = self.request.data.get("auction_image")

        serializer_save_data = request.data.copy()
        if new_image and old_image:
            try:
                os.remove(old_image.path)
            except:
                pass
        elif not new_image:
            if 'auction_image' in serializer_save_data.keys():
                serializer_save_data.pop('auction_image')

    
        serializer = self.get_serializer(instance, data=serializer_save_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GetAuctionRequestSerializer
        return UpdateAuctionRequestSerializer

    def get_serializer_context(self):
        return {"token": self.kwargs["token"]}


class DeleteAuctionPicture(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Auction.objects.all()
    lookup_field = "token"

    def post(self, request, token):
        instance = self.get_object()
        instance.auction_image.delete(save=False)
        # instance.auction_image = None
        instance.save()
        return Response(
            {"message": "Auction picture deleted"}, status=status.HTTP_200_OK
        )


class CategoryList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = GetCategoriesSerializer
    queryset = Category.objects.all()
    
class AuctionScoreDetail(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, token):
        allScores = Score.objects.all()
        auctionScores = allScores.filter(auction__token = token)
        
        if(len(auctionScores) == 0):
            return Response({"message" : "Auction with given token not found."}, status=status.HTTP_404_NOT_FOUND) 
        
        meanList = []
        for auctionScore in auctionScores:
            sum_score = auctionScore.q1 + auctionScore.q2 + auctionScore.q3 + auctionScore.q4 + auctionScore.q5
            mean = sum_score / 5.0
            meanList.append(mean)
            
        score_count  = len(meanList)
        if score_count != 0:
            result = sum(meanList)/score_count
        else:
            result = 0
        
        response = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "mean_score": result,
                "number_of_scores": score_count,
            }
        }
        return Response(response, status=status.HTTP_200_OK)
    
    
    def post(self, request, token):
        auction = get_object_or_404(Auction, token=token)
        requested_data = request.data.copy()
        requested_data["user"] = request.user.id
        requested_data["auction"] = auction.id
        serializer = CreateScoreSreializer(data=requested_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

class CityList(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        cities = City.objects.all()
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AuctionsByCityView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, city_id):
        city_retrieved = get_object_or_404(City, Q(id=city_id))
        auctions = Auction.objects.filter(city=city_retrieved.id)
        response_data = []
        for obj in auctions:
            response_data.append({
                'id': obj.id,
                'name': obj.name,
            })
        response = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "auctions": response_data
            }
        }
        return Response(response, status=status.HTTP_200_OK)
                
class RecentAuctionsView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, limit):
        recent_auctions = Auction.objects.order_by('-created_at')
        if len(recent_auctions) > limit:
            recent_auctions = recent_auctions[:limit]
        serializer = GetAuctionRequestSerializer(
            recent_auctions, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
        
