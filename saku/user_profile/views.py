import os

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Profile, FollowRelationship, Ticket
from .serializers import ProfileSerializer, CreateFollowRelationSerializer, PersonalProfileSerializer, TicketSerializer
from django.shortcuts import get_object_or_404


class UpdateProfile(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    def get_object(self):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        user = self.request.user
        email = serializer.data.get("email")
        if email:
            user.email = email
            user.save()
        profile = Profile.objects.filter(user=user)[0]
        old_profile_image = profile.profile_image
        new_profile_image = self.request.data.get("profile_image")
        if new_profile_image and old_profile_image:
            try:
                os.remove(old_profile_image.path)
            except:
                pass
        return profile

    def get_serializer_context(self):
        context = super(UpdateProfile, self).get_serializer_context()
        context.update({"user": self.request.user})
        return context


class DeleteProfilePicture(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        profile = Profile.objects.filter(user=user)[0]
        if profile.profile_image:
            try:
                os.remove(profile.profile_image.path)
            except:
                pass
            profile.profile_image = None
            profile.save()
        return Response(
            {"message": "Profile picture deleted"}, status=status.HTTP_200_OK
        )

class PersonalProfileInfo(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        print(request)
        user = request.user
        profile_info = Profile.objects.filter(user=user)[0]
        # print(len(profile_info))
        # print(profile_info)
        # profile_info = profile_info[0]
        print("A")
        print(type(profile_info))
        print(profile_info)
        # print(profile_info.user.username)
        serializer = PersonalProfileSerializer(data=profile_info)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DetailedGeneralProfileInfo(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        # print(username)
        profile = Profile.objects.filter(user__username=username)
        # print(len(profile))
        if len(profile) == 0:
            response = {
                "status": "error",
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Invalide username.",
                "data": []
            }
            return Response(response, status=response["code"])
        profile = profile[0]
        # TODO: using the following and the serializer does not work. why?
        # serializer = GeneralProfileSerializer(data=profile.user, context={"request": request})
        if profile.profile_image:
            base_url = request.build_absolute_uri("/").strip("/")
            profile_img_url = base_url + "/media/" + f"{profile.profile_image}"
        else:
            profile_img_url = None

        # get number of followers and followings
        followers = FollowRelationship.objects.filter(followed=profile)
        follower_count = followers.count()
        followings = FollowRelationship.objects.filter(follower=profile)
        following_count = followings.count()

        is_followed = True if len(followers.filter(follower__user__username=request.user.username)) > 0 else False
        
        response = {
            "data": {
                "user_id": profile.user.id,
                "username": profile.user.username,
                "name": profile.name,
                "profile_image_url": profile_img_url,
                "following_count": following_count,
                "follower_count": follower_count,
                "is_followed": is_followed
            }
        }
        
        return Response(response, status=status.HTTP_200_OK)
        

class FollowUserProfile(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        followed = get_object_or_404(Profile, user__username=request.data["username"])
        if request.data["username"] == request.user.username:
            return Response({"detail": "Bad request"}, status=status.HTTP_400_BAD_REQUEST)
        follower = Profile.objects.filter(user__id=request.user.id)[0]
        follow_data = {
            "follower": follower.id,
            "followed": followed.id
        }

        if len(FollowRelationship.objects.filter(follower=follower, followed=followed)) > 0:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

        serializer = CreateFollowRelationSerializer(data=follow_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response = {
            "data": {
                "follower_username": follower.user.username,
                "followed_username": followed.user.username
            }
        }
        # print(serializer.data)
        return Response(response, status=status.HTTP_201_CREATED)


class UnfollowUserProfile(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, username):
        followed = get_object_or_404(Profile, user__username=username)
        follower = Profile.objects.filter(user__id=request.user.id)[0]

        follow_relation = get_object_or_404(FollowRelationship, follower=follower, followed=followed)
        follow_relation.delete()

        return Response({}, status=status.HTTP_204_NO_CONTENT)
    

class WalletInfoView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        wallet = Profile.objects.filter(user=request.user)[0].wallet
        response = {
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "wallet": wallet
            }
        }
        return Response(response, status=status.HTTP_200_OK)
    
class ChargeWalletView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        if not "charge_amount" in request.data:
            return Response({
                "message": "Invalid data",
                "detail": {
                    "charge_amount": "This field is required.",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        charge_amount = request.data["charge_amount"]
        if charge_amount < 1:
            return Response({
                "message": "Invalid value",
                "detail": {
                    "charge_amount": "Only greater or equal to 1 values are accepted for this field.",
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        profile = Profile.objects.filter(user=request.user)[0]
        final_charge_value = int(charge_amount)
        profile.wallet += final_charge_value
        profile.save()
        return Response({
            "status": "success",
            "code": status.HTTP_200_OK,
            "data": {
                "charged_amount": final_charge_value,
                "wallet": profile.wallet
            }
        }, status=status.HTTP_200_OK)
    

class GetTicketsList(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        tickets = Ticket.objects.filter(user=request.user)
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class GetTicket(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, ticket_id):
        tickets = Ticket.objects.filter(user=request.user)
        targeted_ticket = get_object_or_404(tickets, id=ticket_id)
        serializer = TicketSerializer(targeted_ticket)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CreateTicket(generics.GenericAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        sent_question = request.data["question"]
        Ticket.objects.create(question=sent_question, user=request.user)
        return Response(status=status.HTTP_201_CREATED)