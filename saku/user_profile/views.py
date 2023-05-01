import os

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Profile
from .serializers import ProfileSerializer, GeneralProfileSerializer, CreateFollowRelationSerializer
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

class DetailedGeneralProfileInfo(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, username):
        profile = Profile.objects.filter(user__username=username)
        if len(profile) == 0:
            response = {
                "status": "error",
                "code": status.HTTP_404_NOT_FOUND,
                "message": "Invalide username.",
                "data": []
            }
            return Response(response, status=response["code"])
        profile = profile[0]
        serializer = GeneralProfileSerializer(data=profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FollowUserProfile(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        followed = get_object_or_404(Profile, user__username=request.data["username"])
        follower = Profile.objects.filter(user__id=request.user.id)[0]
        follow_data = {
            "follower": follower.id,
            "followed": followed.id
        }
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


