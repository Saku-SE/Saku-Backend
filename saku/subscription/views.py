from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Subscription
from user_profile.models import Profile
from .serializers import SubscriptionSerializer
from django.shortcuts import get_object_or_404
import datetime

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
        })

