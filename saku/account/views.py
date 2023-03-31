import random

from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from saku.user_profile.models import Profile


from saku.account.serializers import (ChangePasswordSerializer, ForgotPasswordSerializer,
                          RegisterSerializer)


class Register(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get("username")
        email = serializer.data.get("email")
        randomcode = random.randrange(1000, 9999)
# send_email is slow!

        # send_mail(
        #     "Verify Email",
        #     f"Hi {username}!\nYour verification code is: {randomcode}",
        #     EMAIL_HOST_USER,
        #     recipient_list=[email],
        #     fail_silently=False,
        # )
        return Response({"code": randomcode}, status=status.HTTP_200_OK)


class CompeleteRegisteration(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.is_active = True
        user.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChangePassword(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.data.get("new_password"))
            user.save()
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Password updated successfully",
                "data": [],
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForgotPassword(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                profile = Profile.objects.get(email=serializer.validated_data["email"])
                user = profile.user
            except:
                response = {
                    "status": "error",
                    "code": status.HTTP_400_BAD_REQUEST,
                    "message": "There is no registered user for this eamil.",
                    "data": [],
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
# send_email is slow!

            # send_mail(
            #     "New Password",
            #     f"Hi {user.username}!\nYour new password is: {new_password}",
            #     EMAIL_HOST_USER,
            #     recipient_list=[user.email],
            #     fail_silently=False,
            # )
            response = {
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "New password was sent to your email.",
                "data": [],
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
