from django.shortcuts import render

# Create your views here.
import pyotp
import json
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from whatsapp.views import send_whatsapp_message



User = get_user_model()

import random

# Simulated OTP storage
otp_store = {}

class RequestOTPView(APIView):
    def post(self, request):
        whatsapp_number = request.data.get("whatsapp_number")

        try:
            user = User.objects.get(username=whatsapp_number)
        except ObjectDoesNotExist:
            return Response({"error": "User not found. Please register first."}, status=status.HTTP_404_NOT_FOUND)

        # Generate a 6-digit OTP
        otp = str(random.randint(100000, 999999))
        otp_store[whatsapp_number] = otp  # Store OTP temporarily

        # Simulate sending the OTP via WhatsApp (Replace this with actual WhatsApp API)
        print(f"Sending OTP {otp} to {whatsapp_number}")
        send_whatsapp_message(whatsapp_number, f"Your OTP is: {otp}", "text")


        return Response({"message": "OTP sent successfully!"}, status=status.HTTP_200_OK)


from rest_framework_simplejwt.tokens import RefreshToken

class VerifyOTPView(APIView):
    def post(self, request):
        whatsapp_number = request.data.get("whatsapp_number")
        otp = request.data.get("otp")

        # Check if OTP is correct
        if otp_store.get(whatsapp_number) == otp:
            user = User.objects.get(username=whatsapp_number)

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            # Remove OTP after successful login
            del otp_store[whatsapp_number]

            return Response({
                "access": access_token,
                "refresh": str(refresh)
            }, status=status.HTTP_200_OK)

        return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)


from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

class RegisterUserView(APIView):
    def post(self, request):
        whatsapp_number = request.data.get("whatsapp_number")
        name = request.data.get("name")
        password = request.data.get("password")

        if not whatsapp_number or not password:
            return Response({"error": "WhatsApp number and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user exists
        if User.objects.filter(username=whatsapp_number).exists():
            return Response({"error": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new user
        user = User.objects.create_user(username=whatsapp_number, password=password, first_name=name)
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
