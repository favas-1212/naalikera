from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    VerifyOTPSerializer,
    ForgotPasswordSerializer,
    LoginOTPConfirmSerializer,
)
from .models import CustomUser, OTP
import random
import string


def generate_otp_code(length: int = 6) -> str:
    return ''.join(random.choices(string.digits, k=length))


def generate_session_token(length: int = 48) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(random.choices(alphabet, k=length))

def index(request):
    return render(request, 'index.html')

def nal(request):
    return render(request, 'nal.html')

def hire_now(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # If logged in, perhaps redirect to a hire page, but for now, back to nal
    return redirect('nal')

def find_workers(request):
    if not request.user.is_authenticated:
        return redirect('login')
    # If logged in, perhaps redirect to find workers page, but for now, back to nal
    return redirect('nal')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_phone_verified:
                return render(request, 'login.html', {'error': 'Please verify your phone number first'})
            login(request, user)
            return redirect('nal')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')

def signup_view(request, user_type):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        location = request.POST.get('location')
        district = request.POST.get('district')
        address = request.POST.get('address')

        if not password:
            return render(request, 'register.html', {
                'user_type': user_type,
                'error': 'Password is required',
                'username': username,
                'email': email,
                'phone': phone,
                'location': location,
                'district': district,
                'address': address
            })

        if not phone:
            return render(request, 'register.html', {
                'user_type': user_type,
                'error': 'Phone number is required',
                'username': username,
                'email': email,
                'phone': phone,
                'location': location,
                'district': district,
                'address': address
            })
        
        # Check if phone exists
        if CustomUser.objects.filter(phone=phone).exists():
            return render(request, 'register.html', {
                'user_type': user_type, 
                'error': 'Phone number already registered',
                'username': username,
                'email': email,
                'phone': phone,
                'location': location,
                'district': district,
                'address': address
            })
        
        # Check if username exists
        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'register.html', {
                'user_type': user_type, 
                'error': 'Username already exists',
                'username': username,
                'email': email,
                'phone': phone,
                'location': location,
                'district': district,
                'address': address
            })
        
        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            phone=phone,
            user_type=user_type,
            password=password
        )
        

        # Send OTP
        if settings.DEBUG:
            otp = '123456'
        else:
            otp = generate_otp_code()
        OTP.objects.create(user=user, phone=phone, otp=otp, purpose=OTP.PURPOSE_REGISTRATION)
        print(f"OTP for {phone}: {otp}")  # For dev testing
        
        # Store user id in session for verification
        request.session['user_id'] = user.id
        
        return redirect('verify_otp')
    
    return render(request, 'register.html', {'user_type': user_type})

def verify_otp_view(request):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        user_id = request.session.get('user_id')
        if not otp:
            return render(request, 'verify-otp.html', {'error': 'OTP is required', 'debug': settings.DEBUG})
        if not user_id:
            return render(request, 'verify-otp.html', {'error': 'Session expired', 'debug': settings.DEBUG})
        
        user = CustomUser.objects.filter(id=user_id).first()
        if not user:
            return render(request, 'verify-otp.html', {'error': 'User not found', 'debug': settings.DEBUG})
        
        # Check OTP
        otp_obj = OTP.objects.filter(
            user=user,
            phone=user.phone,
            purpose=OTP.PURPOSE_REGISTRATION,
            otp=otp
        ).order_by('-created_at').first()
        if not otp_obj or otp_obj.is_expired():
            return render(request, 'verify-otp.html', {'error': 'Invalid or expired OTP', 'debug': settings.DEBUG})
        
        # Verify phone
        user.is_phone_verified = True
        user.save()
        otp_obj.delete()
        
        # Clear session
        del request.session['user_id']
        
        return redirect('login')
    
    return render(request, 'verify-otp.html', {'debug': settings.DEBUG})

def logout_view(request):
    logout(request)
    return render(request, 'logout.html')

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def register(request):
    data = request.data.copy()
    username = (data.get('username') or '').strip()
    phone = (data.get('phone') or '').strip()
    data['username'] = username
    data['phone'] = phone

    # Check if phone exists
    existing_user_by_phone = CustomUser.objects.filter(phone=phone).first()
    if existing_user_by_phone:
        if existing_user_by_phone.username == username:
            if not existing_user_by_phone.is_phone_verified:
                # Resend OTP
                if settings.DEBUG:
                    otp = '123456'
                else:
                    otp = generate_otp_code()
                print(f"OTP for {phone}: {otp}")  # For dev testing
                OTP.objects.create(
                    user=existing_user_by_phone,
                    phone=phone,
                    otp=otp,
                    purpose=OTP.PURPOSE_REGISTRATION
                )
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
        if settings.DEBUG:
            otp = '123456'
        else:
            otp = generate_otp_code()
        print(f"OTP for {user.phone}: {otp}")  # For dev testing
        OTP.objects.create(user=user, phone=user.phone, otp=otp, purpose=OTP.PURPOSE_REGISTRATION)
        return Response({
            'user': serializer.data,
            'otp_sent': True
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        if not user.is_phone_verified:
            return Response({'error': 'Phone number not verified. Please verify your phone first.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if settings.DEBUG:
            otp_code = '123456'
        else:
            otp_code = generate_otp_code()
        session_token = generate_session_token()
        OTP.objects.create(
            user=user,
            phone=user.phone,
            otp=otp_code,
            purpose=OTP.PURPOSE_LOGIN,
            session_token=session_token
        )

        print(f"Login OTP for {user.phone}: {otp_code}")  # For dev/testing only

        return Response({
            'otp_required': True,
            'phone': str(user.phone),
            'session_token': session_token,
            'username': user.username,
            'phone_verified': user.is_phone_verified,
            'message': 'OTP sent to registered phone number'
        }, status=status.HTTP_202_ACCEPTED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_login(request):
    serializer = LoginOTPConfirmSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        otp_obj = serializer.validated_data['otp_obj']

        if not user.is_phone_verified:
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])

        refresh = RefreshToken.for_user(user)
        otp_obj.delete()

        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'phone': str(user.phone),
                'is_phone_verified': user.is_phone_verified,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def verify_otp(request):
    serializer = VerifyOTPSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data.get('user')
        otp_obj = serializer.validated_data.get('otp_obj')
        purpose = request.data.get('purpose', OTP.PURPOSE_REGISTRATION)
        if otp_obj:
            otp_obj.delete()
        if user and not user.is_phone_verified:
            user.is_phone_verified = True
            user.save(update_fields=['is_phone_verified'])
        
        response_data = {'message': 'Phone verified successfully', 'user_id': user.id if user else None}
        
        if purpose == OTP.PURPOSE_REGISTRATION and user:
            refresh = RefreshToken.for_user(user)
            response_data['tokens'] = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            response_data['user'] = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'phone': str(user.phone),
                'is_phone_verified': user.is_phone_verified,
            }
        
        return Response(response_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        return Response(serializer.validated_data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def logout(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'detail': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except TokenError:
        return Response({'detail': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)
    except AttributeError:
        # Token blacklist not enabled; proceed without blacklisting
        pass

    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def bypass_verification(request):
    user = request.user
    user.is_phone_verified = True
    user.save()
    return Response({'message': 'Phone verification bypassed for development'})