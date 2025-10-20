from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import timedelta
from .models import CustomUser, OTP
import random
import string

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=True)  # Make phone mandatory

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'user_type', 'phone')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return {'user': user}
        raise serializers.ValidationError("Invalid credentials")

class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            otp_obj = OTP.objects.filter(
                phone=data['phone'],
                otp=data['otp'],
                is_used=False,
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).first()
            if not otp_obj:
                raise serializers.ValidationError("Invalid or expired OTP")
            otp_obj.is_used = True
            otp_obj.save()
            user = CustomUser.objects.filter(phone=data['phone']).first()
            if user:
                user.is_phone_verified = True
                user.save()
            return {'user': user}
        except:
            raise serializers.ValidationError("Invalid OTP")

class ForgotPasswordSerializer(serializers.Serializer):
    phone = serializers.CharField()

    def validate(self, data):
        user = CustomUser.objects.filter(phone=data['phone']).first()
        if not user:
            raise serializers.ValidationError("User not found")
        # Generate OTP
        otp = '123456'  # Fixed for dev
        print(f"OTP for {data['phone']}: {otp}")  # For dev testing
        OTP.objects.create(phone=data['phone'], otp=otp)
        # Here you would send SMS, but for now, just return
        return {'otp': otp, 'message': 'OTP sent to phone'}