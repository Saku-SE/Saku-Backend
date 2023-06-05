import random

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from user_profile.models import Profile
from google.oauth2 import id_token
from google.auth.transport import requests
from django.http import JsonResponse

from saku.settings import EMAIL_HOST_USER

from .serializers import (ChangePasswordSerializer, ForgotPasswordSerializer,
                          RegisterSerializer)


# send_email is slow!
class Register(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data.get("username")
        email = serializer.data.get("email")
        randomcode = random.randrange(1000, 9999)
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
            # user = User.objects.get(username=serializer.validated_data['username'])
            try:
                # validate_email(user.email)
                profile = Profile.objects.get(email=serializer.validated_data["email"])
                user = profile.user
            except:
                response = {
                    "status": "error",
                    "code": status.HTTP_400_BAD_REQUEST,
                    # 'message': 'There is no valid email for this username.',
                    "message": "There is no registered user for this eamil.",
                    "data": [],
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            new_password = User.objects.make_random_password()
            user.set_password(new_password)
            user.save()
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
    
    
class EasyGoogleLogin(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    def post(self, request):
        # Get the ID token from the request
        id_token = request.POST.get('id_token')
    
         # Verify the ID token with Google
        try:
            #todo Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(id_token, requests.Request(), CLIENT_ID)
        
            # Get user info from the ID token
            email = idinfo['email']
            name = idinfo['name']

            # Check that the ID token is issued by Google
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # Return the user ID
            sub = idinfo['sub']
            profiles = Profile.objects.filter(google_sub=sub)
            if len(profiles) <= 0:
                # create user account
                user = User.objects.create(
                username=validated_data["username"], email=validated_data["email"])
                # create user profile
                Profile.objects.create(user=user, national_id="0", email=user.email)
        
            # Return a JSON response with user info
            return JsonResponse({'email': email, 'name': name})
        except ValueError:
            return JsonResponse({'error': 'Invalid ID token.'})
        
