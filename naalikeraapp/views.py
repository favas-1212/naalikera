from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from .serializers import RegisterSerializer, LoginSerializer, VerifyOTPSerializer, ForgotPasswordSerializer
from .models import CustomUser, OTP
import random
import string
from django.utils import timezone
from datetime import timedelta

def index(request):
    return render(request, 'index.html')

def nal(request):
    return render(request, 'nal.html')

def login_view(request):
    return render(request, 'login.html')

def signup_view(request, user_type):
    return render(request, 'signup.html', {'user_type': user_type})

def verify_otp_view(request):
    return render(request, 'verify-otp.html')

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data
    username = data.get('username')
    phone = data.get('phone')

    # Check if phone exists
    existing_user_by_phone = CustomUser.objects.filter(phone=phone).first()
    if existing_user_by_phone:
        if existing_user_by_phone.username == username:
            if not existing_user_by_phone.is_phone_verified:
                # Resend OTP
                otp = '123456'  # Fixed for dev
                print(f"OTP for {phone}: {otp}")  # For dev testing
                OTP.objects.create(phone=phone, otp=otp)
                refresh = RefreshToken.for_user(existing_user_by_phone)
                return Response({
                    'message': 'User exists but phone not verified. OTP sent.',
                    'user': {
                        'id': existing_user_by_phone.id,
                        'username': existing_user_by_phone.username,
                        'email': existing_user_by_phone.email,
                        'user_type': existing_user_by_phone.user_type,
                        'phone': str(existing_user_by_phone.phone),
                        'is_phone_verified': existing_user_by_phone.is_phone_verified,
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    },
                    'otp_sent': True
                }, status=status.HTTP_200_OK)
            else:
                return Response({'phone': ['Phone number already verified. Please login.']}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'phone': ['Phone number already registered with a different username.']}, status=status.HTTP_400_BAD_REQUEST)

    # Check if username exists with different phone
    existing_user_by_username = CustomUser.objects.filter(username=username).first()
    if existing_user_by_username:
        return Response({'username': ['Username already exists.']}, status=status.HTTP_400_BAD_REQUEST)

    # New user
    serializer = RegisterSerializer(data=data)
    if serializer.is_valid():
        user = serializer.save()
        # Generate OTP for phone verification
        otp = '123456'  # Fixed for dev
        print(f"OTP for {user.phone}: {otp}")  # For dev testing
        OTP.objects.create(phone=user.phone, otp=otp)
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'otp_sent': True
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'phone': str(user.phone) if user.phone else None,
                'is_phone_verified': user.is_phone_verified,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        return Response({'message': 'Phone verified successfully', 'user_id': user.id if user else None})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'message': 'Logged out successfully'})
    except:
        return Response({'message': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bypass_verification(request):
    user = request.user
    user.is_phone_verified = True
    user.save()
    return Response({'message': 'Phone verification bypassed for development'})
