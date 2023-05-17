from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Subscription
from user_profile.models import Profile
from .serializers import SubscriptionSerializer
from django.shortcuts import get_object_or_404
import datetime
from django.db import transaction

class SubscriptionListView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer

class PurchaseSubscriptionView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        if not profile.subscription is None:
            return Response({
                "message": "Invalid purchase",
                "detail": "You have an already active purchase."
            }, status=status.HTTP_400_BAD_REQUEST)
        subscription = get_object_or_404(Subscription, id=request.data['id'])
        if profile.wallet < subscription.price:
            return Response({
                "message": "Insufficient funds",
                "detail": "You don't have enough credit in your wallet"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            profile.wallet -= subscription.price
            profile.subscription = subscription
            profile.subscription_date = datetime.datetime.now()
            profile.save()
        return Response({
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "type": subscription.name,
                "usage_limit": subscription.usage_limit,
                "left_time_in_days": 30, 
            }
        }, status=status.HTTP_200_OK)
    
class UserActiveSubscriptionInfoView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profile = Profile.objects.get(user=request.user)
        active_subscription = profile.subscription
        if active_subscription is None:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        return Response({
            "id": active_subscription.id,
            "name": active_subscription.name,
            "usage_limit": active_subscription.usage_limit,
            "left_time_in_days": 30 - (datetime.datetime.now() - profile.subscription_date).day
        }, status=status.HTTP_200_OK)

